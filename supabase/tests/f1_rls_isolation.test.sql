-- =============================================================================
-- F1 · Pruebas de aislamiento, permisos y trazabilidad
-- -----------------------------------------------------------------------------
-- Qué hace: crea fixtures FICTICIOS (RFC 2606, @example.com), impersona a cada
-- rol mediante `set local role` + `request.jwt.claims` (mecanismo que usa
-- auth.uid()), ejecuta las comprobaciones y termina en ROLLBACK.
--
-- Garantías:
--   * No deja datos, usuarios ni eventos de auditoría en la base.
--   * No usa datos reales ni datos de menores.
--   * Cada negativa se captura con SQLSTATE; la suite no aborta.
--
-- Ejecución: enviar el archivo completo como una sola consulta. Devuelve una
-- fila con el objeto `results`. Los valores esperados están anotados al final.
-- =============================================================================

begin;

-- Baseline previo: la suite puede ejecutarse sobre una base con datos ficticios
-- (usuarios demo, clubes del E2E). Los conteos absolutos se expresan como delta
-- para seguir siendo comprobables sin vaciar la base ni borrar datos.
select
  set_config('f1.base_clubs',       (select count(*)::text from public.clubs), true),
  set_config('f1.base_memberships', (select count(*)::text from public.club_memberships), true),
  set_config('f1.base_profiles',    (select count(*)::text from public.profiles), true);

-- -----------------------------------------------------------------------------
-- 0. Fixtures ficticios
-- -----------------------------------------------------------------------------
insert into auth.users (id, instance_id, aud, role, email, created_at, updated_at) values
  ('a0000000-0000-4000-8000-000000000001','00000000-0000-0000-0000-000000000000','authenticated','authenticated','pa@example.com',       now(), now()),
  ('a0000000-0000-4000-8000-000000000002','00000000-0000-0000-0000-000000000000','authenticated','authenticated','adm-a@example.com',    now(), now()),
  ('a0000000-0000-4000-8000-000000000003','00000000-0000-0000-0000-000000000000','authenticated','authenticated','coach-a@example.com',  now(), now()),
  ('a0000000-0000-4000-8000-000000000004','00000000-0000-0000-0000-000000000000','authenticated','authenticated','adm-b@example.com',    now(), now()),
  ('a0000000-0000-4000-8000-000000000005','00000000-0000-0000-0000-000000000000','authenticated','authenticated','outsider@example.com', now(), now()),
  ('a0000000-0000-4000-8000-000000000006','00000000-0000-0000-0000-000000000000','authenticated','authenticated','nuevo-1@example.com',  now(), now()),
  ('a0000000-0000-4000-8000-000000000007','00000000-0000-0000-0000-000000000000','authenticated','authenticated','nuevo-2@example.com',  now(), now());

insert into public.profiles (id, display_name) values
  ('a0000000-0000-4000-8000-000000000001','Persona Ficticia PA'),
  ('a0000000-0000-4000-8000-000000000002','Persona Ficticia Adm A'),
  ('a0000000-0000-4000-8000-000000000003','Persona Ficticia Coach A'),
  ('a0000000-0000-4000-8000-000000000004','Persona Ficticia Adm B'),
  ('a0000000-0000-4000-8000-000000000005','Persona Ficticia Externa'),
  ('a0000000-0000-4000-8000-000000000006','Persona Ficticia Nueva 1'),
  ('a0000000-0000-4000-8000-000000000007','Persona Ficticia Nueva 2');

insert into public.platform_admins (user_id, granted_by)
values ('a0000000-0000-4000-8000-000000000001', null);

insert into public.clubs (id, name, city, created_by) values
  ('c0000000-0000-4000-8000-00000000000a','Club Ficticio Alfa','Bogota',  'a0000000-0000-4000-8000-000000000001'),
  ('c0000000-0000-4000-8000-00000000000b','Club Ficticio Beta','Medellin','a0000000-0000-4000-8000-000000000001');

insert into public.club_memberships (id, club_id, user_id, role, created_by) values
  ('b0000000-0000-4000-8000-000000000001','c0000000-0000-4000-8000-00000000000a','a0000000-0000-4000-8000-000000000002','club_admin','a0000000-0000-4000-8000-000000000001'),
  ('b0000000-0000-4000-8000-000000000002','c0000000-0000-4000-8000-00000000000a','a0000000-0000-4000-8000-000000000003','coach',     'a0000000-0000-4000-8000-000000000001'),
  ('b0000000-0000-4000-8000-000000000003','c0000000-0000-4000-8000-00000000000b','a0000000-0000-4000-8000-000000000004','club_admin','a0000000-0000-4000-8000-000000000001');

-- -----------------------------------------------------------------------------
-- 1. Comprobaciones estructurales (sin impersonar)
-- -----------------------------------------------------------------------------
do $$
declare v jsonb := '{}'; v_tables text[] := array['clubs','profiles','platform_admins','club_memberships','audit_events'];
begin
  v := v || jsonb_build_object(
    'rls_enabled_all', (
      select bool_and(c.relrowsecurity)
      from pg_class c join pg_namespace n on n.oid = c.relnamespace
      where n.nspname = 'public' and c.relname = any (v_tables)
    ),
    'rls_forced_all', (
      select bool_and(c.relforcerowsecurity)
      from pg_class c join pg_namespace n on n.oid = c.relnamespace
      where n.nspname = 'public' and c.relname = any (v_tables)
    ),
    'anon_sin_privilegios', not exists (
      select 1 from unnest(v_tables) t(name)
      where has_table_privilege('anon', 'public.' || t.name, 'select')
         or has_table_privilege('anon', 'public.' || t.name, 'insert')
         or has_table_privilege('anon', 'public.' || t.name, 'update')
         or has_table_privilege('anon', 'public.' || t.name, 'delete')
    ),
    'authenticated_sin_escritura_directa',
      not has_table_privilege('authenticated','public.clubs','insert')
      and not has_table_privilege('authenticated','public.clubs','update')
      and not has_table_privilege('authenticated','public.clubs','delete')
      and not has_table_privilege('authenticated','public.club_memberships','insert')
      and not has_table_privilege('authenticated','public.club_memberships','update')
      and not has_table_privilege('authenticated','public.club_memberships','delete')
      and not has_table_privilege('authenticated','public.audit_events','insert')
      and not has_table_privilege('authenticated','public.audit_events','update')
      and not has_table_privilege('authenticated','public.audit_events','delete'),
    'authenticated_puede_leer_clubes', has_table_privilege('authenticated','public.clubs','select'),
    'platform_admins_sin_privilegios', not has_table_privilege('authenticated','public.platform_admins','select'),
    'roles_enum', (
      select array_agg(e.enumlabel order by e.enumsortorder)::text
      from pg_enum e join pg_type t on t.oid = e.enumtypid
      where t.typname = 'club_role' and t.typnamespace = 'public'::regnamespace
    ),
    'indice_una_pertenencia_vigente', (
      select count(*)::int from pg_indexes
      where schemaname = 'public' and tablename = 'club_memberships'
        and indexname = 'club_memberships_one_current'
    )
  );
  perform set_config('f1.results', v::text, true);
end $$;

-- -----------------------------------------------------------------------------
-- 1b. Privilegios de funciones y privilegios por defecto
-- -----------------------------------------------------------------------------
do $$
declare v jsonb := current_setting('f1.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'anon_sin_funciones', not exists (
      select 1 from pg_proc p join pg_namespace n on n.oid = p.pronamespace
      where n.nspname in ('public','app') and has_function_privilege('anon', p.oid, 'execute')
    ),
    'helpers_app_expuestos_a_authenticated', (
      select jsonb_agg(p.proname order by p.proname)
      from pg_proc p join pg_namespace n on n.oid = p.pronamespace
      where n.nspname = 'app' and has_function_privilege('authenticated', p.oid, 'execute')
    ),
    'helper_interno_cerrado', not has_function_privilege('authenticated','app.membership_role(uuid)','execute'),
    'rpc_disponible_authenticated', has_function_privilege('authenticated','public.fn_create_club(text,text,char)','execute'),
    'defacl_postgres_denegado', not exists (
      select 1 from pg_default_acl d, aclexplode(d.defaclacl) x
      where d.defaclrole = 'postgres'::regrole
        and d.defaclnamespace in ('public'::regnamespace, 'app'::regnamespace)
        and x.grantee::regrole::text in ('anon','authenticated')
    ),
    'defacl_supabase_admin_expuesto', exists (
      select 1 from pg_default_acl d, aclexplode(d.defaclacl) x
      where d.defaclrole = 'supabase_admin'::regrole
        and d.defaclnamespace = 'public'::regnamespace
        and x.grantee::regrole::text in ('anon','authenticated')
    )
  );
  perform set_config('f1.results', v::text, true);
end $$;

-- -----------------------------------------------------------------------------
-- 2. Lectura: cada actor solo ve su ámbito
-- -----------------------------------------------------------------------------
-- Coach del club Alfa: 1 club, 1 pertenencia, 1 perfil (el suyo), 0 auditoría.
select set_config('request.jwt.claims','{"sub":"a0000000-0000-4000-8000-000000000003","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'coachA_clubes',        (select count(*)::int from public.clubs),
    'coachA_solo_club_alfa',(select bool_and(id = 'c0000000-0000-4000-8000-00000000000a') from public.clubs),
    'coachA_pertenencias',  (select count(*)::int from public.club_memberships),
    'coachA_perfiles',      (select count(*)::int from public.profiles),
    'coachA_auditoria',     (select count(*)::int from public.audit_events)
  );
  perform set_config('f1.results', v::text, true);
end $$;
reset role;

-- Admin del club Alfa: 1 club, 2 pertenencias, 2 perfiles, auditoría solo de Alfa.
select set_config('request.jwt.claims','{"sub":"a0000000-0000-4000-8000-000000000002","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'admA_clubes',            (select count(*)::int from public.clubs),
    'admA_pertenencias',      (select count(*)::int from public.club_memberships),
    'admA_perfiles',          (select count(*)::int from public.profiles),
    'admA_auditoria_ajena',   (select count(*)::int from public.audit_events where club_id = 'c0000000-0000-4000-8000-00000000000b'),
    'admA_auditoria_propia_mayor_que_cero', (select count(*) > 0 from public.audit_events)
  );
  perform set_config('f1.results', v::text, true);
end $$;
reset role;

-- Admin de plataforma: 2 clubs, 3 pertenencias, 7 perfiles (delta sobre el
-- baseline, no conteo absoluto).
select set_config('request.jwt.claims','{"sub":"a0000000-0000-4000-8000-000000000001","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'pa_clubes',       (select count(*)::int from public.clubs)
                       - current_setting('f1.base_clubs')::int,
    'pa_pertenencias', (select count(*)::int from public.club_memberships)
                       - current_setting('f1.base_memberships')::int,
    'pa_perfiles',     (select count(*)::int from public.profiles)
                       - current_setting('f1.base_profiles')::int
  );
  perform set_config('f1.results', v::text, true);
end $$;
reset role;

-- Usuario sin club: no ve ningún club ni pertenencia ajena; solo su perfil.
select set_config('request.jwt.claims','{"sub":"a0000000-0000-4000-8000-000000000005","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'externo_clubes',       (select count(*)::int from public.clubs),
    'externo_pertenencias', (select count(*)::int from public.club_memberships),
    'externo_perfiles',     (select count(*)::int from public.profiles)
  );
  perform set_config('f1.results', v::text, true);
end $$;
reset role;

-- platform_admins no es accesible ni siquiera para el admin de plataforma por API.
select set_config('request.jwt.claims','{"sub":"a0000000-0000-4000-8000-000000000001","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1.results')::jsonb; v_state text;
begin
  begin
    perform count(*) from public.platform_admins;
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('pa_lee_platform_admins', v_state);
  perform set_config('f1.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 3. Anónimo: sin acceso a tablas ni a funciones
-- -----------------------------------------------------------------------------
set local role anon;
do $$
declare v jsonb := current_setting('f1.results')::jsonb; v_state text;
begin
  begin
    perform count(*) from public.clubs;
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('anon_lee_clubes', v_state);

  begin
    perform public.fn_create_club('Club Fantasma');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('anon_ejecuta_rpc', v_state);

  perform set_config('f1.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 4. Escritura de club_admin Alfa
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a0000000-0000-4000-8000-000000000002","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1.results')::jsonb; v_state text; v_id uuid;
begin
  -- W1: alta de entrenador en su propio club -> permitido
  begin
    v_id := public.fn_add_member(
      'c0000000-0000-4000-8000-00000000000a',
      'a0000000-0000-4000-8000-000000000006',
      'coach');
    v := v || jsonb_build_object('W1_alta_entrenador', 'ok');
    perform set_config('f1.m_new', v_id::text, true);
  exception when others then
    v := v || jsonb_build_object('W1_alta_entrenador', sqlstate);
  end;

  -- W2: intento de crear otro administrador -> denegado
  begin
    perform public.fn_add_member(
      'c0000000-0000-4000-8000-00000000000a',
      'a0000000-0000-4000-8000-000000000005',
      'club_admin');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('W2_alta_admin_por_club_admin', v_state);

  -- W3: intento de escribir en otro club -> denegado
  begin
    perform public.fn_add_member(
      'c0000000-0000-4000-8000-00000000000b',
      'a0000000-0000-4000-8000-000000000007',
      'coach');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('W3_alta_en_club_ajeno', v_state);

  -- W4: inserción directa en tabla (sin RPC) -> denegada por privilegios
  begin
    insert into public.club_memberships (club_id, user_id, role, created_by)
    values ('c0000000-0000-4000-8000-00000000000a',
            'a0000000-0000-4000-8000-000000000007',
            'coach',
            'a0000000-0000-4000-8000-000000000002');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('W4_insercion_directa', v_state);

  -- W5: cerrar su propia pertenencia de administrador -> denegado por rol
  -- (un club_admin solo gestiona entrenadores; la guarda de "ultimo admin"
  --  se ejerce despues y se verifica en W11 con platform_admin).
  begin
    perform public.fn_end_membership('b0000000-0000-4000-8000-000000000001');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('W5_cerrar_ultimo_admin', v_state);

  -- W6: borrado directo de auditoría -> denegado
  begin
    delete from public.audit_events where true;
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('W6_borrado_auditoria', v_state);

  perform set_config('f1.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 5. Escritura de un entrenador: sin gestión de usuarios
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a0000000-0000-4000-8000-000000000003","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1.results')::jsonb; v_state text;
begin
  begin
    perform public.fn_add_member(
      'c0000000-0000-4000-8000-00000000000a',
      'a0000000-0000-4000-8000-000000000007',
      'coach');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('W7_alta_por_entrenador', v_state);
  perform set_config('f1.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 6. Admin de plataforma: crear clubes, designar admins y conservar historial
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a0000000-0000-4000-8000-000000000001","role":"authenticated"}', true);
set local role authenticated;
do $$
declare
  v jsonb := current_setting('f1.results')::jsonb;
  v_state text;
  v_club uuid;
  v_new_membership uuid;
begin
  -- W8: validación de nombre (2 caracteres) -> rechazado por CHECK
  begin
    perform public.fn_create_club('X');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('W8_nombre_invalido', v_state);

  -- W9: club válido -> creado, con created_by = admin de plataforma
  begin
    v_club := public.fn_create_club('Club Ficticio Gamma', 'Cali', 'CO');
    v := v || jsonb_build_object(
      'W9_crear_club', 'ok',
      'W9_created_by_correcto',
      (select created_by = 'a0000000-0000-4000-8000-000000000001' from public.clubs where id = v_club));
    perform set_config('f1.club_gamma', v_club::text, true);
  exception when others then
    v := v || jsonb_build_object('W9_crear_club', sqlstate);
  end;

  -- W10: designar administrador de club en el club nuevo
  begin
    perform public.fn_add_member(
      current_setting('f1.club_gamma')::uuid,
      'a0000000-0000-4000-8000-000000000005',
      'club_admin');
    v := v || jsonb_build_object('W10_designar_admin_club', 'ok');
  exception when others then
    v := v || jsonb_build_object('W10_designar_admin_club', sqlstate);
  end;

  -- W11: cerrar al único admin del club Beta -> denegado
  begin
    perform public.fn_end_membership('b0000000-0000-4000-8000-000000000003');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('W11_cerrar_ultimo_admin_beta', v_state);

  -- W12: degradar al único admin de Alfa antes de crear otro -> denegado
  begin
    perform public.fn_change_member_role('b0000000-0000-4000-8000-000000000001','coach');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('W12_degradar_unico_admin_alfa', v_state);

  -- W13: promover al entrenador nuevo a administrador -> permitido
  begin
    v_new_membership := public.fn_change_member_role(current_setting('f1.m_new')::uuid,'club_admin');
    v := v || jsonb_build_object('W13_promover_a_admin', 'ok');
    perform set_config('f1.m_promoted', v_new_membership::text, true);
  exception when others then
    v := v || jsonb_build_object('W13_promover_a_admin', sqlstate);
  end;

  -- W14: ahora sí se puede degradar al admin anterior (queda otro admin)
  begin
    perform public.fn_change_member_role('b0000000-0000-4000-8000-000000000001','coach');
    v := v || jsonb_build_object('W14_degradar_con_reemplazo', 'ok');
  exception when others then
    v := v || jsonb_build_object('W14_degradar_con_reemplazo', sqlstate);
  end;

  -- W15: el historial conserva la fila cerrada
  v := v || jsonb_build_object(
    'W15_filas_historial_admin_alfa',
    (select count(*)::int from public.club_memberships
      where club_id = 'c0000000-0000-4000-8000-00000000000a'
        and user_id = 'a0000000-0000-4000-8000-000000000002'),
    'W15_filas_cerradas',
    (select count(*)::int from public.club_memberships
      where club_id = 'c0000000-0000-4000-8000-00000000000a'
        and user_id = 'a0000000-0000-4000-8000-000000000002'
        and ended_at is not null and status = 'inactive')
  );

  -- W16: la promoción quedó auditada con actor y rol correctos
  v := v || jsonb_build_object(
    'W16_auditoria_actor_correcto',
    exists (
      select 1 from public.audit_events a
      where a.entity = 'club_memberships'
        and a.action = 'insert'
        and a.actor_user_id = 'a0000000-0000-4000-8000-000000000002'
        and a.actor_role = 'club_admin'
        and a.club_id = 'c0000000-0000-4000-8000-00000000000a'
    )
  );

  perform set_config('f1.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 7. Perfiles: propio sí, ajeno no
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a0000000-0000-4000-8000-000000000006","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1.results')::jsonb; v_state text; v_rows int;
begin
  update public.profiles set display_name = 'Persona Ficticia Coach A'
   where id = 'a0000000-0000-4000-8000-000000000003';
  get diagnostics v_rows = row_count;
  v := v || jsonb_build_object('W17_actualizar_perfil_ajeno_filas', v_rows);

  update public.profiles set display_name = 'Persona Ficticia Nueva 1 (editada)'
   where id = 'a0000000-0000-4000-8000-000000000006';
  get diagnostics v_rows = row_count;
  v := v || jsonb_build_object('W18_actualizar_perfil_propio_filas', v_rows);

  begin
    insert into public.profiles (id, display_name)
    values ('a0000000-0000-4000-8000-000000000007','Perfil Ajeno');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('W19_insertar_perfil_ajeno', v_state);

  perform set_config('f1.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 8. Auditoría append-only incluso para el propietario de la tabla
-- -----------------------------------------------------------------------------
do $$
declare v jsonb := current_setting('f1.results')::jsonb; v_state text;
begin
  begin
    update public.audit_events set action = 'manipulado' where true;
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('W20_alterar_auditoria', v_state);

  begin
    truncate public.audit_events;
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('W21_truncar_auditoria', v_state);

  perform set_config('f1.results', v::text, true);
end $$;

-- -----------------------------------------------------------------------------
-- 10. Perfil de club: solo el administrador de plataforma lo edita
-- -----------------------------------------------------------------------------
insert into auth.users (id, instance_id, aud, role, email, created_at, updated_at) values
  ('a0000000-0000-4000-8000-000000000008','00000000-0000-0000-0000-000000000000','authenticated','authenticated','adm-d@example.com',   now(), now()),
  ('a0000000-0000-4000-8000-000000000009','00000000-0000-0000-0000-000000000000','authenticated','authenticated','coach-d@example.com', now(), now());

insert into public.clubs (id, name, city, created_by) values
  ('c0000000-0000-4000-8000-00000000000c','Club Ficticio Delta','Cali','a0000000-0000-4000-8000-000000000001');

insert into public.club_memberships (club_id, user_id, role, created_by) values
  ('c0000000-0000-4000-8000-00000000000c','a0000000-0000-4000-8000-000000000008','club_admin','a0000000-0000-4000-8000-000000000001'),
  ('c0000000-0000-4000-8000-00000000000c','a0000000-0000-4000-8000-000000000009','coach',     'a0000000-0000-4000-8000-000000000001');

select set_config('request.jwt.claims','{"sub":"a0000000-0000-4000-8000-000000000008","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1.results')::jsonb; v_state text;
begin
  begin
    perform public.fn_update_club('c0000000-0000-4000-8000-00000000000c', 'Renombrado por club_admin');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('U1_club_admin_edita', v_state);
  perform set_config('f1.results', v::text, true);
end $$;
reset role;

select set_config('request.jwt.claims','{"sub":"a0000000-0000-4000-8000-000000000009","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1.results')::jsonb; v_state text;
begin
  begin
    perform public.fn_update_club('c0000000-0000-4000-8000-00000000000c', 'Renombrado por coach');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('U2_coach_edita', v_state);
  perform set_config('f1.results', v::text, true);
end $$;
reset role;

set local role anon;
do $$
declare v jsonb := current_setting('f1.results')::jsonb; v_state text;
begin
  begin
    perform public.fn_update_club('c0000000-0000-4000-8000-00000000000c', 'Renombrado por anon');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('U3_anon_edita', v_state);
  perform set_config('f1.results', v::text, true);
end $$;
reset role;

select set_config('request.jwt.claims','{"sub":"a0000000-0000-4000-8000-000000000001","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1.results')::jsonb; v_state text;
begin
  begin
    perform public.fn_update_club('c0000000-0000-4000-8000-00000000000c', 'Club Ficticio Delta Renombrado', 'Medellin');
    v := v || jsonb_build_object('U4_pa_edita', 'ok');
  exception when others then
    v := v || jsonb_build_object('U4_pa_edita', sqlstate);
  end;

  begin
    perform public.fn_update_club('c0000000-0000-4000-8000-00000000000c', '');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('U5_nombre_vacio', v_state);

  begin
    perform public.fn_update_club('ffffffff-ffff-4fff-8fff-ffffffffffff', 'Fantasma');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('U6_club_inexistente', v_state);

  v := v || jsonb_build_object(
    'U7_nombre_actualizado',
    (select name from public.clubs where id = 'c0000000-0000-4000-8000-00000000000c'),
    'U8_ciudad_actualizada',
    (select city from public.clubs where id = 'c0000000-0000-4000-8000-00000000000c'),
    'U9_auditoria_update',
    exists (
      select 1 from public.audit_events a
      where a.entity = 'clubs' and a.action = 'update'
        and a.actor_user_id = 'a0000000-0000-4000-8000-000000000001'
        and a.actor_role = 'platform_admin'
        and a.before_data->>'name' = 'Club Ficticio Delta'
        and a.after_data->>'name' = 'Club Ficticio Delta Renombrado'
    )
  );

  perform set_config('f1.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 11. Resultado
-- -----------------------------------------------------------------------------
select jsonb_pretty(current_setting('f1.results')::jsonb) as results;

rollback;

-- =============================================================================
-- Valores esperados (25/10/2026)
-- -----------------------------------------------------------------------------
-- rls_enabled_all ............................. true
-- rls_forced_all .............................. true
-- anon_sin_privilegios ........................ true
-- authenticated_sin_escritura_directa ......... true
-- authenticated_puede_leer_clubes ............. true
-- platform_admins_sin_privilegios ............. true
-- roles_enum .................................. {club_admin,coach}
-- indice_una_pertenencia_vigente .............. 1
-- anon_sin_funciones .......................... true
-- helpers_app_expuestos_a_authenticated ....... ["can_view_profile","current_user_id","has_club_role","is_club_member","is_platform_admin"]
-- helper_interno_cerrado ...................... true
-- rpc_disponible_authenticated ................ true
-- defacl_postgres_denegado .................... true
-- defacl_supabase_admin_expuesto .............. true  (riesgo residual documentado)
-- coachA_clubes ............................... 1
-- coachA_solo_club_alfa ....................... true
-- coachA_pertenencias ......................... 1
-- coachA_perfiles ............................. 1
-- coachA_auditoria ............................ 0
-- admA_clubes ................................. 1
-- admA_pertenencias ........................... 2
-- admA_perfiles ............................... 2
-- admA_auditoria_ajena ........................ 0
-- admA_auditoria_propia_mayor_que_cero ........ true
-- pa_clubes ................................... 2
-- pa_pertenencias ............................. 3
-- pa_perfiles ................................. 7
-- externo_clubes .............................. 0
-- externo_pertenencias ........................ 0
-- externo_perfiles ............................ 1
-- pa_lee_platform_admins ...................... 42501
-- anon_lee_clubes ............................. 42501
-- anon_ejecuta_rpc ............................ 42501
-- W1_alta_entrenador .......................... ok
-- W2_alta_admin_por_club_admin ................ 42501
-- W3_alta_en_club_ajeno ....................... 42501
-- W4_insercion_directa ........................ 42501
-- W5_cerrar_ultimo_admin ...................... 42501
-- W6_borrado_auditoria ........................ 42501
-- W7_alta_por_entrenador ...................... 42501
-- W8_nombre_invalido .......................... 23514
-- W9_crear_club ............................... ok
-- W9_created_by_correcto ...................... true
-- W10_designar_admin_club ..................... ok
-- W11_cerrar_ultimo_admin_beta ................ 23514
-- W12_degradar_unico_admin_alfa ............... 23514
-- W13_promover_a_admin ........................ ok
-- W14_degradar_con_reemplazo .................. ok
-- W15_filas_historial_admin_alfa .............. 2
-- W15_filas_cerradas .......................... 1
-- W16_auditoria_actor_correcto ................ true
-- W17_actualizar_perfil_ajeno_filas ........... 0
-- W18_actualizar_perfil_propio_filas .......... 1
-- W19_insertar_perfil_ajeno ................... 42501
-- W20_alterar_auditoria ....................... 42501
-- W21_truncar_auditoria ....................... 42501
-- U1_club_admin_edita ......................... 42501
-- U2_coach_edita .............................. 42501
-- U3_anon_edita ............................... 42501
-- U4_pa_edita ................................. ok
-- U5_nombre_vacio ............................. 23514
-- U6_club_inexistente ......................... P0002
-- U7_nombre_actualizado ....................... Club Ficticio Delta Renombrado
-- U8_ciudad_actualizada ....................... Medellin
-- U9_auditoria_update ......................... true
-- =============================================================================
