
-- =============================================================================
-- F1 · RPC de solo lectura para el ámbito de plataforma
-- -----------------------------------------------------------------------------
-- Motivo:
--   `platform_admins` no tiene GRANT para `authenticated` ni políticas RLS.
--   La suite `f1_rls_isolation` exige que esa tabla devuelva 42501 por API.
--   La capa de aplicación necesita saber si el llamador es platform_admin sin
--   consultar la tabla. Esta función devuelve solo un booleano.
--
-- Seguridad:
--   - SECURITY DEFINER con search_path vacío.
--   - No expone filas, correos ni identificadores de `platform_admins`.
--   - Solo `authenticated` puede ejecutarla; `anon` y PUBLIC no.
-- =============================================================================

create or replace function public.fn_is_platform_admin()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select app.is_platform_admin()
$$;

comment on function public.fn_is_platform_admin() is
  'Devuelve solo si el llamador es platform_admin. Evita exponer platform_admins por PostgREST.';

revoke all on function public.fn_is_platform_admin() from public, anon, authenticated;
grant execute on function public.fn_is_platform_admin() to authenticated;
