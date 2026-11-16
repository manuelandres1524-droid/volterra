
-- =============================================================================
-- F1 · Denegacion por defecto para objetos futuros y cierre de helpers
-- Requisitos: A-01, A-03, S-02 (superficie minima), DEC-02.
--
-- Motivo:
--  1) El proyecto concede por defecto arwdDxtm a anon y authenticated sobre
--     toda tabla nueva de public. Las tablas de F1 se revocaron a mano; esta
--     migracion evita que la siguiente migracion vuelva a exponerlas.
--  2) Varios helpers de app quedaron con el ACL por defecto de PostgreSQL,
--     que concede EXECUTE a PUBLIC. Son SECURITY DEFINER y leen pertenencias:
--     no deben ser invocables por el cliente.
--
-- Limitacion conocida y documentada en supabase/README.md: PostgreSQL concede
-- EXECUTE a PUBLIC en cada funcion nueva y ALTER DEFAULT PRIVILEGES no elimina
-- esa concesion base. Por eso toda migracion que cree funciones en public debe
-- revocarla explicitamente.
-- =============================================================================

-- --- 1. Objetos futuros: sin privilegios para roles de cliente ---------------
alter default privileges in schema public revoke all on tables from anon, authenticated;
alter default privileges in schema public revoke all on sequences from anon, authenticated;
alter default privileges in schema app    revoke all on tables from anon, authenticated;
alter default privileges in schema app    revoke all on sequences from anon, authenticated;
alter default privileges in schema public revoke execute on functions from anon, authenticated;
alter default privileges in schema app    revoke execute on functions from anon, authenticated;

-- --- 2. Barrido de funciones existentes -------------------------------------
do $$
declare r record;
begin
  -- Funciones expuestas por PostgREST: PUBLIC y anon no las ejecutan.
  for r in
    select p.oid::regprocedure::text as fn
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public' and p.prokind = 'f'
  loop
    execute format('revoke all on function %s from public, anon', r.fn);
  end loop;

  -- Helpers internos: tampoco los ejecuta el cliente autenticado.
  for r in
    select p.oid::regprocedure::text as fn
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'app' and p.prokind = 'f'
  loop
    execute format('revoke all on function %s from public, anon, authenticated', r.fn);
  end loop;
end $$;

-- --- 3. Restituir solo lo que las politicas RLS necesitan --------------------
-- Las politicas se evaluan con el rol del solicitante, asi que authenticated
-- necesita EXECUTE en estos cinco helpers y en ningun otro de app.
grant execute on function app.current_user_id()                       to authenticated;
grant execute on function app.is_platform_admin()                      to authenticated;
grant execute on function app.is_club_member(uuid)                     to authenticated;
grant execute on function app.has_club_role(uuid, public.club_role[])  to authenticated;
grant execute on function app.can_view_profile(uuid)                   to authenticated;

-- --- 4. Las RPC siguen disponibles para authenticated ------------------------
grant execute on function public.fn_create_club(text, text, char)              to authenticated;
grant execute on function public.fn_add_member(uuid, uuid, public.club_role)   to authenticated;
grant execute on function public.fn_change_member_role(uuid, public.club_role) to authenticated;
grant execute on function public.fn_end_membership(uuid)                       to authenticated;
