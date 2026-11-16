-- =============================================================================
-- F1 · Revocación de privilegios por defecto en public (F-11)
-- Contexto: los privilegios POR DEFECTO en public conceden arwdDxtm a anon y
-- authenticated. Las migraciones anteriores revocan explícitamente para las
-- tablas conocidas, pero las tablas futuras heredarían los privilegios por
-- defecto. Esta migración revoca los privilegios por defecto para que cada
-- tabla nueva deba otorgar explícitamente los grants necesarios.
-- Riesgo mitigado: tabla futura sin RLS habilitado accesible con la clave
-- pública (defense-in-depth sobre RLS).
-- =============================================================================

-- Revocar privilegios por defecto para tablas futuras en public
alter default privileges in schema public
    revoke all on tables from anon, authenticated;

alter default privileges in schema public
    revoke all on sequences from anon, authenticated;

-- También revocar para el rol supabase_admin (si existe) para evitar que
-- tablas futuras hereden privilegios amplios.
do $$
begin
    if exists (select 1 from pg_roles where rolname = 'supabase_admin') then
        alter default privileges in schema public
            revoke all on tables from supabase_admin;
        alter default privileges in schema public
            revoke all on sequences from supabase_admin;
    end if;
end $$;

-- Verificación: mostrar privilegios por defecto actuales
-- (comentado para no bloquear la migración en entornos sin pg_catalog accesible)
-- select * from pg_default_acl where defaclnamespace = 'public'::regnamespace;