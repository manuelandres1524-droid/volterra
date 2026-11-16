# O-03 · Respaldo y restauración: procedimiento técnico

**Estado:** **primer volcado real ejecutado y verificado el 26/10/2026** (416.995 bytes, 666 entradas,
SHA256 `970E7242…`), con **restauración de ensayo** en un clúster local desechable: 127/127
comprobaciones SQL en verde sobre la copia restaurada. **O-03 sigue abierta**: no se ha restaurado
en un proyecto Supabase real. Los objetivos **ya están decididos** (DEC-07, 13/11/2026): RPO 24 h,
RTO 8 h, volcado diario cifrado fuera del proveedor, retención 30 días, responsable el propietario.

**Alcance de lo probado:** el ensayo restaura `public` + `app` en un PostgreSQL 17.6 con `auth`
simulado (`auth.users` y `auth.uid()` equivalentes). No prueba un `pg_restore` completo de Supabase
—con `auth`, `storage`, extensiones y roles del proveedor— en otro proyecto.

**Naturaleza:** documento operativo. Los valores de RPO, RTO, frecuencia, retención, destino y
responsable vienen de **DEC-07** (aprobada el 13/11/2026); este documento no los modifica.

> **Actualización del 12/11/2026.** Los hechos de §1 son históricos y describen el proyecto
> `taevpaknhuoyiujqgjku`, que ya no resuelve en DNS. §2 y §3 se han reapuntado al proyecto
> indicado ahora, `tioeoswnhwrlbovkxocd`, con pooler IPv4
> `aws-1-us-east-2.pooler.supabase.com:5432`. No se ha ejecutado un volcado nuevo ni se ha leído
> ninguna credencial: las cifras de §1 no describen el proyecto nuevo.

---

## 1. Hechos comprobados

| Hecho | Dato |
|---|---|
| Binarios | PostgreSQL 17.6 en `C:\Users\Miguel\Tools\pgsql-17.6\pgsql\bin` (`pg_dump`, `pg_restore`, `psql`, `initdb`, `pg_ctl`) |
| Versión del servidor | PostgreSQL 17.11 (proyecto Supabase) |
| Host alcanzable | `aws-0-us-east-1.pooler.supabase.com:5432` (**pooler en modo sesión**) |
| Host no alcanzable | `db.taevpaknhuoyiujqgjku.supabase.co:5432` (resuelve a IPv6) |
| Credencial | `%APPDATA%\postgresql\pgpass.conf` **existe** desde el 26/10/2026; la creó el propietario. **No se ha leído su contenido** en ningún momento |
| Primer volcado real | 26/10/2026 21:18, `pg_dump -Fc` contra el pooler en modo sesión: **exit 0** |
| Restauración de ensayo | 26/10/2026, clúster local desechable con roles y `auth` simulados: **exit 0, 0 errores**, 127/127 pruebas |
| Respaldos automáticos | El plan gratuito de Supabase no los incluye |
| Docker | No instalado. `supabase db dump` no sirve; por eso `pg_dump` nativo |

---

## 2. Prerrequisito: `pgpass.conf` (lo crea el propietario, nunca por chat)

El archivo debe contener **una sola línea** con el formato de PostgreSQL:

```
aws-1-us-east-2.pooler.supabase.com:5432:postgres:postgres.tioeoswnhwrlbovkxocd:CONTRASEÑA
```

- `5432` es el **pooler en modo sesión**. `6543` (transacción) no admite todas las operaciones
  que necesita `pg_dump`.
- La contraseña es la de *Project Settings → Database*, no la `service_role`/`anon` key.

Creación y permisos (PowerShell, sin exponer el contenido):

```powershell
$dir = Join-Path $env:APPDATA 'postgresql'
New-Item -ItemType Directory -Force -Path $dir | Out-Null
notepad (Join-Path $dir 'pgpass.conf')
icacls (Join-Path $dir 'pgpass.conf') /inheritance:r /grant:r "$($env:USERNAME):(R)"
```

Verificación **sin imprimir la contraseña**: que el archivo exista y que `pg_dump` no pida
contraseña (si la pide, el formato de la línea es incorrecto).

---

## 3. Respaldo (a ejecutar cuando exista la credencial)

```powershell
$bin  = 'C:\Users\Miguel\Tools\pgsql-17.6\pgsql\bin'
$out  = "C:\Users\Miguel\Projects\VOLTERRA\workspace\backups\volterra-$(Get-Date -Format yyyyMMdd-HHmmss)"
New-Item -ItemType Directory -Force -Path $out | Out-Null

# 3.1 Esquema y datos completos, formato custom (permite restauración selectiva)
& "$bin\pg_dump.exe" -h aws-1-us-east-2.pooler.supabase.com -p 5432 -U postgres.tioeoswnhwrlbovkxocd `
  -d postgres -Fc -f "$out\volterra.dump"

# 3.2 Roles del cluster (puede fallar: `postgres` no es superusuario en Supabase)
& "$bin\pg_dumpall.exe" -h aws-1-us-east-2.pooler.supabase.com -p 5432 -U postgres.tioeoswnhwrlbovkxocd `
  --roles-only -f "$out\roles.sql"
```

**Advertencia sobre el volcado completo:** incluye esquemas de Supabase (`auth`, `storage`,
`extensions`…). Restaurarlo en un PostgreSQL «vanilla» falla por extensiones y objetos que exigen
superusuario. La restauración realista es **en otro proyecto Supabase**, no en un Postgres local.
Un respaldo reducido a `--schema=public --schema=app` no incluye `auth.users`, y
`clubs.created_by` tiene FK contra esa tabla: sin ella, la restauración de datos falla. No se ha
probado ninguna de las dos variantes contra el proyecto real.

**Verificación del archivo (obligatoria, antes de dar el respaldo por bueno):**

```powershell
(Get-Item "$out\volterra.dump").Length            # > 0
& "$bin\pg_restore.exe" --list "$out\volterra.dump" | Measure-Object -Line
(Get-FileHash "$out\volterra.dump" -Algorithm SHA256).Hash
```

Anotar tamaño, número de entradas del índice y hash. El 26/10/2026 se ejecutó el paso 3.1 y su
verificación (§4.2). **El paso 3.2 (`pg_dumpall --roles-only`) no se ejecutó**: el directorio del
volcado contiene solo `volterra.dump`.

---

## 4. Pruebas de restauración

### 4.1 Tubería genérica, con un fixture (26/10/2026)

Objetivo: comprobar que la tubería `pg_dump -Fc` → `pg_restore` reproduce un esquema con las
construcciones de F1 (esquema propio, enum, funciones `SECURITY DEFINER`, trigger, RLS forzada,
política, `GRANT`, comentario y datos). **No sustituye a la restauración de un volcado real de
Supabase.**

```powershell
$bin  = 'C:\Users\Miguel\Tools\pgsql-17.6\pgsql\bin'
$tmp  = Join-Path $env:TEMP 'volterra-pgtest'
$data = Join-Path $tmp 'data'

& "$bin\initdb.exe" -D $data -U postgres -A trust -E UTF8 --locale=C
& "$bin\pg_ctl.exe" -D $data -l "$tmp\server.log" -o "-p 55432 -c listen_addresses=127.0.0.1" -w start
& "$bin\createdb.exe" -h 127.0.0.1 -p 55432 -U postgres volterra_src
& "$bin\psql.exe"   -h 127.0.0.1 -p 55432 -U postgres -d volterra_src -v ON_ERROR_STOP=1 -f fixture.sql

& "$bin\pg_dump.exe"    -h 127.0.0.1 -p 55432 -U postgres -Fc -f "$tmp\src.dump" volterra_src
& "$bin\createdb.exe"   -h 127.0.0.1 -p 55432 -U postgres volterra_dst
& "$bin\pg_restore.exe" -h 127.0.0.1 -p 55432 -U postgres -d volterra_dst --exit-on-error "$tmp\src.dump"

& "$bin\pg_ctl.exe" -D $data -m fast stop
```

**Resultado real:** `pg_dump` 0, `pg_restore` 0, índice con 36 entradas, volcado de 7.586 bytes.
Comparación origen/destino con `json_build_object` sobre `pg_class`, `pg_proc`, `pg_policies`,
`pg_trigger`, `pg_indexes`, `pg_description` y conteos de filas:

```
ORIGEN : {"tablas":2,"funciones":3,"politicas":1,"triggers":1,"indices":3,
          "filas_clubs":3,"filas_auditoria":3,"comentarios":1,
          "md5_cuerpos":"f2cf142603cfe76e595a4df7a9eaaffb",
          "md5_politicas":"098f641dc65a6c13b955ceebbf8a3558","rls_forzada":true}
DESTINO: idéntico byte a byte
```

Con `--no-owner --no-privileges` la restauración también termina en 0 y conserva tablas, datos y
políticas, pero **pierde los `GRANT`**: `has_table_privilege('authenticated','public.clubs',
'SELECT')` devuelve `false`. Consecuencia: si se usa esa variante, los privilegios deben reponerse
después (en F1 están en las migraciones 2 y 4) y hay que verificarlos, no suponerlos.

### 4.2 Volcado real y ensayo de restauración (26/10/2026)

**Volcado.** Ejecutado con el comando de §3.1 contra el pooler en modo sesión, sin pedir contraseña
(la credencial de `pgpass.conf` funcionó). `exit 0`.

| Dato | Valor |
|---|---|
| Ruta | `workspace/backups/volterra-20261026-211832/volterra.dump` (no versionado: ver `.gitignore`) |
| Fecha y hora | 26/10/2026 21:18:33 |
| Tamaño | 416.995 bytes |
| SHA256 | `970E72423E5F7AEF72096ED02C1B953D44EF41A5908D13711653D26375F9F279` |
| Formato | `CUSTOM`, compresión `gzip`, *dump version* 1.16-0 |
| Entradas en `pg_restore --list` | **666** (la cabecera declara `TOC Entries: 673`; diferencia no explicada, se cita 666) |
| Servidor de origen | PostgreSQL 17.11 · volcado con `pg_dump` 17.6 |
| Esquemas presentes | `public`, `app`, `auth`, `storage`, `realtime`, `graphql`, `extensions`, `vault` |

**Ensayo.** Clúster desechable creado con `initdb` (PostgreSQL 17.6, puerto 55433, `trust`, solo
`127.0.0.1`), borrado al terminar. Antes de restaurar hubo que crear a mano lo que en Supabase ya
existe; sin ello `pg_restore` falla y el ensayo no mide nada:

- roles `anon`, `authenticated` y `service_role` (`nologin`; `service_role` con `BYPASSRLS`);
- esquema `app` vacío (el volcado no trae `CREATE SCHEMA app`);
- esquema `auth` con una tabla `auth.users` mínima y una función `auth.uid()` equivalente
  (lee `request.jwt.claims->>'sub'`), más `USAGE`/`SELECT` para los tres roles;
- rol `supabase_admin`, referenciado por privilegios por defecto del volcado.

Restauración selectiva: `pg_restore --no-owner -n public -n app` → **exit 0, cero líneas de error**.

| Métrica | Origen (Supabase) | Restaurado |
|---|---|---|
| Tablas en `public` | 5 | 5 |
| Funciones en `public`+`app` | 19 | 19 |
| Políticas | 6 | 6 |
| Triggers en `public`+`app` | 7 | 7 |
| Índices en `public` | 9 | 9 |
| Enums | 3 | 3 |
| Tablas con RLS `enable`+`force` | 5 | 5 |
| md5 de cuerpos de funciones | `5e11ad2b3f1a666e99dbad25c644e7e1` | idéntico |
| md5 de expresiones de políticas | `4d084dc57ec4a9c14452ade387f02c7d` | idéntico |
| md5 de privilegios tabla/rol/acción | `068aebb6d25a0164478addb34e4d13b6` | idéntico |

**Pruebas sobre la copia restaurada:** `f1_rls_isolation` 65/65, `f1_hardening` 37/37 y
`f1_service_role` 25/25 → **127/127**, ejecutadas con `psql -v ON_ERROR_STOP=1` y comparadas con las
expectativas anotadas en cada archivo.

**Quién lo ejecutó.** El asistente (sesión de agente en este repositorio), por indicación del
propietario, que es quien creó y custodia `pgpass.conf`; la contraseña nunca pasó por el chat ni se
imprimió. El ensayo corrió en el equipo del propietario y el clúster desechable se detuvo y eliminó
al terminar.

**Qué prueba y qué no.** Prueba que el volcado contiene los objetos de F1 (tablas, datos, funciones,
políticas, triggers, índices, enums, privilegios) y que se reconstruyen idénticos en un PostgreSQL
vacío una vez existen los prerrequisitos. **No prueba** una restauración completa en otro proyecto
Supabase: no se restauraron `auth` ni `storage` reales (quedaron fuera **8 triggers de otros
esquemas y 33 entradas** del índice), no se restauraron extensiones ni roles del proveedor, y no hay
segundo proyecto donde ensayarlo (DEC-07 ya está decidida; **O-03 sigue abierta** por esta prueba).

---

## 5. Verificación de una restauración (criterio de aceptación)

Un respaldo solo cuenta como recuperable si, tras restaurarlo:

1. El esquema conserva las **5 tablas**, el esquema `app`, las 5 RPC y las **6 políticas**.
2. `relrowsecurity` y `relforcerowsecurity` son `true` en las 5 tablas.
3. Los conteos de filas coinciden con el origen **y** los `md5` de cuerpos de funciones y
   expresiones de políticas son iguales.
4. Las 127 comprobaciones SQL (`supabase/tests/`) siguen en verde sobre la base restaurada.
5. Queda registrado: fecha, tamaño, hash, versión de `pg_dump`, y quién ejecutó la prueba.

En el ensayo del 26/10/2026 se cumplen 1–5 **para `public` + `app` en un PostgreSQL local**. Falta lo
que de verdad cierra O-03: restaurar el volcado en un proyecto Supabase real y comparar contra el
origen. Hasta entonces **no se declara un respaldo recuperable** y así debe informarse.

---

## 6. Pendiente (DEC-07 ya decidida; ejecución pendiente)

| Punto | Estado |
|---|---|
| RPO y RTO | **Decidido** (DEC-07, 13/11/2026): RPO 24 h, RTO 8 h en horario laboral |
| Frecuencia y retención | **Decidido** (DEC-07): volcado diario, retención 30 días |
| Destino fuera del proveedor | **Decidido** (DEC-07): almacenamiento cifrado fuera del proveedor, sin coste; el destino concreto no está elegido |
| Responsable de ejecutar y verificar | **Decidido** (DEC-07): el propietario |
| Primer volcado real | **Hecho** el 26/10/2026 (§4.2): 416.995 bytes, SHA256 `970E7242…` |
| Volcado de roles (§3.2) | **No ejecutado**; el directorio solo contiene `volterra.dump` |
| Automatizar el volcado | No hecho; hoy es manual y no hay programación |
| Restauración sobre proyecto Supabase | No probada: no existe un segundo proyecto autorizado |
| Ensayo en PostgreSQL local | **Hecho** (§4.2), con `auth` simulado; cobertura parcial y declarada |

Tener `pgpass.conf` **no** autoriza gastos ni despliegues: solo permite ejecutar los comandos
anteriores contra la base ya existente. La credencial la creó y la custodia el propietario; su
contenido no se ha leído ni se ha volcado en ningún documento.

---
---

## 4.3 Ruta para restauración en un proyecto Supabase real (cuando exista autorización)

**Pre-requisitos**
- Segundo proyecto Supabase **existente y autorizado**, sin gasto nuevo.
- Credencial válida para ese proyecto (gestión fuera del chat).
- Binarios `pg_dump`/`pg_restore` 17.6 ya disponibles (`C:\Users\Miguel\Tools\pgsql-17.6\pgsql\bin`).
- Volcado verificado: `workspace/backups/volterra-20261026-211832/volterra.dump` (SHA256 `970E72423E5F7AEF72096ED02C1B953D44EF41A5908D13711653D26375F9F279`, 416.995 bytes, 666 entradas).

**Pasos (orientativos, ejecutar solo con permiso explícito)**
1. Comprobar conectividad por **pooler en modo sesión** (5432). `6543` (modo transacción) no es válido para `pg_dump`.
2. Restaurar con cuidado: un volcado completo incluye `auth`, `storage`, `extensions`, `realtime`, etc., que son gestionados por Supabase. Priorizar restauración selectiva o seguir el procedimiento acordado con el propietario.
3. Verificar objetos críticos: 5 tablas, esquema `app`, 5 RPC, **6 políticas**, `relrowsecurity`/`relforcerowsecurity` en las 5 tablas, enums, triggers, índices, privilegios.
4. Ejecutar las 3 suites con `psql -v ON_ERROR_STOP=1`:
   - `supabase/tests/f1_rls_isolation.test.sql` (65)
   - `supabase/tests/f1_hardening.test.sql` (37)
   - `supabase/tests/f1_service_role.test.sql` (25) → **127/127**
5. Registrar todo en este documento: fecha/hora, tamaño, SHA256, versión `pg_dump`, exit codes de `pg_restore` y `psql`, conteos/md5 comparados con origen, resultado de pruebas, quién ejecutó.

**Advertencia:** Restaurar un volcado completo puede chocar con objetos administrados por Supabase. El camino más seguro es el ensayo selectivo y documentar desviaciones. **Hasta completar 1–5 no se declara el respaldo como recuperable.**

Reproduce las construcciones de F1 sin las dependencias de Supabase (`auth`). Los roles se crean
locales y desechables.

```sql
create role anon nologin;
create role authenticated nologin;
create role service_role nologin bypassrls;

create schema app;
create type public.club_status as enum ('active','inactive');

create table public.clubs (
  id uuid primary key default gen_random_uuid(),
  name text not null check (length(btrim(name)) between 3 and 120),
  status public.club_status not null default 'active',
  created_at timestamptz not null default now(),
  created_by uuid not null
);
create index clubs_name_idx on public.clubs (name);

create table public.audit_events (
  id bigserial primary key,
  entity text not null,
  entity_id text,
  action text not null,
  at timestamptz not null default now()
);

create function app.current_user() returns uuid
language sql stable set search_path = ''
as $$ select nullif(current_setting('request.jwt.claims', true)::json->>'sub','')::uuid $$;

create function app.is_member(p_club uuid) returns boolean
language sql stable security definer set search_path = ''
as $$ select exists (select 1 from public.clubs c where c.id = p_club and app.current_user() is not null) $$;

create function app.audit_row_change() returns trigger
language plpgsql security definer set search_path = ''
as $$
begin
  insert into public.audit_events (entity, entity_id, action)
  values (tg_table_name, coalesce(new.id::text, old.id::text), lower(tg_op));
  return null;
end $$;

create trigger trg_audit_clubs after insert or update or delete on public.clubs
for each row execute function app.audit_row_change();

alter table public.clubs enable row level security;
alter table public.clubs force row level security;
create policy clubs_select on public.clubs for select to authenticated using (app.is_member(id));

revoke all on public.clubs from anon;
grant select on public.clubs to authenticated;
comment on table public.clubs is 'Club ficticio de prueba de tuberia';

insert into public.clubs (name, created_by) values
  ('Club Alfa', gen_random_uuid()),
  ('Club Beta', gen_random_uuid()),
  ('Club Gamma', gen_random_uuid());
```
