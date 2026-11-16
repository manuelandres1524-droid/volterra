
-- =============================================================================
-- F1 · Endurecimiento tras revision de seguridad independiente
-- Corrige cuatro hallazgos:
--   D1  carrera en la invariante "el club conserva un administrador activo"
--   D2  profiles sin auditoria y con UPDATE/INSERT de tabla completa
--   D3  la auditoria de clubs se guardaba con club_id NULL (invisible al club)
--   D4  un club_admin veia el historial completo de exmiembros
-- Requisitos: A-01, A-02, A-03, S-04, T-01, DEC-02.
-- =============================================================================

-- --- D1: serializar por club antes de evaluar la invariante ------------------
-- Sin bloqueo, dos transacciones concurrentes pueden cerrar a los dos ultimos
-- administradores: cada una ve al otro vigente y ambas confirman. Se bloquea
-- la fila del club, no las pertenencias, para no serializar clubes distintos.
-- En READ COMMITTED la guarda posterior usa una instantanea nueva.

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

  -- D1
  perform 1 from public.clubs c where c.id = v_club for update;

  perform app.assert_can_manage_role(v_club, v_old_role);
  perform app.assert_can_manage_role(v_club, p_new_role);

  if v_old_role = 'club_admin' then
    perform app.assert_club_keeps_admin(v_club, p_membership_id);
  end if;

  update public.club_memberships
     set ended_at = now(), status = 'inactive'
   where id = p_membership_id and ended_at is null;

  if not found then
    raise exception 'La pertenencia cambio durante la operacion'
      using errcode = '40001';
  end if;

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

  -- D1
  perform 1 from public.clubs c where c.id = v_club for update;

  perform app.assert_can_manage_role(v_club, v_role);

  if v_role = 'club_admin' then
    perform app.assert_club_keeps_admin(v_club, p_membership_id);
  end if;

  update public.club_memberships
     set ended_at = now(), status = 'inactive'
   where id = p_membership_id and ended_at is null;

  if not found then
    raise exception 'La pertenencia cambio durante la operacion'
      using errcode = '40001';
  end if;
end $$;

-- --- D2: profiles con privilegios por columna y auditoria --------------------
-- El titular solo puede escribir su nombre visible. No puede reescribir
-- created_at ni updated_at, y todo cambio queda registrado sin copiar el
-- valor anterior (minimizacion: el evento senala que hubo cambio, no el dato).

revoke insert, update on public.profiles from authenticated;
grant insert (id, display_name) on public.profiles to authenticated;
grant update (display_name) on public.profiles to authenticated;

create or replace function app.audit_profile_change()
returns trigger
language plpgsql security definer set search_path = ''
as $$
begin
  insert into public.audit_events
    (actor_user_id, actor_role, club_id, entity, entity_id, action)
  values
    (auth.uid(), null, null, 'profiles',
     coalesce(new.id, old.id)::text, lower(tg_op));
  return null;
end $$;

revoke all on function app.audit_profile_change() from public, anon, authenticated;

drop trigger if exists trg_audit_profiles on public.profiles;
create trigger trg_audit_profiles
  after insert or update or delete on public.profiles
  for each row execute function app.audit_profile_change();

-- --- D3: derivar club_id de la propia fila cuando la tabla es clubs ----------
create or replace function app.audit_row_change()
returns trigger
language plpgsql security definer set search_path = ''
as $$
declare
  v_new jsonb := case when tg_op in ('INSERT','UPDATE') then to_jsonb(new) else null end;
  v_old jsonb := case when tg_op in ('UPDATE','DELETE') then to_jsonb(old) else null end;
  v_club uuid := coalesce(
    (v_new->>'club_id')::uuid,
    (v_old->>'club_id')::uuid,
    case when tg_table_name = 'clubs'
         then coalesce((v_new->>'id')::uuid, (v_old->>'id')::uuid)
    end
  );
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

-- --- D4: el club_admin ve la plantilla vigente, no el historial de exmiembros -
-- El historial completo queda para platform_admin y para el propio titular.
drop policy if exists memberships_select on public.club_memberships;
create policy memberships_select on public.club_memberships
  for select to authenticated
  using (
    app.is_platform_admin()
    or user_id = auth.uid()
    or (
      ended_at is null
      and app.has_club_role(club_id, array['club_admin']::public.club_role[])
    )
  );
