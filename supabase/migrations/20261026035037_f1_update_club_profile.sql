
-- =============================================================================
-- F1 · Actualizacion del perfil de club
-- Requisitos: A-01, A-03, S-04, T-01. Matriz DEC-03: "gestionar club/usuarios"
-- corresponde al administrador de plataforma.
--
-- Criterio adoptado (el mas restrictivo de los compatibles con la matriz):
-- SOLO platform_admin edita el perfil del club. Un club_admin gestiona
-- entrenadores, no la identidad del club. Queda registrado como provisional
-- en docs/implementation/f1/00-autorizacion-y-alcance.md.
--
-- El trigger trg_audit_clubs registra before_data/after_data de cada cambio.
-- =============================================================================

create or replace function public.fn_update_club(
  p_club_id uuid,
  p_name    text default null,
  p_city    text default null,
  p_country char(2) default null,
  p_status  public.club_status default null
) returns void
language plpgsql security definer set search_path = ''
as $$
declare v_uid uuid := auth.uid();
begin
  if v_uid is null then
    raise exception 'No autenticado' using errcode = '28000';
  end if;

  if not app.is_platform_admin() then
    raise exception 'No autorizado: se requiere administrador de plataforma'
      using errcode = '42501';
  end if;

  if not exists (select 1 from public.clubs c where c.id = p_club_id) then
    raise exception 'El club % no existe', p_club_id using errcode = 'P0002';
  end if;

  -- Los campos nulos conservan el valor actual. Un nombre vacio no se ignora:
  -- cae en el CHECK de la tabla y se rechaza (23514), en lugar de pasar
  -- desapercibido como si no se hubiera enviado nada.
  update public.clubs
     set name    = case when p_name    is null then name    else btrim(p_name) end,
         city    = case when p_city    is null then city    else nullif(btrim(p_city), '') end,
         country = coalesce(p_country, country),
         status  = coalesce(p_status, status)
   where id = p_club_id;
end $$;

revoke all on function public.fn_update_club(uuid, text, text, char, public.club_status)
  from public, anon;
grant execute on function public.fn_update_club(uuid, text, text, char, public.club_status)
  to authenticated;
