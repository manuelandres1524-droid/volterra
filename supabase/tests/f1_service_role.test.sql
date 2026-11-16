-- =============================================================================
-- F1 · Prueba del rol `service_role` (clave secreta de Supabase)
-- -----------------------------------------------------------------------------
-- Resuelve la hipótesis nº 1 de `decisions/dec-12-material-decision.md`:
-- «llamar a las RPC con service_role hace que auth.uid() sea nulo y las
-- guardas denieguen». Se comprueba, y además se mide el riesgo dominante:
-- que service_role tiene BYPASSRLS y acceso directo a todas las tablas.
--
-- Qué prueba este archivo:
--   S  propiedades estructurales del rol y sus privilegios
--   R  lectura directa SIN identidad de usuario, saltándose RLS
--   W  escritura directa SIN identidad de usuario, saltándose RLS
--   P  las 5 RPC públicas con un JWT de service_role (sin `sub`) → deniegan
--   C  un llamador que puede fijar `request.jwt.claims` suplanta a un usuario
--
-- Qué NO prueba:
--   * que PostgREST fije las claims correctamente (eso es del servidor de API);
--   * concurrencia real (hace falta más de una conexión);
--   * que un cliente pueda falsificar un JWT sin el secreto del proyecto.
--
-- Fixtures FICTICIOS (@example.com). Todo termina en ROLLBACK: sin residuos.
-- Ejecución: enviar el archivo completo como una sola consulta.
-- =============================================================================

begin;

-- Baseline previo: la suite puede ejecutarse sobre una base con datos ficticios
-- (usuarios demo, clubes del E2E). Los conteos absolutos se expresan como delta
-- para seguir siendo comprobables sin vaciar la base ni borrar datos.
select
  set_config('f1svc.base_clubs',           (select count(*)::text from public.clubs), true),
  set_config('f1svc.base_platform_admins', (select count(*)::text from public.platform_admins), true),
  set_config('f1svc.base_profiles',        (select count(*)::text from public.profiles), true);

-- -----------------------------------------------------------------------------
-- 0. Fixtures ficticios: 2 clubes de dueños distintos
-- -----------------------------------------------------------------------------
insert into auth.users (id, instance_id, aud, role, email, created_at, updated_at) values
  ('a2000000-0000-4000-8000-000000000001','00000000-0000-0000-0000-000000000000','authenticated','authenticated','svc-pa@example.com',      now(), now()),
  ('a2000000-0000-4000-8000-000000000002','00000000-0000-0000-0000-000000000000','authenticated','authenticated','svc-adm-alfa@example.com',now(), now()),
  ('a2000000-0000-4000-8000-000000000003','00000000-0000-0000-0000-000000000000','authenticated','authenticated','svc-adm-beta@example.com',now(), now());

insert into public.profiles (id, display_name) values
  ('a2000000-0000-4000-8000-000000000001','Persona Ficticia Svc PA'),
  ('a2000000-0000-4000-8000-000000000002','Persona Ficticia Svc Alfa'),
  ('a2000000-0000-4000-8000-000000000003','Persona Ficticia Svc Beta');

insert into public.platform_admins (user_id) values ('a2000000-0000-4000-8000-000000000001');

insert into public.clubs (id, name, city, created_by) values
  ('c2000000-0000-4000-8000-00000000000a','Club Ficticio Svc Alfa','Bogota','a2000000-0000-4000-8000-000000000001'),
  ('c2000000-0000-4000-8000-00000000000b','Club Ficticio Svc Beta','Cali',  'a2000000-0000-4000-8000-000000000001');

insert into public.club_memberships (id, club_id, user_id, role, created_by) values
  ('b2000000-0000-4000-8000-000000000001','c2000000-0000-4000-8000-00000000000a','a2000000-0000-4000-8000-000000000002','club_admin','a2000000-0000-4000-8000-000000000001'),
  ('b2000000-0000-4000-8000-000000000002','c2000000-0000-4000-8000-00000000000b','a2000000-0000-4000-8000-000000000003','club_admin','a2000000-0000-4000-8000-000000000001');

select set_config('f1svc.results', '{}', true);

-- -----------------------------------------------------------------------------
-- 1. S · propiedades del rol (como postgres)
-- -----------------------------------------------------------------------------
do $$
declare v jsonb := current_setting('f1svc.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'S1_service_role_bypassrls',
      (select rolbypassrls from pg_roles where rolname = 'service_role'),
    'S2_service_role_superusuario',
      (select rolsuper from pg_roles where rolname = 'service_role'),
    'S3_svc_lee_platform_admins',
      has_table_privilege('service_role','public.platform_admins','SELECT'),
    'S4_svc_inserta_platform_admins',
      has_table_privilege('service_role','public.platform_admins','INSERT'),
    'S5_svc_ejecuta_5_rpc',
      -- Se listan las cinco RPC de F1 por nombre: la suite no debe fallar si
      -- se añade una RPC nueva (por ejemplo, fn_is_platform_admin).
      (select count(*)::int from pg_proc p join pg_namespace n on n.oid = p.pronamespace
       where n.nspname = 'public'
         and p.proname in ('fn_create_club','fn_add_member','fn_change_member_role',
                           'fn_end_membership','fn_update_club')
         and has_function_privilege('service_role', p.oid, 'EXECUTE')),
    'S6_authenticated_no_es_miembro_de_svc',
      pg_has_role('authenticated','service_role','MEMBER'),
    'S7_anon_no_es_miembro_de_svc',
      pg_has_role('anon','service_role','MEMBER')
  );
  perform set_config('f1svc.results', v::text, true);
end $$;

-- -----------------------------------------------------------------------------
-- 2. R · lectura directa sin identidad de usuario (claims de service_role)
-- -----------------------------------------------------------------------------
set local role service_role;
select set_config('request.jwt.claims','{"role":"service_role"}',true);

do $$
declare v jsonb := current_setting('f1svc.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'R1_auth_uid_es_nulo', auth.uid() is null,
    'R2_clubes_visibles', (select count(*)::int from public.clubs)
      - current_setting('f1svc.base_clubs')::int,
    'R3_platform_admins_visibles', (select count(*)::int from public.platform_admins)
      - current_setting('f1svc.base_platform_admins')::int,
    'R4_perfiles_visibles', (select count(*)::int from public.profiles)
      - current_setting('f1svc.base_profiles')::int,
    'R5_auditoria_visible', (select count(*)::int from public.audit_events) > 0
  );
  perform set_config('f1svc.results', v::text, true);
end $$;

-- -----------------------------------------------------------------------------
-- 3. W · escritura directa sin identidad, incluido un club ajeno
-- -----------------------------------------------------------------------------
do $$
declare v jsonb := current_setting('f1svc.results')::jsonb; v_state text;
begin
  begin
    insert into public.clubs (name, city, country, created_by)
      values ('Club Ficticio Svc Escritura Directa','Medellin','CO',
              'a2000000-0000-4000-8000-000000000003');
    v_state := 'permitido';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object(
    'W1_insert_directo_club', v_state,
    'W2_clubes_tras_insert', (select count(*)::int from public.clubs)
      - current_setting('f1svc.base_clubs')::int
  );

  begin
    update public.clubs set name = 'Club Ficticio Svc Alfa Renombrado'
      where id = 'c2000000-0000-4000-8000-00000000000a';
    v := v || jsonb_build_object(
      'W3_update_club_ajeno_filas',
        (select count(*)::int from public.clubs where name = 'Club Ficticio Svc Alfa Renombrado')
    );
  exception when others then
    v := v || jsonb_build_object('W3_update_club_ajeno_filas', sqlstate);
  end;

  begin
    update public.platform_admins set user_id = user_id; -- no-op solo para medir privilegio
    v := v || jsonb_build_object('W4_update_platform_admins', 'permitido');
  exception when others then
    v := v || jsonb_build_object('W4_update_platform_admins', sqlstate);
  end;

  perform set_config('f1svc.results', v::text, true);
end $$;

-- -----------------------------------------------------------------------------
-- 4. P · las cinco RPC con JWT de service_role (sin `sub`)
-- -----------------------------------------------------------------------------
do $$
declare v jsonb := current_setting('f1svc.results')::jsonb; v_state text;
begin
  begin
    perform public.fn_create_club('Club Ficticio Svc RPC');
    v_state := 'permitido';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('P1_fn_create_club', v_state);

  begin
    perform public.fn_add_member(
      'c2000000-0000-4000-8000-00000000000a',
      'a2000000-0000-4000-8000-000000000003',
      'coach');
    v_state := 'permitido';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('P2_fn_add_member', v_state);

  begin
    perform public.fn_change_member_role(
      'b2000000-0000-4000-8000-000000000001','coach');
    v_state := 'permitido';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('P3_fn_change_member_role', v_state);

  begin
    perform public.fn_end_membership('b2000000-0000-4000-8000-000000000001');
    v_state := 'permitido';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('P4_fn_end_membership', v_state);

  begin
    perform public.fn_update_club('c2000000-0000-4000-8000-00000000000a','X');
    v_state := 'permitido';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('P5_fn_update_club', v_state);

  -- Contrapeso: nada de lo anterior escribió pese a tener BYPASSRLS, porque
  -- las guardas van antes de tocar las tablas.
  v := v || jsonb_build_object(
    'P6_clubes_tras_rpc', (select count(*)::int from public.clubs)
      - current_setting('f1svc.base_clubs')::int
  );

  perform set_config('f1svc.results', v::text, true);
end $$;

-- -----------------------------------------------------------------------------
-- 5. C · si el llamador puede fijar claims, suplanta a quien quiera
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims',
  '{"sub":"a2000000-0000-4000-8000-000000000001","role":"authenticated"}', true);

do $$
declare v jsonb := current_setting('f1svc.results')::jsonb; v_state text; v_by uuid;
begin
  begin
    perform public.fn_create_club('Club Ficticio Svc Suplantado');
    v_state := 'permitido';
  exception when others then v_state := sqlstate;
  end;

  select c.created_by into v_by
  from public.clubs c where c.name = 'Club Ficticio Svc Suplantado' limit 1;

  v := v || jsonb_build_object(
    'C1_rpc_con_sub_suplantado', v_state,
    'C2_created_by_es_el_suplantado',
      v_by = 'a2000000-0000-4000-8000-000000000001',
    'C3_clubes_totales', (select count(*)::int from public.clubs)
      - current_setting('f1svc.base_clubs')::int
  );
  perform set_config('f1svc.results', v::text, true);
end $$;

reset role;

-- -----------------------------------------------------------------------------
-- 6. Resultado
-- -----------------------------------------------------------------------------
select jsonb_pretty(current_setting('f1svc.results')::jsonb) as results;

rollback;

-- =============================================================================
-- Lectura esperada (base vacía, 2 clubes de fixture):
--   S1_service_role_bypassrls ................... true
--   S2_service_role_superusuario ................ false
--   S3_svc_lee_platform_admins .................. true
--   S4_svc_inserta_platform_admins .............. true
--   S5_svc_ejecuta_5_rpc ........................ 5
--   S6_authenticated_no_es_miembro_de_svc ....... false
--   S7_anon_no_es_miembro_de_svc ................ false
--   R1_auth_uid_es_nulo ......................... true
--   R2_clubes_visibles .......................... 2
--   R3_platform_admins_visibles ................. 1
--   R4_perfiles_visibles ........................ 3
--   R5_auditoria_visible ........................ true
--   W1_insert_directo_club ...................... permitido
--   W2_clubes_tras_insert ....................... 3
--   W3_update_club_ajeno_filas .................. 1
--   W4_update_platform_admins ................... permitido
--   P1_fn_create_club ........................... 28000
--   P2_fn_add_member ............................ 28000
--   P3_fn_change_member_role .................... 28000
--   P4_fn_end_membership ........................ 28000
--   P5_fn_update_club ........................... 28000
--   P6_clubes_tras_rpc .......................... 3
--   C1_rpc_con_sub_suplantado ................... permitido
--   C2_created_by_es_el_suplantado .............. true
--   C3_clubes_totales ........................... 4
--
-- Notas:
--  * R2/R3/R4 = 2/1/3 con `auth.uid()` nulo: RLS no interviene porque
--    service_role tiene BYPASSRLS. Es la prueba del riesgo dominante.
--  * P1..P5 = 28000: las cinco RPC rechazan por «No autenticado» antes de
--    tocar datos. La hipótesis 1 del material de DEC-12 queda confirmada.
--  * C1 = permitido: la autoridad real es `request.jwt.claims`. Quien pueda
--    fijar esa variable (una conexión con la clave service_role) puede actuar
--    como cualquier usuario. No se cierra ningún bloqueo: se documenta.
--  * W4: `update platform_admins ... set user_id = user_id` no cambia filas,
--    pero exige privilegio UPDATE: devuelve «permitido» porque service_role
--    lo tiene. No se modifica ningún dato real (y todo termina en ROLLBACK).
-- =============================================================================
