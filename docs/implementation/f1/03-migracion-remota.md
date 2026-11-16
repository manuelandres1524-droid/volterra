# F1 — Aplicar la migración remota pendiente (vía SQL Editor)

**Fecha:** 12/11/2026
**Estado:** **ejecutado** contra el proyecto `tioeoswnhwrlbovkxocd` el 12/11/2026.
**Ejecutor:** agente de desarrollo, con aprobación explícita del propietario.
**Motivo:** sin `public.fn_is_platform_admin()`, cualquier petición autenticada del BFF
terminaba en `503`.

> Este documento no autoriza nada por sí mismo: describe cómo ejecutar la migración que el
> propietario ya decidió aplicar. No crea proyectos, no cambia de plan y no usa datos reales.

---

## 0. Contexto verificado el 12/11/2026

| Dato | Valor | Cómo se comprobó |
|---|---|---|
| Proyecto | `tioeoswnhwrlbovkxocd` | Indicado por el propietario |
| API | `https://tioeoswnhwrlbovkxocd.supabase.co` | `/auth/v1/health` → `401 No API key found` (esperado sin `apikey`) |
| Pooler IPv4 | `aws-1-us-east-2.pooler.supabase.com:5432` | `psql` llega a autenticación; los demás poolers responden `tenant/user not found` |
| Conexión directa | `db.tioeoswnhwrlbovkxocd.supabase.co` | Solo publica IPv6; no alcanzable desde el entorno del agente |
| Proyecto anterior | `taevpaknhuoyiujqgjku` | **NXDOMAIN** en el resolver local y en Google DNS |

**Discrepancia abierta:** el pooler y el prefijo IPv6 apuntan a `us-east-2`, mientras
`00-autorizacion-y-alcance.md` fija `us-east-1`. La región es materia de DEC-19/E-6 y **no se
considera aprobada** por este documento.

---

## 1. Paso 0 — Preflight (solo lectura)

En Supabase → **SQL Editor**, ejecuta el contenido completo de:

```
supabase/tests/preflight_remote_state.sql
```

No crea objetos ni escribe filas. Devuelve dos resultados: un JSON `preflight` y la lista de
migraciones registradas.

### Interpretación

| Resultado | Significado | Acción |
|---|---|---|
| `hay_esquema_app: true`, las 5 tablas con número de filas, `hay_fn_is_platform_admin: false`, `migraciones_registradas: 6` | Es el estado esperado: F1 aplicada, falta la migración 7. | Continúa al paso 2. |
| `hay_fn_is_platform_admin: true` | La migración ya estaba aplicada. | No la repitas; pasa al paso 4. |
| `hay_esquema_app: false` o tablas `"tabla ausente"` | El proyecto no tiene F1: es un proyecto vacío o distinto. | **Detente.** Aplicar solo la migración 7 fallaría: depende de `app.is_platform_admin()`. Hay que aplicar la secuencia 1→7, y eso es una acción de mayor alcance que requiere aprobación explícita. |
| `migraciones_registradas` distinto de 6 con el esquema presente | El historial no coincide con lo documentado. | **Detente** y registra el JSON antes de tocar nada. |

Guarda el JSON del preflight: es la evidencia «antes».

---

## 2. Paso 1 — Aplicar la migración

Pega y ejecuta el contenido completo de:

```
supabase/migrations/20261102120000_f1_is_platform_admin.sql
```

Es idempotente: usa `create or replace`, `revoke` y `grant`. Volver a ejecutarla no rompe nada.

Qué hace, en una frase: crea `public.fn_is_platform_admin()` como `SECURITY DEFINER` con
`search_path = ''`, que devuelve solo un booleano y delega en `app.is_platform_admin()`;
concede `EXECUTE` únicamente a `authenticated`.

No abre `platform_admins`, no cambia políticas RLS y no modifica datos.

---

## 3. Paso 2 — Preflight posterior

Vuelve a ejecutar `supabase/tests/preflight_remote_state.sql`.

Debe aparecer `"hay_fn_is_platform_admin": true` y el resto igual que antes. Si el resto cambió,
detente y regístralo.

---

## 4. Paso 3 — Suite de la RPC (7 comprobaciones)

Ejecuta el contenido completo de:

```
supabase/tests/f1_platform_admin_rpc.test.sql
```

Termina en `ROLLBACK`: crea fixtures ficticios y no deja residuos. Devuelve un único JSON
`results`. Valores esperados:

```json
{
  "authenticated_puede_ejecutar": true,
  "anon_no_puede_ejecutar": true,
  "platform_admins_sigue_cerrada": true,
  "pa_es_platform_admin": true,
  "coach_no_es_platform_admin": true,
  "sin_claims_no_es_platform_admin": true,
  "anon_ejecuta": "42501"
}
```

Cualquier otro valor es un fallo: no lo interpretes como éxito parcial.

---

## 5. Paso 4 — Registrar la versión (opcional)

El SQL Editor no escribe en el historial de migraciones de Supabase. Si quieres que
`supabase_migrations.schema_migrations` refleje la migración 7:

```sql
insert into supabase_migrations.schema_migrations (version, name)
values ('20261102120000', 'f1_is_platform_admin')
on conflict (version) do nothing;
```

Es una escritura en una tabla de control. Si prefieres no tocarla, la migración sigue aplicada
igual; solo el historial queda sin esa fila.

---

## 6. Reversión

Si algo sale mal, la migración se deshace con:

```sql
drop function if exists public.fn_is_platform_admin();
```

El BFF volvería a `503` con token válido, que es el estado anterior. No hay datos que restaurar:
la migración no escribe filas.

---

## 7. Después de aplicarla

1. Crear `volterra/.env` a partir de `.env.example` con `SUPABASE_URL` y `SUPABASE_ANON_KEY`
   del proyecto nuevo. La clave `anon` la pone el propietario; no se pega en el chat.
2. Arrancar el BFF y comprobar que `/api/v1/me/` responde `200` y no `503`.
3. Seguir `02-demo-local.md` para el recorrido del frontend.

## 8. Evidencia local de este procedimiento

El 12/11/2026 se reprodujo la secuencia completa en un PostgreSQL 16.15 desechable, con `auth`
simulado y las seis migraciones previas:

| Comprobación | Resultado |
|---|---|
| Preflight con 6 migraciones | `hay_esquema_app: true`, `hay_fn_is_platform_admin: false`, `migraciones_registradas: 6` |
| Aplicar migración 7 | sin errores |
| Preflight posterior | `hay_fn_is_platform_admin: true` |
| `f1_platform_admin_rpc.test.sql` | 7/7, `anon_ejecuta: 42501` |

Esto valida el SQL y el orden de los pasos; **no sustituye** la ejecución contra el proyecto
real.

---

## 9. Ejecución real (12/11/2026)

El preflight contra `tioeoswnhwrlbovkxocd` devolvió un proyecto **vacío**, no el estado
esperado:

```json
{"hay_esquema_app": false, "hay_app_is_platform_admin": false,
 "hay_fn_is_platform_admin": false, "migraciones_registradas": "sin tabla",
 "filas_clubs": "tabla ausente", "filas_profiles": "tabla ausente",
 "filas_platform_admins": "tabla ausente", "filas_club_memberships": "tabla ausente",
 "filas_audit_events": "tabla ausente", "rol": "postgres", "version_pg": "17.11"}
```

Comprobación adicional: `public` sin tablas, `auth.users` con 0 filas, extensiones `pgcrypto`,
`uuid-ossp`, `supabase_vault` y `pg_stat_statements`, `postgres` sin `superuser`.

Según el árbol de decisión de §1, eso obligaba a aplicar la secuencia 1→7, que es una acción
de mayor alcance. **El propietario la aprobó explícitamente** («Aplica F1 completo (1→7)»).

### 9.1 Aplicación

```bash
# 1. Concatenar las 7 migraciones dentro de una transacción
{ echo 'begin;'; for f in $(ls supabase/migrations/*.sql | sort); do
    echo; echo "-- >>> $f"; cat "$f"; done; echo; echo 'commit;'; } > /tmp/opencode/f1_all.sql

# 2. Aplicar con ON_ERROR_STOP: cualquier error revierte todo
psql -w -X -q -v ON_ERROR_STOP=1 \
  "host=aws-1-us-east-2.pooler.supabase.com port=5432 dbname=postgres \
   user=postgres.tioeoswnhwrlbovkxocd sslmode=require" \
  -f /tmp/opencode/f1_all.sql
```

Resultado: **exit 0**, solo `NOTICE ... does not exist, skipping` de los `drop ... if exists`.

### 9.2 Verificación estructural

| Comprobación | Resultado |
|---|---|
| Tablas en `public` | `audit_events, club_memberships, clubs, platform_admins, profiles` |
| RLS | `enable=true, force=true` en las 5 |
| Políticas | 6 |
| Funciones `public.fn_*` | 6 (`add_member`, `change_member_role`, `create_club`, `end_membership`, `is_platform_admin`, `update_club`) |
| `app.is_platform_admin()` | presente |
| `fn_is_platform_admin` | ejecutable por `authenticated`, no por `anon` |
| Filas | 0 en las 5 tablas |

### 9.3 Suites en remoto

| Suite | Comprobaciones | Resultado |
|---|---:|---:|
| `f1_rls_isolation` | 65 | 65/65 |
| `f1_hardening` | 37 | 37/37 |
| `f1_service_role` | 25 | 25/25 |
| `f1_platform_admin_rpc` | 7 | 7/7 |
| **Total** | **134** | **134/134** |

Comparación clave por clave del JSON de cada suite contra los valores esperados del archivo:
0 faltantes, 0 sobrantes, 0 distintos. Todas terminan en `ROLLBACK`; en ese momento
`auth.users` seguía con 0 filas (los usuarios ficticios se crearon después, §9.5).

### 9.4 Historial de migraciones

`supabase_migrations.schema_migrations` **no existe** en el proyecto: las migraciones se
aplicaron con `psql`, no con el CLI. El esquema está aplicado y verificado, pero el CLI no lo
sabe. Decisión pendiente: registrarlo (§5) o reconstruir el proyecto con `supabase db push`
desde cero. No se hizo ninguna de las dos.

### 9.5 Usuarios y datos ficticios

Con autorización del propietario se crearon dos usuarios de Auth por SQL (correo confirmado,
contraseña ficticia con `extensions.crypt`, fila en `auth.identities`) y se ejecutó
`supabase/seed/f1_demo.sql`. Resultado:

| Comprobación | Resultado |
|---|---|
| `auth.users` | 2 (`demo-pa@example.com`, `demo-coach@example.com`) |
| Perfiles / clubes / pertenencias / platform_admins | 2 / 1 / 2 / 1 |
| Eventos de auditoría | 6 |
| `demo-pa` con `authenticated` | `fn_is_platform_admin() = true`, ve 1 club, 2 pertenencias, 2 perfiles |
| `demo-coach` con `authenticated` | `fn_is_platform_admin() = false`, ve 1 club, 1 pertenencia (la suya), 1 perfil |
| `anon` llamando a la RPC | `42501 permission denied for function` |

No se usaron datos reales. La contraseña ficticia no se guarda en el repositorio; se comunica
fuera de él y puede restablecerse desde el panel.

### 9.6 BFF y flujo autenticado (cerrado el 12/11/2026)

Con `volterra/.env` apuntando al proyecto nuevo, `COOKIE_SECURE=false` y la **legacy anon key**
(`eyJ…`, rol `anon`, `ref=tioeoswnhwrlbovkxocd`) el BFF arrancó en `127.0.0.1:8011` y el flujo
completo funcionó contra el Supabase real.

**Clave de Auth.** La `sb_publishable_…` **no sirve para el login** en este proyecto: PostgREST la
acepta (devuelve `42501` como `anon`), pero GoTrue v2.197.0 la rechaza en `/auth/v1/token` con
`401 Invalid API key` (probado con `apikey`, query param y `Bearer`). Se usó la legacy anon key.

| Prueba | Resultado |
|---|---|
| `POST /auth/v1/token?grant_type=password` (GoTrue) | `200`, `access_token` + `refresh_token` |
| `POST /auth/v1/token` con `sb_publishable_…` | `401 Invalid API key` (no usable para login) |
| JWT emitido | `role=authenticated`, `aud=authenticated`, `iss=https://tioeoswnhwrlbovkxocd.supabase.co/auth/v1` |
| JWKS | `200`, 1 clave ES256/EC con `kid` |
| `rpc/fn_is_platform_admin` con el token | `200` → `true` para `demo-pa` |
| `pytest` del BFF | **76 passed, 1 warning** |

**Recorrido E2E del frontend** (`httpx` contra `127.0.0.1:8011`, 37 comprobaciones, todas OK):

| Bloque | Comprobado |
|---|---|
| Sin sesión | `/me`, `/clubs`, `/platform` → `303` a `/login?next_url=…` |
| CSRF | `POST /login` con token inválido → `403` |
| Login `demo-pa` | `303` a `/me`; cookies `volterra_access`/`volterra_refresh` `HttpOnly`; cookie CSRF legible |
| `/me` | `200`, muestra `Club Demo Volterra`, `Demo Platform Admin` y el ámbito de plataforma |
| `/clubs` y `/clubs/{id}` | `200`, club y ciudad `Bogota` |
| `/clubs/{id}/members` | `200`, incluye al coach y al admin |
| `/platform` | `200` para `demo-pa` |
| `POST /auth/refresh` | `403` sin CSRF; `204` con CSRF; **rota** el access token; `/me` sigue en `200` |
| Club ajeno | `404` |
| Logout | `303` a `/login`; `/me` vuelve a `303` |
| `demo-coach` | login OK; `/me` sin ámbito de plataforma; en miembros **no** ve al admin; `/platform` → `403` |

**`scripts/smoke_f1.py`** (contra el BFF): `POST /auth/v1/token → 200`, `/api/v1/me/ → 200`,
`/api/v1/clubs/me → 200`, `/api/v1/clubs/{id} → 200`, `/api/v1/clubs/{id}/members → 200`,
`/api/v1/platform/overview → 200`, **SMOKE OK**.

**Nota de entorno.** El runtime de esta sesión (`LD_PRELOAD=/opt/qroot/lib/libqroot-runtime.so`)
aborta procesos con `free(): invalid pointer`: afecta a `curl`, a `git clone` y, de forma
intermitente, a `uvicorn`. Por eso las pruebas se hicieron con un supervisor que relanza el
servidor y con reintentos en el cliente; en la tanda final hubo **0 reinicios y 0 reintentos**.
No es un defecto del BFF.

### 9.7 Escrituras de F1 (cerrado el 13/11/2026)

Se añadieron endpoints API y formularios HTML para las cinco RPC de escritura que ya existían en
el esquema. **No hay migración nueva**: `fn_create_club`, `fn_update_club`, `fn_add_member`,
`fn_change_member_role` y `fn_end_membership` estaban aplicadas desde el 12/11/2026.

| Capa | Cambio |
|---|---|
| Servicio | `volterra/apps/services/f1_writes.py`: envuelve las RPC y traduce SQLSTATE → HTTP |
| API JSON | `POST /api/v1/clubs`, `PATCH /api/v1/clubs/{id}`, `POST/PATCH/DELETE` de miembros |
| Web | `/clubs/new`, `POST /clubs`, `/clubs/{id}/edit`, alta/cambio/cierre de miembros |
| CSRF | `require_csrf_if_cookie` en la API; campo oculto en formularios; `Bearer` exento |
| Plantillas | `club_form.html` nuevo; `members.html`, `club_detail.html` y `clubs.html` actualizados |

**Pruebas del BFF:** `pytest` **109 passed, 1 warning** (76 previas + 33 nuevas de escrituras).
Las nuevas cubren el mapeo de errores, el CSRF por cookie, el orden de dependencias, la validación
de UUID/país/rol, el 404 de una pertenencia de otro club y las negativas por rol.

**E2E real** (`scripts/e2e_f1_writes.py` contra `127.0.0.1:8011` y el Supabase del proyecto,
usuarios ficticios, **45/45 OK**):

| Bloque | Comprobado |
|---|---|
| Login | PA y coach por formulario; cookies `HttpOnly`; CSRF rotado |
| Negativas | `POST /clubs` sin CSRF → `403`; coach en `/clubs/new` → `403` |
| Club | alta → `303`; detalle; edición de nombre/ciudad/estado → `303` |
| Miembros | alta de coach y de PA como admin; lista con `Demo Coach` |
| Rol | coach → `club_admin` → coach, con nueva pertenencia en cada cambio |
| Cierre | se cierra la pertenencia del coach; deja de figurar |
| Invariante | cerrar al **último** admin → `400` con mensaje de administrador |
| Aislamiento | el coach sin pertenencia vigente no ve los miembros del club |

**Residuo declarado:** el E2E deja **un club ficticio** (`Club E2E <marca de tiempo>`) con el PA
como administrador y la pertenencia del coach cerrada. F1 no tiene borrado y no se elimina nada sin
aprobación explícita. El club del seed (`c4000000-…-000a`) no se modificó.

**Alcance:** local, datos ficticios, sin despliegue. La autorización efectiva sigue en RLS + RPC;
el BFF no reimplementa reglas de dominio.
