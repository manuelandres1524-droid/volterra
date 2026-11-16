-- =============================================================================
-- F1 · Preflight remoto antes de aplicar 20261102120000_f1_is_platform_admin.sql
-- -----------------------------------------------------------------------------
-- Solo lectura: no crea objetos, no escribe filas, no cambia privilegios.
-- Se puede ejecutar varias veces sin efecto.
--
-- Objetivo: saber si el proyecto remoto ya tiene el esquema de F1 y cuál es la
-- última migración registrada. Con eso se decide si basta la migración 7 o si
-- hay que aplicar la secuencia completa 1→7.
--
-- Ejecutar como `postgres` en el SQL Editor del panel.
-- =============================================================================

select set_config('preflight.out', '{}', false);

do $$
declare
  v jsonb := '{}'::jsonb;
  n bigint;
  t text;
  tablas text[] := array[
    'clubs', 'profiles', 'platform_admins', 'club_memberships', 'audit_events'
  ];
begin
  v := v || jsonb_build_object(
    'base_de_datos', current_database(),
    'rol', current_user,
    'version_pg', current_setting('server_version'),
    'hay_esquema_app', exists (select 1 from pg_namespace where nspname = 'app'),
    'hay_app_is_platform_admin',
      to_regprocedure('app.is_platform_admin()') is not null,
    'hay_fn_is_platform_admin',
      to_regprocedure('public.fn_is_platform_admin()') is not null
  );

  foreach t in array tablas loop
    if to_regclass('public.' || t) is null then
      v := v || jsonb_build_object('filas_' || t, 'tabla ausente');
    else
      execute format('select count(*) from public.%I', t) into n;
      v := v || jsonb_build_object('filas_' || t, n);
    end if;
  end loop;

  if to_regclass('supabase_migrations.schema_migrations') is not null then
    execute 'select count(*) from supabase_migrations.schema_migrations' into n;
    v := v || jsonb_build_object('migraciones_registradas', n);
  else
    v := v || jsonb_build_object('migraciones_registradas', 'sin tabla');
  end if;

  perform set_config('preflight.out', v::text, false);
end $$;

select current_setting('preflight.out')::jsonb as preflight;

-- Detalle de migraciones registradas. Si esta consulta falla, el proyecto no
-- tiene el historial estándar de Supabase y hay que revisarlo antes de seguir.
select version, name
from supabase_migrations.schema_migrations
order by version;
