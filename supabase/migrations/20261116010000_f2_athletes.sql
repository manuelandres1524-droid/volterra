-- F2: fichas de atleta (solo mayores de edad, art. 9 Ley 1581/2012; P-13).
-- Menores/NNA fuera de alcance: altas con birth_date >= hoy - 18 años son rechazadas.
-- Auditoría sanitizada: el trigger NO guarda display_name ni birth_date condicionales.

do $$
begin
  create type public.athlete_gender as enum ('male', 'female', 'unspecified');
exception
  when duplicate_object then null;
end $$;

do $$
begin
  create type public.athlete_status as enum ('active', 'inactive');
exception
  when duplicate_object then null;
end $$;

create table if not exists public.athletes (
  id uuid primary key default gen_random_uuid(),
  club_id uuid not null references public.clubs(id) on delete restrict,
  display_name text not null,
  position text,
  birth_date date not null,
  gender public.athlete_gender not null default 'unspecified',
  category text,
  status public.athlete_status not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  created_by uuid not null references auth.users(id) on delete restrict,

  constraint athletes_display_name_length check (
    char_length(btrim(display_name)) between 2 and 120
  ),
  constraint athletes_position_length check (
    position is null or char_length(btrim(position)) between 2 and 30
  ),
  constraint athletes_category_length check (
    category is null or char_length(btrim(category)) between 2 and 30
  ),
  constraint athletes_birth_date_adult check (
    birth_date <= current_date - interval '18 years'
    and birth_date >= current_date - interval '100 years'
  )
);

comment on table public.athletes is
  'Fichas de atleta de clubes VOLTERRA. Solo mayores de edad (art. 9 Ley 1581/2012). E-2/E-7/E-8 (NNA) pendientes: menores fuera de F2.';
comment on column public.athletes.display_name is 'Alias público, no es nombre legal.';
comment on column public.athletes.birth_date is 'Fecha de nacimiento. No se expone en auditoría en claro.';

create index if not exists athletes_club_id_active_idx
  on public.athletes (club_id)
  where status = 'active';

revoke all on public.athletes from anon, authenticated;
alter table public.athletes enable row level security;
alter table public.athletes force row level security;

drop policy if exists athletes_select on public.athletes;
create policy athletes_select on public.athletes
  for select to authenticated
  using (app.is_platform_admin() or app.is_club_member(club_id));

-- Escritura solo vía RPC SECURITY DEFINER (sin políticas de escritura).
grant select on public.athletes to authenticated;

-- Guarda para gestión de atletas: platform_admin en cualquier club; si no, club_admin del club.
create or replace function app.assert_can_manage_athletes(p_club_id uuid)
returns void
language plpgsql stable security definer set search_path = ''
as $$
begin
  if auth.uid() is null then
    raise exception 'No autenticado' using errcode = '28000';
  end if;

  if app.is_platform_admin() then
    return;
  end if;

  if not app.has_club_role(p_club_id, array['club_admin']::public.club_role[]) then
    raise exception 'No autorizado: se requiere administrador del club'
      using errcode = '42501';
  end if;
end $$;

revoke all on function app.assert_can_manage_athletes(uuid) from public, anon;
grant execute on function app.assert_can_manage_athletes(uuid) to authenticated;

-- Auditoría sanitizada para atletas: sin display_name ni birth_date en claro.
create or replace function app.audit_athlete_change()
returns trigger
language plpgsql security definer set search_path = ''
as $$
declare
  v_club_id uuid := coalesce(
    (case when tg_op in ('INSERT','UPDATE') then (to_jsonb(new)->>'club_id')::uuid end),
    (case when tg_op in ('UPDATE','DELETE') then (to_jsonb(old)->>'club_id')::uuid end)
  );
  v_role text;
begin
  if app.is_platform_admin() then
    v_role := 'platform_admin';
  else
    select m.role::text into v_role
    from public.club_memberships m
    where m.user_id = auth.uid()
      and m.ended_at is null
      and m.club_id = v_club_id
    limit 1;
  end if;

  insert into public.audit_events
    (actor_user_id, actor_role, club_id, entity, entity_id, action)
  values
    (auth.uid(), v_role, v_club_id, 'athletes',
     coalesce((case when tg_op in ('INSERT','UPDATE') then new.id end)::text,
              (case when tg_op in ('UPDATE','DELETE') then old.id end)::text),
     lower(tg_op));
  return null;
end $$;

revoke all on function app.audit_athlete_change() from public, anon, authenticated;

drop trigger if exists trg_audit_athletes on public.athletes;
create trigger trg_audit_athletes
  after insert or update or delete on public.athletes
  for each row execute function app.audit_athlete_change();

drop trigger if exists trg_athletes_updated_at on public.athletes;
create trigger trg_athletes_updated_at
  before update on public.athletes
  for each row execute function app.touch_updated_at();

-- RPC: altas (solo club_admin / platform_admin).
create or replace function public.fn_create_athlete(
  p_club_id uuid,
  p_display_name text,
  p_birth_date date,
  p_position text default null,
  p_gender public.athlete_gender default 'unspecified',
  p_category text default null
) returns uuid
language plpgsql security definer set search_path = ''
as $$
declare
  v_id uuid;
  v_uid uuid := auth.uid();
begin
  if v_uid is null then
    raise exception 'No autenticado' using errcode = '28000';
  end if;

  perform app.assert_can_manage_athletes(p_club_id);

  if not exists (select 1 from public.clubs c where c.id = p_club_id and c.status = 'active') then
    raise exception 'El club no existe o no está activo' using errcode = 'P0002';
  end if;

  insert into public.athletes (club_id, display_name, position, birth_date, gender, category, created_by)
  values (p_club_id, btrim(p_display_name),
          nullif(btrim(p_position), ''),
          p_birth_date,
          coalesce(p_gender, 'unspecified'),
          nullif(btrim(p_category), ''),
          v_uid)
  returning id into v_id;

  return v_id;
end $$;

revoke all on function public.fn_create_athlete(uuid, text, date, text, public.athlete_gender, text) from public, anon;
grant execute on function public.fn_create_athlete(uuid, text, date, text, public.athlete_gender, text) to authenticated;

-- RPC: edición (null conserva el valor vigente).
create or replace function public.fn_update_athlete(
  p_athlete_id uuid,
  p_display_name text default null,
  p_position text default null,
  p_gender public.athlete_gender default null,
  p_category text default null
) returns uuid
language plpgsql security definer set search_path = ''
as $$
declare
  v_club uuid;
  v_status public.athlete_status;
begin
  if auth.uid() is null then
    raise exception 'No autenticado' using errcode = '28000';
  end if;

  select a.club_id, a.status into v_club, v_status
  from public.athletes a
  where a.id = p_athlete_id
  for update;

  if not found then
    raise exception 'El atleta no existe' using errcode = 'P0002';
  end if;

  perform app.assert_can_manage_athletes(v_club);

  update public.athletes a
  set display_name = coalesce(nullif(btrim(p_display_name), ''), a.display_name),
      position = case when p_position is not null then nullif(btrim(p_position), '') else a.position end,
      gender = coalesce(p_gender, a.gender),
      category = case when p_category is not null then nullif(btrim(p_category), '') else a.category end
  where a.id = p_athlete_id;

  return p_athlete_id;
end $$;

revoke all on function public.fn_update_athlete(uuid, text, text, public.athlete_gender, text) from public, anon;
grant execute on function public.fn_update_athlete(uuid, text, text, public.athlete_gender, text) to authenticated;

-- RPC: desactivación lógica (status = 'inactive').
create or replace function public.fn_deactivate_athlete(
  p_athlete_id uuid
) returns uuid
language plpgsql security definer set search_path = ''
as $$
declare
  v_club uuid;
begin
  if auth.uid() is null then
    raise exception 'No autenticado' using errcode = '28000';
  end if;

  select a.club_id into v_club
  from public.athletes a
  where a.id = p_athlete_id
    and a.status = 'active'
  for update;

  if not found then
    raise exception 'El atleta no existe o ya está inactivo' using errcode = 'P0002';
  end if;

  perform app.assert_can_manage_athletes(v_club);

  update public.athletes a
  set status = 'inactive'
  where a.id = p_athlete_id;

  return p_athlete_id;
end $$;

revoke all on function public.fn_deactivate_athlete(uuid) from public, anon;
grant execute on function public.fn_deactivate_athlete(uuid) to authenticated;
