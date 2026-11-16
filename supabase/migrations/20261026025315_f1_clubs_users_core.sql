
-- =============================================================================
-- F1 · Perfiles de club y usuarios — núcleo de datos
-- Requisitos: A-01 (club_id + filtrado), A-02 (historial inmutable),
--             DEC-02 (multi-club, aislamiento), DEC-03 (roles por club), T-01.
-- Datos: ninguno. Esta migración solo define estructura.
-- =============================================================================

-- --- Tipos -------------------------------------------------------------------
do $$ begin
  create type public.club_role as enum ('club_admin', 'coach');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.membership_status as enum ('active', 'inactive');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.club_status as enum ('active', 'suspended', 'closed');
exception when duplicate_object then null; end $$;

-- --- Clubes ------------------------------------------------------------------
create table if not exists public.clubs (
  id          uuid primary key default gen_random_uuid(),
  name        text not null check (length(btrim(name)) between 3 and 120),
  city        text check (city is null or length(btrim(city)) between 2 and 80),
  country     char(2) not null default 'CO' check (country ~ '^[A-Z]{2}$'),
  status      public.club_status not null default 'active',
  created_at  timestamptz not null default now(),
  created_by  uuid not null references auth.users(id) on delete restrict
);

comment on table public.clubs is
  'Club = unidad de aislamiento (DEC-02). No contiene datos personales de terceros.';

-- --- Perfiles (identidad global, sin club_id) --------------------------------
create table if not exists public.profiles (
  id            uuid primary key references auth.users(id) on delete restrict,
  display_name  text not null check (length(btrim(display_name)) between 2 and 80),
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

comment on table public.profiles is
  'Identidad global minima. Sin rol, sin club_id, sin datos deportivos ni sensibles.';

-- --- Administracion de plataforma (ambito separado de los roles de club) -----
create table if not exists public.platform_admins (
  user_id     uuid primary key references auth.users(id) on delete restrict,
  granted_at  timestamptz not null default now(),
  granted_by  uuid references auth.users(id) on delete restrict
);

comment on table public.platform_admins is
  'Ambito de plataforma, deliberadamente separado de club_memberships (evita rol global).';

-- --- Pertenencia al club, con historial --------------------------------------
create table if not exists public.club_memberships (
  id          uuid primary key default gen_random_uuid(),
  club_id     uuid not null references public.clubs(id) on delete restrict,
  user_id     uuid not null references auth.users(id) on delete restrict,
  role        public.club_role not null,
  status      public.membership_status not null default 'active',
  started_at  timestamptz not null default now(),
  ended_at    timestamptz,
  created_by  uuid not null references auth.users(id) on delete restrict,
  constraint membership_end_after_start check (ended_at is null or ended_at >= started_at),
  constraint membership_status_matches_end check ((status = 'active') = (ended_at is null))
);

comment on table public.club_memberships is
  'Rol + vigencia. El rol NO se guarda en profiles. Cambiar rol = cerrar fila y abrir otra (historial).';

-- Una sola pertenencia vigente por persona y club; el historial no se sobrescribe.
create unique index if not exists club_memberships_one_current
  on public.club_memberships (club_id, user_id) where ended_at is null;

create index if not exists club_memberships_active_by_user
  on public.club_memberships (user_id) where ended_at is null;

create index if not exists club_memberships_active_by_club
  on public.club_memberships (club_id) where ended_at is null;

-- --- Bitacora append-only (T-01) ---------------------------------------------
create table if not exists public.audit_events (
  id            bigint generated always as identity primary key,
  occurred_at   timestamptz not null default now(),
  actor_user_id uuid,
  actor_role    text,
  club_id       uuid,
  entity        text not null,
  entity_id     text not null,
  action        text not null,
  before_data   jsonb,
  after_data    jsonb
);

comment on table public.audit_events is
  'Append-only. Solo identificadores y estado, sin datos personales en claro (T-01, minimizacion).';

create index if not exists audit_events_by_club
  on public.audit_events (club_id, occurred_at desc);
