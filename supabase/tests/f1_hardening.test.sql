-- =============================================================================
-- F1 · Pruebas de endurecimiento (migración 20261026040817_f1_hardening)
-- -----------------------------------------------------------------------------
-- Verifica los cuatro defectos corregidos tras la revisión de seguridad
-- independiente, más la regresión de privilegios de profiles:
--   D1  el club no puede quedarse sin administrador por concurrencia
--       (se comprueba de forma ESTRUCTURAL: el bloqueo va antes de la guarda;
--        la carrera real necesita dos conexiones y no se prueba aquí)
--   D2  profiles: privilegios por columna y auditoría sin datos personales
--   D3  la auditoría de clubs se registra con club_id propio
--   D4  el club_admin ve la plantilla vigente, no el historial de exmiembros
--
-- Igual que la suite principal: fixtures FICTICIOS (@example.com), `set local
-- role` + `request.jwt.claims`, y ROLLBACK final. Sin residuos.
--
-- Ejecución: enviar el archivo completo como una sola consulta.
-- =============================================================================

begin;

-- Baseline previo: la suite puede ejecutarse sobre una base con datos ficticios
-- (usuarios demo). Los conteos de auditoría se expresan como delta para seguir
-- siendo comprobables sin vaciar la base ni borrar datos.
select set_config(
  'f1h.base_profiles_audit',
  (select count(*)::text from public.audit_events where entity = 'profiles'),
  true
);

-- -----------------------------------------------------------------------------
-- 0. Fixtures ficticios
-- -----------------------------------------------------------------------------
insert into auth.users (id, instance_id, aud, role, email, created_at, updated_at) values
  ('a1000000-0000-4000-8000-000000000001','00000000-0000-0000-0000-000000000000','authenticated','authenticated','h-pa@example.com',       now(), now()),
  ('a1000000-0000-4000-8000-000000000002','00000000-0000-0000-0000-000000000000','authenticated','authenticated','h-adm-alfa@example.com', now(), now()),
  ('a1000000-0000-4000-8000-000000000003','00000000-0000-0000-0000-000000000000','authenticated','authenticated','h-coach-alfa@example.com',now(), now()),
  ('a1000000-0000-4000-8000-000000000004','00000000-0000-0000-0000-000000000000','authenticated','authenticated','h-adm-beta@example.com', now(), now()),
  ('a1000000-0000-4000-8000-000000000005','00000000-0000-0000-0000-000000000000','authenticated','authenticated','h-ex-coach@example.com', now(), now()),
  ('a1000000-0000-4000-8000-000000000006','00000000-0000-0000-0000-000000000000','authenticated','authenticated','h-nuevo-coach@example.com',now(), now());

-- Perfiles de fixture (insertados como postgres, sin claims): generan eventos
-- de auditoría con actor nulo, que NO deben contener datos personales.
insert into public.profiles (id, display_name) values
  ('a1000000-0000-4000-8000-000000000001','Persona Ficticia PA'),
  ('a1000000-0000-4000-8000-000000000002','Persona Ficticia Adm Alfa'),
  ('a1000000-0000-4000-8000-000000000003','Persona Ficticia Coach Alfa'),
  ('a1000000-0000-4000-8000-000000000004','Persona Ficticia Adm Beta'),
  ('a1000000-0000-4000-8000-000000000005','Persona Ficticia Ex Coach');

insert into public.platform_admins (user_id) values ('a1000000-0000-4000-8000-000000000001');

insert into public.clubs (id, name, city, created_by) values
  ('c1000000-0000-4000-8000-00000000000a','Club Ficticio Hotel','Bogota',  'a1000000-0000-4000-8000-000000000001'),
  ('c1000000-0000-4000-8000-00000000000b','Club Ficticio India','Medellin','a1000000-0000-4000-8000-000000000001');

insert into public.club_memberships
  (id, club_id, user_id, role, status, started_at, ended_at, created_by) values
  ('b1000000-0000-4000-8000-000000000001','c1000000-0000-4000-8000-00000000000a','a1000000-0000-4000-8000-000000000002','club_admin','active',   now(), null, 'a1000000-0000-4000-8000-000000000001'),
  ('b1000000-0000-4000-8000-000000000002','c1000000-0000-4000-8000-00000000000a','a1000000-0000-4000-8000-000000000003','coach',     'active',   now(), null, 'a1000000-0000-4000-8000-000000000001'),
  ('b1000000-0000-4000-8000-000000000003','c1000000-0000-4000-8000-00000000000b','a1000000-0000-4000-8000-000000000004','club_admin','active',   now(), null, 'a1000000-0000-4000-8000-000000000001'),
  ('b1000000-0000-4000-8000-000000000004','c1000000-0000-4000-8000-00000000000a','a1000000-0000-4000-8000-000000000005','coach',     'inactive', now() - interval '30 days', now() - interval '1 day', 'a1000000-0000-4000-8000-000000000001');

-- -----------------------------------------------------------------------------
-- 1. Comprobaciones estructurales
-- -----------------------------------------------------------------------------
do $$
declare
  v jsonb := '{}';
  v_src_change text;
  v_src_end text;
begin
  v_src_change := (select p.prosrc from pg_proc p join pg_namespace n on n.oid = p.pronamespace
                   where n.nspname = 'public' and p.proname = 'fn_change_member_role');
  v_src_end := (select p.prosrc from pg_proc p join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'public' and p.proname = 'fn_end_membership');

  v := v || jsonb_build_object(
    -- D1: el bloqueo de la fila del club existe y precede a la guarda.
    'D1_bloqueo_en_change_role',
      position('for update' in lower(v_src_change)) > 0,
    'D1_bloqueo_en_end_membership',
      position('for update' in lower(v_src_end)) > 0,
    'D1_bloqueo_antes_de_la_guarda',
      position('for update' in lower(v_src_change)) > 0
      and position('for update' in lower(v_src_change))
          < position('assert_club_keeps_admin' in lower(v_src_change)),
    'D1_rechazo_si_la_fila_cambio',
      position('40001' in lower(v_src_change)) > 0
      and position('40001' in lower(v_src_end)) > 0,

    -- D2: privilegios por columna en profiles.
    'D2_insert_columna_display_name',
      has_column_privilege('authenticated','public.profiles','display_name','insert'),
    'D2_insert_columna_created_at_denegado',
      not has_column_privilege('authenticated','public.profiles','created_at','insert'),
    'D2_update_columna_display_name',
      has_column_privilege('authenticated','public.profiles','display_name','update'),
    'D2_update_columna_created_at_denegado',
      not has_column_privilege('authenticated','public.profiles','created_at','update'),
    'D2_update_tabla_completa_denegado',
      not has_table_privilege('authenticated','public.profiles','update'),
    'D2_trigger_auditoria_profiles', (
      select count(*)::int from pg_trigger t
      join pg_class c on c.oid = t.tgrelid
      join pg_namespace n on n.oid = c.relnamespace
      where n.nspname = 'public' and c.relname = 'profiles'
        and t.tgname = 'trg_audit_profiles' and not t.tgisinternal
    ),

    -- D4: la política de pertenencias ya no expone el historial a club_admin.
    'D4_politica_sin_historial_para_club_admin', (
      select pg_get_expr(p.polqual, p.polrelid) like '%ended_at IS NULL%'
      from pg_policy p
      join pg_class c on c.oid = p.polrelid
      join pg_namespace n on n.oid = c.relnamespace
      where n.nspname = 'public' and c.relname = 'club_memberships'
        and p.polname = 'memberships_select'
    )
  );

  perform set_config('f1h.results', v::text, true);
end $$;

-- -----------------------------------------------------------------------------
-- 2. D4 · club_admin Alfa: ve la plantilla vigente, no el historial
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a1000000-0000-4000-8000-000000000002","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1h.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'D4_club_admin_ve_pertenencia_vigente', (
      select count(*)::int from public.club_memberships
      where id = 'b1000000-0000-4000-8000-000000000002'),
    'D4_club_admin_no_ve_exmiembro', (
      select count(*)::int from public.club_memberships
      where id = 'b1000000-0000-4000-8000-000000000004'),
    'D4_club_admin_ve_solo_vigentes_del_club', (
      select count(*)::int from public.club_memberships
      where club_id = 'c1000000-0000-4000-8000-00000000000a')
  );
  perform set_config('f1h.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 3. Escritura de club_admin sobre otro club: denegada
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a1000000-0000-4000-8000-000000000002","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1h.results')::jsonb; v_state text;
begin
  -- cambio de rol en el club Beta
  begin
    perform public.fn_change_member_role(
      'b1000000-0000-4000-8000-000000000003', 'coach');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('X1_cambiar_rol_en_club_ajeno', v_state);

  -- cierre de pertenencia en el club Beta
  begin
    perform public.fn_end_membership('b1000000-0000-4000-8000-000000000003');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('X2_cerrar_pertenencia_en_club_ajeno', v_state);

  -- el intento fallido no modificó nada observable
  perform set_config('f1h.results', v::text, true);
end $$;
reset role;

do $$
declare v jsonb := current_setting('f1h.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'X3_club_ajeno_intacto', (
      select (role = 'club_admin' and ended_at is null) from public.club_memberships
      where id = 'b1000000-0000-4000-8000-000000000003')
  );
  perform set_config('f1h.results', v::text, true);
end $$;

-- -----------------------------------------------------------------------------
-- 4. Sección de auditoría no es escribible por el cliente
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a1000000-0000-4000-8000-000000000001","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1h.results')::jsonb; v_state text;
begin
  begin
    insert into public.audit_events (entity, entity_id, action)
    values ('clubs','00000000-0000-4000-8000-000000000000','insert');
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('X4_insert_directo_auditoria', v_state);

  begin
    update public.audit_events set action = 'falso' where true;
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('X5_update_directo_auditoria', v_state);

  perform set_config('f1h.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 5. D3 · la auditoría del club lleva su propio club_id
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a1000000-0000-4000-8000-000000000001","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1h.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'D3_evento_club_con_club_id', (
      select count(*)::int from public.audit_events
      where entity = 'clubs'
        and entity_id = 'c1000000-0000-4000-8000-00000000000a'
        and club_id = 'c1000000-0000-4000-8000-00000000000a'
        and action = 'insert'),
    'D3_ningun_evento_de_clubs_sin_club_id', (
      select count(*)::int from public.audit_events
      where entity = 'clubs' and club_id is null),
    -- D2: los eventos de profiles no copian nombre ni ningún dato personal
    'D2_eventos_profiles_sin_datos', (
      select count(*)::int from public.audit_events
      where entity = 'profiles' and (before_data is not null or after_data is not null)),
    'D2_eventos_profiles_registrados', (
      select count(*)::int from public.audit_events where entity = 'profiles')
      - current_setting('f1h.base_profiles_audit')::int
  );
  perform set_config('f1h.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 6. D2 · profiles: el titular escribe solo su nombre visible, y queda auditado
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a1000000-0000-4000-8000-000000000006","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1h.results')::jsonb; v_state text; v_rows int;
begin
  -- alta del perfil propio intentando fijar created_at: denegada por columna
  -- (se ejecuta antes del alta válida para que la negativa no dependa del
  --  duplicado: la RLS deja pasar la fila, es el privilegio el que la corta)
  begin
    insert into public.profiles (id, display_name, created_at)
    values ('a1000000-0000-4000-8000-000000000006','Persona Ficticia Nuevo Coach', now());
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('X7_alta_con_created_at', v_state);

  -- alta del perfil propio con las columnas permitidas
  begin
    insert into public.profiles (id, display_name)
    values ('a1000000-0000-4000-8000-000000000006','Persona Ficticia Nuevo Coach');
    v_state := 'ok';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('X6_alta_perfil_propio', v_state);

  -- actualización del nombre visible propio
  update public.profiles set display_name = 'Persona Ficticia Nuevo Coach (editada)'
   where id = 'a1000000-0000-4000-8000-000000000006';
  get diagnostics v_rows = row_count;
  v := v || jsonb_build_object('X8_actualizar_nombre_propio_filas', v_rows);

  -- actualización intentando fijar created_at
  begin
    update public.profiles set created_at = now() - interval '1 year'
     where id = 'a1000000-0000-4000-8000-000000000006';
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('X9_actualizar_created_at', v_state);

  -- actualización intentando cambiar el id (no hay privilegio de columna)
  begin
    update public.profiles set id = 'a1000000-0000-4000-8000-000000000005'
     where id = 'a1000000-0000-4000-8000-000000000006';
    v_state := 'sin_error';
  exception when others then v_state := sqlstate;
  end;
  v := v || jsonb_build_object('X10_actualizar_id', v_state);

  perform set_config('f1h.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 7. D2 · auditoría del cambio de perfil y de la pertenencia del exmiembro
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a1000000-0000-4000-8000-000000000002","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1h.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'D4_club_admin_sigue_sin_ver_exmiembro', (
      select count(*)::int from public.club_memberships
      where id = 'b1000000-0000-4000-8000-000000000004'),
    'D3_club_admin_ve_auditoria_de_su_club', (
      select count(*) > 0 from public.audit_events
      where club_id = 'c1000000-0000-4000-8000-00000000000a'),
    'D2_club_admin_no_ve_auditoria_de_perfiles', (
      select count(*)::int from public.audit_events where entity = 'profiles')
  );
  perform set_config('f1h.results', v::text, true);
end $$;
reset role;

select set_config('request.jwt.claims','{"sub":"a1000000-0000-4000-8000-000000000006","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1h.results')::jsonb;
begin
  -- Limitación conocida y deliberada: la política de audit_events solo admite
  -- platform_admin y club_admin del club del evento (T-01). El titular NO ve
  -- la auditoría de su propio perfil, aunque el evento exista. Es denegación
  -- por defecto, no una fuga; el derecho de acceso del titular queda como
  -- decisión funcional pendiente (ver docs/implementation/f1/).
  v := v || jsonb_build_object(
    'D2_titular_no_ve_auditoria_de_su_perfil', (
      select count(*)::int from public.audit_events
      where entity = 'profiles'
        and entity_id = 'a1000000-0000-4000-8000-000000000006'
        and actor_user_id = 'a1000000-0000-4000-8000-000000000006'),
    'D2_titular_no_ve_eventos_de_otros_perfiles', (
      select count(*)::int from public.audit_events
      where entity = 'profiles' and entity_id <> 'a1000000-0000-4000-8000-000000000006')
  );
  perform set_config('f1h.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 8. platform_admin: historial completo y auditoría global
-- -----------------------------------------------------------------------------
select set_config('request.jwt.claims','{"sub":"a1000000-0000-4000-8000-000000000001","role":"authenticated"}', true);
set local role authenticated;
do $$
declare v jsonb := current_setting('f1h.results')::jsonb;
begin
  v := v || jsonb_build_object(
    'D4_platform_admin_ve_exmiembro', (
      select count(*)::int from public.club_memberships
      where id = 'b1000000-0000-4000-8000-000000000004'),
    'D4_platform_admin_ve_historial_completo', (
      select count(*)::int from public.club_memberships
      where club_id = 'c1000000-0000-4000-8000-00000000000a'),
    'D2_platform_admin_ve_eventos_de_perfiles', (
      select count(*)::int from public.audit_events where entity = 'profiles')
      - current_setting('f1h.base_profiles_audit')::int,
    'D2_evento_update_del_titular_registrado', exists (
      select 1 from public.audit_events
      where entity = 'profiles'
        and entity_id = 'a1000000-0000-4000-8000-000000000006'
        and actor_user_id = 'a1000000-0000-4000-8000-000000000006'
        and action = 'update')
  );
  perform set_config('f1h.results', v::text, true);
end $$;
reset role;

-- -----------------------------------------------------------------------------
-- 9. Resultado
-- -----------------------------------------------------------------------------
select jsonb_pretty(current_setting('f1h.results')::jsonb) as results;

rollback;

-- =============================================================================
-- Valores esperados (26/10/2026, verificado sobre el proyecto de desarrollo)
-- -----------------------------------------------------------------------------
-- D1_bloqueo_en_change_role ................... true
-- D1_bloqueo_en_end_membership ................ true
-- D1_bloqueo_antes_de_la_guarda ............... true
-- D1_rechazo_si_la_fila_cambio ................ true
-- D2_insert_columna_display_name .............. true
-- D2_insert_columna_created_at_denegado ....... true
-- D2_update_columna_display_name .............. true
-- D2_update_columna_created_at_denegado ....... true
-- D2_update_tabla_completa_denegado ........... true
-- D2_trigger_auditoria_profiles ............... 1
-- D4_politica_sin_historial_para_club_admin ... true
-- D4_club_admin_ve_pertenencia_vigente ........ 1
-- D4_club_admin_no_ve_exmiembro ............... 0
-- D4_club_admin_ve_solo_vigentes_del_club ..... 2
-- X1_cambiar_rol_en_club_ajeno ................ 42501
-- X2_cerrar_pertenencia_en_club_ajeno ......... 42501
-- X3_club_ajeno_intacto ....................... true
-- X4_insert_directo_auditoria ................. 42501
-- X5_update_directo_auditoria ................. 42501
-- D3_evento_club_con_club_id .................. 1
-- D3_ningun_evento_de_clubs_sin_club_id ....... 0
-- D2_eventos_profiles_sin_datos ............... 0
-- D2_eventos_profiles_registrados ............. 5
-- X7_alta_con_created_at ...................... 42501
-- X6_alta_perfil_propio ....................... ok
-- X8_actualizar_nombre_propio_filas ........... 1
-- X9_actualizar_created_at .................... 42501
-- X10_actualizar_id ........................... 42501
-- D4_club_admin_sigue_sin_ver_exmiembro ....... 0
-- D3_club_admin_ve_auditoria_de_su_club ....... true
-- D2_club_admin_no_ve_auditoria_de_perfiles ... 0
-- D2_titular_no_ve_auditoria_de_su_perfil ..... 0   (limitación conocida, ver nota)
-- D2_titular_no_ve_eventos_de_otros_perfiles .. 0
-- D4_platform_admin_ve_exmiembro .............. 1
-- D4_platform_admin_ve_historial_completo ..... 3
-- D2_platform_admin_ve_eventos_de_perfiles .... 7
-- D2_evento_update_del_titular_registrado ..... true
--
-- Notas:
--  * D3_evento_club_con_club_id = 1: solo el club Alfa coincide con el filtro
--    entity_id. Los dos clubes de fixture se insertan como postgres y el
--    trigger deriva el club_id de la propia fila: ninguno queda en NULL.
--  * D2_eventos_profiles_registrados = 5 antes de la sección 6 (los cinco
--    perfiles de fixture). Tras el alta y la edición del titular son 7: el
--    alta y el UPDATE generan un evento cada uno, sin copiar datos.
--  * D4_platform_admin_ve_historial_completo = 3: en el club Alfa hay 2
--    pertenencias vigentes + 1 cerrada.
--  * D2_titular_no_ve_auditoria_de_su_perfil = 0: el evento existe (lo
--    comprueba D2_evento_update_del_titular_registrado), pero la política de
--    audit_events solo admite platform_admin y club_admin del club. Es
--    denegación por defecto. El acceso del titular a su propia traza queda
--    como decisión funcional pendiente.
-- =============================================================================
