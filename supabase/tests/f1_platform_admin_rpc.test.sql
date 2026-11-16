-- =============================================================================
-- F1 · Prueba de public.fn_is_platform_admin()
-- -----------------------------------------------------------------------------
-- Verifica que la RPC de solo lectura usada por la capa de aplicación:
--   * devuelve true solo al platform_admin;
--   * devuelve false a un miembro de club y a un authenticated sin claims;
--   * no es ejecutable por anon;
--   * mantiene platform_admins cerrada por PostgREST.
--
-- Fixtures FICTICIOS (@example.com). Termina en ROLLBACK: sin residuos.
-- Requiere la migración 20261102120000_f1_is_platform_admin.sql.
-- =============================================================================

begin;

insert into auth.users (id, instance_id, aud, role, email, created_at, updated_at) values
  ('a3000000-0000-4000-8000-000000000001','00000000-0000-0000-0000-000000000000','authenticated','authenticated','rpc-pa@example.com',    now(), now()),
  ('a3000000-0000-4000-8000-000000000002','00000000-0000-0000-0000-000000000000','authenticated','authenticated','rpc-coach@example.com', now(), now());

insert into public.profiles (id, display_name) values
  ('a3000000-0000-4000-8000-000000000001','Persona Ficticia RPC PA'),
  ('a3000000-0000-4000-8000-000000000002','Persona Ficticia RPC Coach');

insert into public.platform_admins (user_id)
values ('a3000000-0000-4000-8000-000000000001');

insert into public.clubs (id, name, created_by) values
  ('c3000000-0000-4000-8000-00000000000a','Club Ficticio RPC','a3000000-0000-4000-8000-000000000001');

insert into public.club_memberships (id, club_id, user_id, role, created_by) values
  ('b3000000-0000-4000-8000-000000000001','c3000000-0000-4000-8000-00000000000a','a3000000-0000-4000-8000-000000000002','coach','a3000000-0000-4000-8000-000000000001');

select set_config('f1rpc.results', '{}', true);

-- -----------------------------------------------------------------------------
-- 1. Estructura: permisos y cierre de la tabla
-- -----------------------------------------------------------------------------
do $$
declare v jsonb := current_setting('f1rpc.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'authenticated_puede_ejecutar',
      has_function_privilege('authenticated','public.fn_is_platform_admin()','execute'),
    'anon_no_puede_ejecutar',
      not has_function_privilege('anon','public.fn_is_platform_admin()','execute'),
    'platform_admins_sigue_cerrada',
      not has_table_privilege('authenticated','public.platform_admins','select')
  );
  perform set_config('f1rpc.results', v::text, true);
end $$;

-- -----------------------------------------------------------------------------
-- 2. Platform admin: true
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a3000000-0000-4000-8000-000000000001","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1rpc.results')::jsonb;
begin
  v := v || jsonb_build_object('pa_es_platform_admin', public.fn_is_platform_admin());
  perform set_config('f1rpc.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 3. Entrenador: false
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a3000000-0000-4000-8000-000000000002","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1rpc.results')::jsonb;
begin
  v := v || jsonb_build_object('coach_no_es_platform_admin', not public.fn_is_platform_admin());
  perform set_config('f1rpc.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 4. Authenticated sin claims: false
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1rpc.results')::jsonb;
begin
  v := v || jsonb_build_object('sin_claims_no_es_platform_admin', not public.fn_is_platform_admin());
  perform set_config('f1rpc.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 5. Anónimo: sin EXECUTE
-- -----------------------------------------------------------------------------
set local role anon;
do $$
declare v jsonb := current_setting('f1rpc.results')::jsonb; v_state text;
begin
  begin
    perform public.fn_is_platform_admin();
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('anon_ejecuta', v_state);
  perform set_config('f1rpc.results', v::text, true);
end $$;
reset role;

select current_setting('f1rpc.results')::jsonb as results;
rollback;

-- =============================================================================
-- Valores esperados (7 comprobaciones)
-- -----------------------------------------------------------------------------
-- authenticated_puede_ejecutar ........ true
-- anon_no_puede_ejecutar .............. true
-- platform_admins_sigue_cerrada ....... true
-- pa_es_platform_admin ................ true
-- coach_no_es_platform_admin .......... true
-- sin_claims_no_es_platform_admin ..... true
-- anon_ejecuta ........................ 42501
-- =============================================================================
