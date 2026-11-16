
-- =============================================================================
-- F1 · Mutaciones autorizadas y bitacora obligatoria
-- Requisitos: S-02 (autorizacion por objeto), S-04 (sin asignacion masiva),
--             T-01 (bitacora de cambios de permisos), DEC-03 (matriz de roles).
-- Toda escritura pasa por funciones SECURITY DEFINER con guardas explicitas.
-- =============================================================================

-- --- Guardas -----------------------------------------------------------------
create or replace function app.assert_club_keeps_admin(p_club_id uuid, p_excluding_membership uuid)
returns void
language plpgsql stable security definer set search_path = ''
as $$
begin
  if not exists (
    select 1 from public.club_memberships m
    where m.club_id = p_club_id
      and m.ended_at is null
      and m.role = 'club_admin'
      and (p_excluding_membership is null or m.id <> p_excluding_membership)
  ) then
    raise exception 'El club % quedaria sin administrador activo', p_club_id
      using errcode = '23514';
  end if;
end $$;

create or replace function app.membership_role(p_membership_id uuid)
returns public.club_role
language sql stable security definer set search_path = ''
as $$
  select m.role from public.club_memberships m where m.id = p_membership_id
$$;

create or replace function app.membership_club(p_membership_id uuid)
returns uuid
language sql stable security definer set search_path = ''
as $$
  select m.club_id from public.club_memberships m where m.id = p_membership_id
$$;

create or replace function app.membership_is_active(p_membership_id uuid)
returns boolean
language sql stable security definer set search_path = ''
as $$
  select exists (
    select 1 from public.club_memberships m
    where m.id = p_membership_id and m.ended_at is null
  )
$$;

-- Regla unica de quien puede tocar que:
--   platform_admin: cualquier club, cualquier rol
--   club_admin:     su club, y SOLO rol coach
--   nadie mas:      denegado
create or replace function app.assert_can_manage_role(p_club_id uuid, p_target_role public.club_role)
returns void
language plpgsql stable security definer set search_path = ''
as $$
begin
  if auth.uid() is null then
    raise exception 'No autenticado' using errcode = '28000';
  end if;

  if app.is_platform_admin() then
    return;
  end if;

  if not app.has_club_role(p_club_id, array['club_admin']::public.club_role[]) then
    raise exception 'No autorizado: se requiere administrador del club'
      using errcode = '42501';
  end if;

  if p_target_role <> 'coach' then
    raise exception 'Un administrador de club solo puede gestionar entrenadores'
      using errcode = '42501';
  end if;
end $$;

-- --- Utilidades --------------------------------------------------------------
create or replace function app.touch_updated_at()
returns trigger language plpgsql set search_path = ''
as $$
begin
  new.updated_at := now();
  return new;
end $$;

-- --- Funciones publicas (RPC) ------------------------------------------------
create or replace function public.fn_create_club(
  p_name text,
  p_city text default null,
  p_country char(2) default 'CO'
) returns uuid
language plpgsql security definer set search_path = ''
as $$
declare v_id uuid; v_uid uuid := auth.uid();
begin
  if v_uid is null then
    raise exception 'No autenticado' using errcode = '28000';
  end if;
  if not app.is_platform_admin() then
    raise exception 'No autorizado: se requiere administrador de plataforma'
      using errcode = '42501';
  end if;

  insert into public.clubs (name, city, country, created_by)
  values (btrim(p_name), nullif(btrim(p_city), ''), p_country, v_uid)
  returning id into v_id;

  return v_id;
end $$;

create or replace function public.fn_add_member(
  p_club_id uuid,
  p_user_id uuid,
  p_role public.club_role
) returns uuid
language plpgsql security definer set search_path = ''
as $$
declare v_id uuid; v_uid uuid := auth.uid();
begin
  if v_uid is null then
    raise exception 'No autenticado' using errcode = '28000';
  end if;

  perform app.assert_can_manage_role(p_club_id, p_role);

  if not exists (select 1 from auth.users u where u.id = p_user_id) then
    raise exception 'El usuario % no existe', p_user_id using errcode = '23503';
  end if;

  if exists (
    select 1 from public.club_memberships m
    where m.club_id = p_club_id and m.user_id = p_user_id and m.ended_at is null
  ) then
    raise exception 'El usuario ya tiene una pertenencia vigente en este club'
      using errcode = '23505';
  end if;

  insert into public.club_memberships (club_id, user_id, role, created_by)
  values (p_club_id, p_user_id, p_role, v_uid)
  returning id into v_id;

  return v_id;
end $$;

create or replace function public.fn_change_member_role(
  p_membership_id uuid,
  p_new_role public.club_role
) returns uuid
language plpgsql security definer set search_path = ''
as $$
declare
  v_uid uuid := auth.uid();
  v_club uuid;
  v_user uuid;
  v_old_role public.club_role;
  v_new_id uuid;
begin
  if v_uid is null then
    raise exception 'No autenticado' using errcode = '28000';
  end if;

  select m.club_id, m.user_id, m.role into v_club, v_user, v_old_role
  from public.club_memberships m
  where m.id = p_membership_id and m.ended_at is null;

  if v_club is null then
    raise exception 'Pertenencia inexistente o ya cerrada' using errcode = 'P0002';
  end if;
  if v_old_role = p_new_role then
    raise exception 'El rol ya es %', p_new_role using errcode = '22023';
  end if;

  -- Quien no puede tocar el rol actual, tampoco puede cambiarlo.
  perform app.assert_can_manage_role(v_club, v_old_role);
  perform app.assert_can_manage_role(v_club, p_new_role);

  if v_old_role = 'club_admin' then
    perform app.assert_club_keeps_admin(v_club, p_membership_id);
  end if;

  -- Historial: se cierra la fila y se abre otra. Nunca se sobrescribe.
  update public.club_memberships
     set ended_at = now(), status = 'inactive'
   where id = p_membership_id;

  insert into public.club_memberships (club_id, user_id, role, created_by)
  values (v_club, v_user, p_new_role, v_uid)
  returning id into v_new_id;

  return v_new_id;
end $$;

create or replace function public.fn_end_membership(p_membership_id uuid)
returns void
language plpgsql security definer set search_path = ''
as $$
declare v_club uuid; v_role public.club_role;
begin
  if auth.uid() is null then
    raise exception 'No autenticado' using errcode = '28000';
  end if;

  select m.club_id, m.role into v_club, v_role
  from public.club_memberships m
  where m.id = p_membership_id and m.ended_at is null;

  if v_club is null then
    raise exception 'Pertenencia inexistente o ya cerrada' using errcode = 'P0002';
  end if;

  perform app.assert_can_manage_role(v_club, v_role);

  if v_role = 'club_admin' then
    perform app.assert_club_keeps_admin(v_club, p_membership_id);
  end if;

  update public.club_memberships
     set ended_at = now(), status = 'inactive'
   where id = p_membership_id;
end $$;

revoke all on function public.fn_create_club(text, text, char) from public, anon;
revoke all on function public.fn_add_member(uuid, uuid, public.club_role) from public, anon;
revoke all on function public.fn_change_member_role(uuid, public.club_role) from public, anon;
revoke all on function public.fn_end_membership(uuid) from public, anon;

grant execute on function public.fn_create_club(text, text, char) to authenticated;
grant execute on function public.fn_add_member(uuid, uuid, public.club_role) to authenticated;
grant execute on function public.fn_change_member_role(uuid, public.club_role) to authenticated;
grant execute on function public.fn_end_membership(uuid) to authenticated;

-- --- Bitacora obligatoria ----------------------------------------------------
create or replace function app.audit_row_change()
returns trigger
language plpgsql security definer set search_path = ''
as $$
declare
  v_new jsonb := case when tg_op in ('INSERT', 'UPDATE') then to_jsonb(new) else null end;
  v_old jsonb := case when tg_op in ('UPDATE', 'DELETE') then to_jsonb(old) else null end;
  v_club uuid := coalesce((v_new->>'club_id')::uuid, (v_old->>'club_id')::uuid);
  v_entity_id text := coalesce(v_new->>'id', v_old->>'id', v_new->>'user_id', v_old->>'user_id');
  v_role text;
begin
  if app.is_platform_admin() then
    v_role := 'platform_admin';
  else
    select m.role::text into v_role
    from public.club_memberships m
    where m.user_id = auth.uid()
      and m.ended_at is null
      and (v_club is null or m.club_id = v_club)
    limit 1;
  end if;

  insert into public.audit_events
    (actor_user_id, actor_role, club_id, entity, entity_id, action, before_data, after_data)
  values
    (auth.uid(), v_role, v_club, tg_table_name, v_entity_id, lower(tg_op), v_old, v_new);

  return null;
end $$;

create or replace function app.block_audit_mutation()
returns trigger language plpgsql set search_path = ''
as $$
begin
  raise exception 'audit_events es append-only' using errcode = '42501';
end $$;

drop trigger if exists trg_audit_clubs on public.clubs;
create trigger trg_audit_clubs after insert or update or delete on public.clubs
  for each row execute function app.audit_row_change();

drop trigger if exists trg_audit_memberships on public.club_memberships;
create trigger trg_audit_memberships after insert or update or delete on public.club_memberships
  for each row execute function app.audit_row_change();

drop trigger if exists trg_audit_platform_admins on public.platform_admins;
create trigger trg_audit_platform_admins after insert or update or delete on public.platform_admins
  for each row execute function app.audit_row_change();

drop trigger if exists trg_profiles_touch on public.profiles;
create trigger trg_profiles_touch before update on public.profiles
  for each row execute function app.touch_updated_at();

drop trigger if exists trg_audit_append_only on public.audit_events;
create trigger trg_audit_append_only before update or delete on public.audit_events
  for each row execute function app.block_audit_mutation();

drop trigger if exists trg_audit_no_truncate on public.audit_events;
create trigger trg_audit_no_truncate before truncate on public.audit_events
  for each statement execute function app.block_audit_mutation();

revoke all on function app.audit_row_change() from public, anon, authenticated;
revoke all on function app.block_audit_mutation() from public, anon, authenticated;
