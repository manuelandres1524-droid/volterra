
-- =============================================================================
-- F1 · Aislamiento multi-club: helpers, RLS y privilegios
-- Requisitos: A-01, A-03, S-02, S-03, DEC-02.
-- Contexto verificado: los privilegios POR DEFECTO en public conceden
-- arwdDxtm a anon y authenticated. Sin el REVOKE de abajo, toda tabla nueva
-- seria legible y escribible por cualquiera con la clave publica.
-- =============================================================================

-- --- 1. Revocar privilegios heredados del esquema public ----------------------
revoke all on public.clubs            from anon, authenticated;
revoke all on public.profiles         from anon, authenticated;
revoke all on public.platform_admins  from anon, authenticated;
revoke all on public.club_memberships from anon, authenticated;
revoke all on public.audit_events     from anon, authenticated;

do $$ begin
  if exists (select 1 from pg_class where relname = 'audit_events_id_seq') then
    revoke all on sequence public.audit_events_id_seq from anon, authenticated;
  end if;
end $$;

-- --- 2. Esquema privado de helpers (no expuesto por PostgREST) ---------------
create schema if not exists app;
revoke all on schema app from public;
revoke all on schema app from anon;
grant usage on schema app to authenticated;

-- --- 3. Helpers de autorizacion ---------------------------------------------
-- SECURITY DEFINER + search_path vacio: evaluan la pertenencia sin quedar
-- sujetos a las politicas de las propias tablas (evita recursion infinita).

create or replace function app.current_user_id()
returns uuid
language sql stable security definer set search_path = ''
as $$ select auth.uid() $$;

create or replace function app.is_platform_admin()
returns boolean
language sql stable security definer set search_path = ''
as $$
  select exists (
    select 1 from public.platform_admins pa where pa.user_id = auth.uid()
  )
$$;

create or replace function app.is_club_member(p_club_id uuid)
returns boolean
language sql stable security definer set search_path = ''
as $$
  select exists (
    select 1 from public.club_memberships m
    where m.user_id = auth.uid()
      and m.club_id = p_club_id
      and m.ended_at is null
  )
$$;

create or replace function app.has_club_role(p_club_id uuid, p_roles public.club_role[])
returns boolean
language sql stable security definer set search_path = ''
as $$
  select exists (
    select 1 from public.club_memberships m
    where m.user_id = auth.uid()
      and m.club_id = p_club_id
      and m.ended_at is null
      and m.role = any (p_roles)
  )
$$;

-- Un perfil es visible por: su titular, un administrador de plataforma,
-- o el administrador del club del que ambos son miembros activos.
-- Un entrenador NO ve los perfiles de sus companeros (matriz DEC-03:
-- "Gestionar club/usuarios" = entrenador denegado).
create or replace function app.can_view_profile(p_user_id uuid)
returns boolean
language sql stable security definer set search_path = ''
as $$
  select case
    when p_user_id is null then false
    when p_user_id = auth.uid() then true
    when app.is_platform_admin() then true
    else exists (
      select 1
      from public.club_memberships me
      join public.club_memberships peer on peer.club_id = me.club_id
      where me.user_id = auth.uid()
        and me.ended_at is null
        and me.role = 'club_admin'
        and peer.user_id = p_user_id
        and peer.ended_at is null
    )
  end
$$;

revoke all on function app.current_user_id() from public, anon;
revoke all on function app.is_platform_admin() from public, anon;
revoke all on function app.is_club_member(uuid) from public, anon;
revoke all on function app.has_club_role(uuid, public.club_role[]) from public, anon;
revoke all on function app.can_view_profile(uuid) from public, anon;

grant execute on function app.current_user_id() to authenticated;
grant execute on function app.is_platform_admin() to authenticated;
grant execute on function app.is_club_member(uuid) to authenticated;
grant execute on function app.has_club_role(uuid, public.club_role[]) to authenticated;
grant execute on function app.can_view_profile(uuid) to authenticated;

-- --- 4. RLS en todas las tablas expuestas -----------------------------------
alter table public.clubs            enable row level security;
alter table public.profiles         enable row level security;
alter table public.platform_admins  enable row level security;
alter table public.club_memberships enable row level security;
alter table public.audit_events     enable row level security;

alter table public.clubs            force row level security;
alter table public.profiles         force row level security;
alter table public.platform_admins  force row level security;
alter table public.club_memberships force row level security;
alter table public.audit_events     force row level security;

-- --- 5. Politicas: lectura por alcance. Escritura solo por funciones ---------
drop policy if exists clubs_select on public.clubs;
create policy clubs_select on public.clubs
  for select to authenticated
  using (app.is_platform_admin() or app.is_club_member(id));

drop policy if exists profiles_select on public.profiles;
create policy profiles_select on public.profiles
  for select to authenticated
  using (app.can_view_profile(id));

drop policy if exists profiles_insert_self on public.profiles;
create policy profiles_insert_self on public.profiles
  for insert to authenticated
  with check (id = auth.uid());

drop policy if exists profiles_update_self on public.profiles;
create policy profiles_update_self on public.profiles
  for update to authenticated
  using (id = auth.uid())
  with check (id = auth.uid());

drop policy if exists memberships_select on public.club_memberships;
create policy memberships_select on public.club_memberships
  for select to authenticated
  using (
    app.is_platform_admin()
    or user_id = auth.uid()
    or app.has_club_role(club_id, array['club_admin']::public.club_role[])
  );

drop policy if exists audit_select on public.audit_events;
create policy audit_select on public.audit_events
  for select to authenticated
  using (
    app.is_platform_admin()
    or app.has_club_role(club_id, array['club_admin']::public.club_role[])
  );

-- platform_admins: RLS activa y CERO politicas -> nadie la lee por PostgREST.
-- No hay politicas de INSERT/UPDATE/DELETE en ninguna tabla: esas operaciones
-- solo ocurren dentro de funciones SECURITY DEFINER auditadas.

-- --- 6. Privilegios minimos para el rol authenticated -----------------------
grant select on public.clubs            to authenticated;
grant select on public.club_memberships to authenticated;
grant select on public.audit_events     to authenticated;
grant select, insert, update on public.profiles to authenticated;
-- Sin GRANT sobre public.platform_admins: inaccesible por diseno.
