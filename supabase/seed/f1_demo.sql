-- =============================================================================
-- F1 · Datos ficticios para la demo local
-- -----------------------------------------------------------------------------
-- Requisitos:
--   1. La migración 20261102120000_f1_is_platform_admin.sql está aplicada.
--   2. Existen dos usuarios en Supabase Auth (Authentication → Users):
--        demo-pa@example.com
--        demo-coach@example.com
--      Si usas otros correos, cambia las dos variables del bloque.
--   3. Ejecutar como `postgres` desde el SQL Editor del panel.
--
-- No usa datos reales. Es idempotente: se puede ejecutar más de una vez.
-- =============================================================================

begin;

do $$
declare
  v_pa_email    text := 'demo-pa@example.com';
  v_coach_email text := 'demo-coach@example.com';
  v_pa    uuid;
  v_coach uuid;
  v_club  uuid := 'c4000000-0000-4000-8000-00000000000a';
begin
  select id into v_pa
  from auth.users
  where lower(email) = lower(v_pa_email);

  select id into v_coach
  from auth.users
  where lower(email) = lower(v_coach_email);

  if v_pa is null then
    raise exception 'No existe el usuario % en auth.users', v_pa_email;
  end if;
  if v_coach is null then
    raise exception 'No existe el usuario % en auth.users', v_coach_email;
  end if;

  insert into public.profiles (id, display_name)
  values (v_pa, 'Demo Platform Admin'), (v_coach, 'Demo Coach')
  on conflict (id) do nothing;

  insert into public.platform_admins (user_id)
  values (v_pa)
  on conflict (user_id) do nothing;

  insert into public.clubs (id, name, city, country, created_by)
  values (v_club, 'Club Demo Volterra', 'Bogota', 'CO', v_pa)
  on conflict (id) do nothing;

  if not exists (
    select 1
    from public.club_memberships
    where club_id = v_club and user_id = v_pa and ended_at is null
  ) then
    insert into public.club_memberships (club_id, user_id, role, created_by)
    values (v_club, v_pa, 'club_admin', v_pa);
  end if;

  if not exists (
    select 1
    from public.club_memberships
    where club_id = v_club and user_id = v_coach and ended_at is null
  ) then
    insert into public.club_memberships (club_id, user_id, role, created_by)
    values (v_club, v_coach, 'coach', v_pa);
  end if;

  raise notice 'Seed OK: pa=%, coach=%, club=%', v_pa, v_coach, v_club;
end $$;

select
  c.id as club_id,
  c.name,
  c.city,
  (
    select count(*)
    from public.club_memberships m
    where m.club_id = c.id and m.ended_at is null
  ) as active_members
from public.clubs c
where c.id = 'c4000000-0000-4000-8000-00000000000a';

commit;
