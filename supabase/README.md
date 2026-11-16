# Base de datos de VOLTERRA — F1

**Estado:** migraciones aplicadas en el proyecto Supabase de desarrollo · **Fecha:** 26/10/2026
**Alcance:** F1 «Perfiles de club y usuarios». No incluye F2, F3 ni F7. Sin datos reales.

> **Actualización del 12/11/2026 — el proyecto cambió.** El propietario indicó el proyecto
> `tioeoswnhwrlbovkxocd`. El host del proyecto anterior (`taevpaknhuoyiujqgjku.supabase.co`) ya
> **no existe en DNS** (NXDOMAIN verificado con el resolver local y con Google DNS). El pooler
> IPv4 del proyecto nuevo es `aws-1-us-east-2.pooler.supabase.com:5432`; la conexión directa
> `db.tioeoswnhwrlbovkxocd.supabase.co` solo publica IPv6. Las tablas y cifras de §2 son del
> proyecto anterior y **no se han vuelto a verificar** en el nuevo. La región aparente es
> `us-east-2`, no `us-east-1`; sigue siendo materia de DEC-19/E-6 y **no se considera aprobada**.
>
> **Actualización posterior (12/11/2026) — F1 aplicada en el proyecto nuevo.** El preflight
> confirmó que `tioeoswnhwrlbovkxocd` estaba **vacío** (`hay_esquema_app: false`, sin
> `supabase_migrations`, `public` sin tablas, `auth.users` con 0 filas). Con aprobación explícita
> del propietario se aplicaron las **siete migraciones en una sola transacción**
> (`ON_ERROR_STOP=1`, exit 0). Verificación estructural: 5 tablas, RLS `enable`+`force` en las 5,
> 6 políticas, 6 funciones `public.fn_*`, `app.is_platform_admin()` presente, y **0 filas** en las
> 5 tablas. Las cuatro suites se ejecutaron contra el proyecto real: **134/134**. No se insertaron
> usuarios ni datos. El historial `supabase_migrations` sigue vacío (ver §8).
>
> Después se crearon dos usuarios ficticios de Auth y se ejecutó `supabase/seed/f1_demo.sql`:
> 2 perfiles, 1 `platform_admin`, 1 club, 2 pertenencias y 6 eventos de auditoría. Verificado con
> RLS: `demo-pa` es platform_admin y ve 2 pertenencias; `demo-coach` no lo es y solo ve la suya;
> `anon` recibe `42501` al llamar a la RPC.
>
> **BFF verificado (12/11/2026).** Con la legacy anon key, el frontend Jinja2+HTMX funcionó de
> extremo a extremo contra este proyecto: login, `/me`, `/clubs`, miembros, `/platform`, refresh
> con rotación y logout (**37/37** comprobaciones) y `scripts/smoke_f1.py` → **SMOKE OK**. La
> `sb_publishable_…` **no** sirve para el login: PostgREST la acepta, GoTrue v2.197.0 la rechaza
> con `401 Invalid API key`. Detalle: `docs/implementation/f1/03-migracion-remota.md` §9.6.


> Este directorio contiene el esquema versionado. La base remota se modificó con
> `apply_migration` del MCP de Supabase, ejecutando como rol `postgres`. Cada
> archivo reproduce las sentencias aplicadas; cinco de los seis son idénticos
> byte a byte al texto guardado en `supabase_migrations.schema_migrations`
> (md5 verificado). El cuarto (`f1_default_deny`) se aplicó sin los comentarios
> explicativos: sus sentencias ejecutables son las mismas.

---

## 1. Entorno

| Dato | Valor |
|---|---|
| Proyecto | `tioeoswnhwrlbovkxocd` (indicado por el propietario el 12/11/2026; el anterior era `taevpaknhuoyiujqgjku`, ya sin DNS) |
| Región | `us-east-2` aparente, según el pooler IPv4 y el prefijo IPv6 del proyecto nuevo. **No** evaluada jurídicamente; DEC-19/E-6 sigue abierta |
| Uso | Desarrollo no productivo, solo datos ficticios |
| Coste | Plan gratuito; sin backups automáticos ni PITR |
| Rol de migración | `postgres` (no superusuario, miembro de `anon`/`authenticated`/`service_role`) |

Ver `docs/implementation/f1/00-autorizacion-y-alcance.md` para los límites de esa autorización.

---

## 2. Migraciones aplicadas

| Versión | Nombre | md5 del texto aplicado | Contenido |
|---|---|---|---|
| `20261026025315` | `f1_clubs_users_core` | `6a68e8ec3723b65ce112892e8b3c521b` | Tipos, 5 tablas, índices |
| `20261026025346` | `f1_rls_isolation` | `4bcfd1ed61c92bcb40c2a59fa46c096e` | Esquema `app`, 5 helpers, RLS, políticas, `REVOKE` |
| `20261026025413` | `f1_mutations_and_audit` | `647f394c5cdba5e1b61f0dd0e9fb82cd` | 4 RPC, guardas, triggers de auditoría |
| `20261026032936` | `f1_default_deny` | `cfbfe0f355e0c9ae5bb4ce7dffe33264` | Privilegios por defecto y barrido de funciones |
| `20261026035037` | `f1_update_club_profile` | `3d927542ef1ce0b96bcc9031b0f5644c` | RPC `fn_update_club` (solo plataforma) |
| `20261026040817` | `f1_hardening` | `4b65da67e3633503dae420f872cec06b` | Corrección de los defectos D1–D4 de la revisión de seguridad |

### Migración 7: aplicada el 12/11/2026

| Versión | Nombre | Contenido | Estado |
|---|---|---|---|
| `20261102120000` | `f1_is_platform_admin` | RPC `public.fn_is_platform_admin()`: solo booleano, `SECURITY DEFINER`, sin abrir `platform_admins`. | **Aplicada** al proyecto `tioeoswnhwrlbovkxocd` (junto con 1→6, en una transacción) |

> Esta migración responde al desajuste entre el backend y el diseño de la base: el backend
> consultaba `platform_admins` por PostgREST y recibía `42501`, lo que convertía toda petición
> autenticada en un `503`. Ver `docs/implementation/f1/01-platform-admin-rpc.md`.
>
> El proyecto nuevo estaba vacío, así que no bastó la migración 7: se aplicó la secuencia
> completa 1→7 con `psql` sobre el pooler IPv4. Ver
> `docs/implementation/f1/03-migracion-remota.md` y la nota de la cabecera.

Estado verificado en el proyecto nuevo (12/11/2026, antes del seed): 5 tablas, RLS
`enable`+`force` en las 5, 6 políticas, 6 funciones `public.fn_*`, `app.is_platform_admin()`
presente, 0 filas en las 5 tablas. Después se crearon 2 usuarios ficticios y se sembraron
2 perfiles, 1 club, 2 pertenencias, 1 `platform_admin` y 6 eventos de auditoría.

### Modelo en una línea

`clubs` (unidad de aislamiento) ← `club_memberships` (rol + vigencia + historial) → `profiles`
(identidad global, sin club, sin rol). `platform_admins` es un ámbito aparte, sin `club_id`,
excepción explícita a A-01. `audit_events` es append-only.

### Decisiones de diseño ya aplicadas

- El rol **no** vive en `profiles`: vive en la pertenencia, con `ended_at`. Cambiar rol cierra
  la fila y abre otra (historial), no sobrescribe.
- Una sola pertenencia vigente por `(club_id, user_id)` (índice único parcial).
- Ninguna tabla acepta `INSERT`/`UPDATE`/`DELETE` directo de `authenticated`: toda escritura
  pasa por RPC `SECURITY DEFINER` con guardas y auditoría.
- `profiles` es la única tabla con escritura directa, y solo por columna: el titular puede
  insertar `(id, display_name)` y actualizar `display_name`; no puede tocar `created_at`,
  `updated_at` ni el `id`. Los cambios de perfil se auditan sin copiar el dato.
- Un `club_admin` solo gestiona `coach`; no puede crear ni degradar administradores.
- Solo `platform_admin` edita el perfil del club (`fn_update_club`): un `club_admin` gestiona
  entrenadores, no la identidad del club. Criterio provisional, el más restrictivo compatible
  con la matriz de DEC-03.
- Un club no puede quedarse sin administrador activo (`23514`). La comprobación se serializa
  bloqueando la fila del club (`for update`) antes de contar; `fn_end_membership` y
  `fn_change_member_role` esperan ese bloqueo, así que dos cierres simultáneos no pueden dejar
  el club sin administrador.
- Un `club_admin` ve las pertenencias **vigentes** de su club y la suya propia; el historial de
  exmiembros queda para `platform_admin` y para el titular de cada fila.
- La auditoría de un club (`clubs`) se registra con el `club_id` del propio club, no en `NULL`.
- `platform_admins` no tiene políticas ni `GRANT` para `authenticated`/`anon`: inaccesible por API
  con JWT de usuario. **Con la clave `service_role` sí es legible** (`BYPASSRLS` + `GRANT`): ver §5.

---

## 3. Pruebas

```
supabase/tests/f1_rls_isolation.test.sql        -- 65 comprobaciones
supabase/tests/f1_hardening.test.sql            -- 37 comprobaciones
supabase/tests/f1_service_role.test.sql         -- 25 comprobaciones (hipótesis de DEC-12)
supabase/tests/f1_platform_admin_rpc.test.sql   -- 7 comprobaciones
```

**Suite de la RPC:** `f1_platform_admin_rpc.test.sql` verifica
`public.fn_is_platform_admin()` y que `platform_admins` siga cerrada. Validada localmente
(7/7) y **ejecutada contra el proyecto remoto el 12/11/2026** (7/7, `anon_ejecuta: 42501`).

**Validación local (02/11/2026):** en un contenedor PostgreSQL 17.11 con `auth` y roles
simulados se ejecutaron las cuatro suites: 65/65 + 37/37 + 25/25 + 7/7 = **134/134**. La
suite `f1_service_role` cuenta las cinco RPC de F1 por nombre para no romperse al añadir
RPC nuevas. Esta validación **no sustituye** la ejecución en el proyecto Supabase: no
reproduce sus roles, ACL ni esquemas administrados.

**Revalidación local (12/11/2026):** repetida tras el endurecimiento del BFF (sin cambios en
SQL) sobre **PostgreSQL 16.15** desechable, con `auth.users`, `auth.uid()`, `anon`,
`authenticated`, `service_role` y `supabase_admin` simulados, aplicando las **siete**
migraciones en orden. Resultado: 65/65 + 37/37 + 25/25 + 7/7 = **134/134**, comparando el
JSON de resultados contra los valores esperados de cada suite.

**Resultado real en el proyecto remoto (12/11/2026, `tioeoswnhwrlbovkxocd`):**

| Suite | Comprobaciones | Conformes | Residuos |
|---|---:|---:|---:|
| `f1_rls_isolation` | 65 | 65 | 0 |
| `f1_hardening` | 37 | 37 | 0 |
| `f1_service_role` | 25 | 25 | 0 |
| `f1_platform_admin_rpc` | 7 | 7 | 0 |
| **Total** | **134** | **134** | **0** |

Las cuatro suites terminaron con `exit 0` y sus JSON se compararon clave por clave contra los
valores esperados de cada archivo: 0 faltantes, 0 sobrantes, 0 distintos. Las suites terminan
en `ROLLBACK`, así que no dejaron fixtures. En ese momento `auth.users` tenía **0 filas**; los
dos usuarios ficticios se crearon después (§9.5 de `03-migracion-remota.md`).

Cada archivo se envía como una sola consulta. Crean fixtures ficticios (`@example.com`),
impersonan a cada rol con `set local role` + `request.jwt.claims` (el mecanismo que lee
`auth.uid()`) y terminan en `ROLLBACK`: no dejan usuarios, filas ni eventos.

**Revalidación en el proyecto remoto (16/11/2026, `tioeoswnhwrlbovkxocd`):**

| Suite | Comprobaciones | Conformes | Residuos |
|---|---:|---:|---:|
| `f1_rls_isolation` | 65 | 65 | 0 |
| `f1_hardening` | 37 | 37 | 0 |
| `f1_service_role` | 25 | 25 | 0 |
| `f1_platform_admin_rpc` | 7 | 7 | 0 |
| **Total** | **134** | **134** | **0** |

La base ya no estaba vacía: 2 clubes, 2 perfiles, 6 pertenencias y 2 usuarios ficticios
(usuarios demo y clubes del E2E de escrituras). La primera pasada dio **128/134**: las seis
discrepancias eran conteos absolutos que incluían esas filas preexistentes, no fallos de
control. Para que las suites sigan siendo comprobables sobre una base con datos, los conteos
afectados se expresan ahora como **delta sobre un baseline** capturado al inicio de la
transacción (`f1.base_*`, `f1h.base_profiles_audit`, `f1svc.base_*`). Con ese cambio:
**134/134**, 0 residuos y las cuatro terminaron en `ROLLBACK`. Los valores esperados de cada
suite no cambian: en una base vacía el delta coincide con el conteo absoluto anterior.

> Criterio para suites futuras: medir el delta de los fixtures propios, no el total de la
> tabla. Un conteo absoluto falla en cuanto la base tiene datos legítimos y oculta el fallo
> real entre discrepancias de baseline.

**Resultado real (26/10/2026), sobre la base con las seis migraciones aplicadas:**

| Suite | Comprobaciones | Conformes | Residuos |
|---|---|---|---|
| `f1_rls_isolation` | 65 (56 de núcleo + 9 de perfil de club) | 65 | 0 |
| `f1_hardening` | 37 | 37 | 0 |
| `f1_service_role` | 25 | 25 | 0 |

Total: **127 comprobaciones, 127 conformes**. La verificación final se hizo comparando en SQL
el objeto de resultados contra el mapa de valores esperados: 65/65 claves iguales, 0 faltantes,
0 sobrantes. La suite de aislamiento se re-ejecutó **después** de la migración de
endurecimiento, porque esta cambia la política de pertenencias, los privilegios de `profiles`
y los triggers de auditoría.

Dos expectativas iniciales eran erróneas y se corrigieron tras verificar la causa:
`W5` devuelve `42501` (la guarda de alcance de rol actúa antes que la de último administrador;
esa regla se prueba en `W11` con `23514`) y el conteo de eventos de `clubs` era 1, no 2.

Cubre la suite principal: aislamiento de lectura por club, `anon` sin acceso a tablas ni
funciones, escritura directa denegada, escalado de rol denegado, club ajeno denegado, último
administrador protegido, historial conservado, auditoría con actor y rol, perfiles ajenos
invisibles e inmutables, `audit_events` append-only incluso para el propietario.

Cubre la suite de endurecimiento: bloqueo por club antes de la guarda (estructural: la carrera
real necesita dos conexiones), privilegios por columna en `profiles` (5 comprobaciones),
auditoría de `profiles` sin datos personales, `club_id` correcto en la auditoría de clubes,
historial de exmiembros oculto a `club_admin` y visible a `platform_admin`, y negativa a
insertar o modificar `audit_events` desde el cliente.

Cubre la suite de `service_role` (25 comprobaciones, resultado real del 26/10/2026): confirma
las dos caras de la clave secreta. **Las 5 RPC deniegan con `28000`** cuando el JWT es de
`service_role` (no hay `sub`, `auth.uid()` es nulo), pero **las tablas no están protegidas**:
`service_role` tiene `BYPASSRLS` y `SELECT`/`INSERT` sobre las 5 tablas, incluida
`platform_admins`. En la prueba lee los 2 clubes y los 3 perfiles sin identidad, inserta un
club, renombra un club ajeno y actualiza `platform_admins`. Además, si la conexión fija
`request.jwt.claims` con el `sub` de otra persona, la RPC lo acepta y atribuye la creación a
ese usuario suplantado. Conclusión: **la clave `service_role` anula RLS y la autorización de
dominio; no puede usarse en ningún camino de usuario.**

---

## 4. Asesores de Supabase: hallazgos aceptados

| Asesor | Nivel | Estado | Motivo |
|---|---|---|---|
| `rls_enabled_no_policy` en `platform_admins` | INFO | **Intencional** | RLS activa y cero políticas = nadie la lee por PostgREST. El acceso es solo por funciones `SECURITY DEFINER`. |
| `authenticated_security_definer_function_executable` (×5) | WARN | **Intencional** | Son las 5 RPC de F1. Hacen su propia autorización (`assert_can_manage_role` / `is_platform_admin`) y auditan. Deben ser invocables por `authenticated`; lo que no deben es ser `INVOKER`. |

Ninguno de los dos se resuelve ocultando botones en la interfaz.

---

## 5. Riesgos residuales (no cerrados)

| Riesgo | Impacto | Mitigación actual |
|---|---|---|
| **La clave `service_role` anula RLS** (`BYPASSRLS` + `GRANT` en las 5 tablas, incluida `platform_admins`) y, si fija `request.jwt.claims`, suplanta a cualquier usuario | Un backend o script con esa clave puede leer y escribir todos los clubes sin pasar por las RPC | Regla de uso: **`service_role` nunca en un camino de usuario**, solo operaciones administrativas puntuales. Probado en `f1_service_role.test.sql`. Revocar sus privilegios sería una decisión de arquitectura, no tomada |
| **`platform_admins` no es legible por PostgREST** | El backend no puede resolver el ámbito de plataforma con una consulta directa | Sustituido por `public.fn_is_platform_admin()` (aplicada el 12/11/2026). La RPC devuelve solo un booleano y `platform_admins` sigue cerrada (`42501`) |
| **`supabase_admin` conserva privilegios por defecto** que conceden `arwdDxtm` a `anon`/`authenticated` en `public` | Una tabla creada por ese rol (herramientas internas de Supabase) nacería expuesta | `postgres` no tiene permiso para cambiarlos (`42501`). Regla: crear objetos solo con migraciones aplicadas como `postgres` y verificar privilegios después de cualquier cambio hecho desde el panel |
| **PostgreSQL concede `EXECUTE` a `PUBLIC` en cada función nueva**; `ALTER DEFAULT PRIVILEGES` no elimina esa concesión base | Una función nueva en `public` sería ejecutable por `anon` | Toda migración que cree funciones debe ejecutar `revoke all on function … from public, anon`. La suite lo comprueba (`anon_sin_funciones`) |
| Sin restauración probada contra un proyecto Supabase (O-03 / DEC-07) | Pérdida total ante un error | Solo datos ficticios. Primer volcado real ejecutado el 26/10/2026 (416.995 bytes) y **restauración de ensayo en local** con 127/127 pruebas en verde; restaurar en otro proyecto Supabase sigue sin probar: `docs/operations/o-03-respaldo-restauracion.md` §4.2 |
| Región `us-east-1` sin evaluación jurídica (E-6 / DEC-19) | Transferencia internacional sin calificar | Solo datos ficticios. No se afirma cumplimiento |
| Sin política de retención (E-4 / DEC-05) | Datos ficticios sin purga | Solo desactivación lógica (`ended_at`) |
| Sin nivel ASVS fijado (DEC-06) | Alcance de verificación indefinido | Se aplican controles de forma conservadora |
| **La carrera de D1 no se probó con dos conexiones simultáneas** | Una regresión futura podría reintroducir el cierre doble sin que la suite lo detecte | La suite comprueba la estructura (bloqueo antes de la guarda) y el rechazo `40001`. La prueba de carrera real requiere dos sesiones: pendiente |
| **El titular no ve la auditoría de su propio perfil** (la política solo admite `platform_admin` y `club_admin` del club) | Un usuario no puede consultar su propia traza de cambios | Denegación por defecto, no fuga. Depende de la decisión de acceso del titular, pendiente y no tomada |

---

## 6. Reversión

**No ejecutar sin autorización.** Con datos ficticios la reversión es aceptable; con datos
reales implicaría pérdida de información y quedaría bloqueada por O-03.

Orden inverso al de aplicación:

```sql
-- 6. f1_hardening
drop trigger if exists trg_audit_profiles on public.profiles;
drop function if exists app.audit_profile_change();
-- Volver a los privilegios de tabla de la migración 2. Solo tiene sentido si se
-- revierte también el endurecimiento; reabre la escritura de created_at.
revoke insert (id, display_name) on public.profiles from authenticated;
revoke update (display_name)      on public.profiles from authenticated;
grant  insert, update             on public.profiles to authenticated;

-- 5. f1_update_club_profile
drop function if exists public.fn_update_club(uuid, text, text, char, public.club_status);

-- 4. f1_default_deny: no se revierte. Volver a conceder privilegios por defecto
--    a anon/authenticated reabriría la exposición; no hay razón para hacerlo.

-- 3. f1_mutations_and_audit
drop trigger if exists trg_audit_clubs            on public.clubs;
drop trigger if exists trg_audit_memberships      on public.club_memberships;
drop trigger if exists trg_audit_platform_admins  on public.platform_admins;
drop trigger if exists trg_profiles_touch         on public.profiles;
drop trigger if exists trg_audit_append_only      on public.audit_events;
drop trigger if exists trg_audit_no_truncate      on public.audit_events;
drop function if exists public.fn_end_membership(uuid);
drop function if exists public.fn_change_member_role(uuid, public.club_role);
drop function if exists public.fn_add_member(uuid, uuid, public.club_role);
drop function if exists public.fn_create_club(text, text, char);
drop function if exists app.audit_row_change();
drop function if exists app.block_audit_mutation();
drop function if exists app.touch_updated_at();
drop function if exists app.assert_can_manage_role(uuid, public.club_role);
drop function if exists app.assert_club_keeps_admin(uuid, uuid);
drop function if exists app.membership_role(uuid);
drop function if exists app.membership_club(uuid);
drop function if exists app.membership_is_active(uuid);

-- 2. f1_rls_isolation
drop policy if exists clubs_select       on public.clubs;
drop policy if exists profiles_select    on public.profiles;
drop policy if exists profiles_insert_self on public.profiles;
drop policy if exists profiles_update_self on public.profiles;
drop policy if exists memberships_select on public.club_memberships;
drop policy if exists audit_select       on public.audit_events;
drop function if exists app.can_view_profile(uuid);
drop function if exists app.has_club_role(uuid, public.club_role[]);
drop function if exists app.is_club_member(uuid);
drop function if exists app.is_platform_admin();
drop function if exists app.current_user_id();
drop schema if exists app;   -- vacío tras lo anterior

-- 1. f1_clubs_users_core  (destruye datos)
drop table if exists public.audit_events;
drop table if exists public.club_memberships;
drop table if exists public.platform_admins;
drop table if exists public.profiles;
drop table if exists public.clubs;
drop type if exists public.club_status;
drop type if exists public.membership_status;
drop type if exists public.club_role;
```

Los archivos de migración no son idempotentes en su totalidad (`create table` usa
`if not exists`, pero un `drop type` intermedio rompería las tablas). Para reconstruir desde
cero: revertir en el orden anterior y volver a aplicar las seis migraciones en orden.

---

## 7. Operación: alta del primer administrador de plataforma

No existe RPC para conceder `platform_admin`. Es deliberado: una función expuesta que otorgue
ese rol sería un camino de escalado de privilegios. La concesión se hace **una sola vez**, por
SQL directo, con acceso al proyecto:

```sql
-- Requiere que el usuario exista ya en auth.users.
insert into public.platform_admins (user_id, granted_by)
values ('<uuid-del-usuario>', null);
```

A partir de ahí, ese usuario puede crear clubes y designar administradores de club mediante
`fn_create_club` y `fn_add_member`. Cada concesión queda auditada por
`trg_audit_platform_admins`.

**Pendiente de la capa de aplicación (DEC-12 cerrada el 12/11/2026: FastAPI como BFF, sin desplegar):**

- Crear el registro en `profiles` cuando se da de alta un usuario. Hoy el titular puede insertar
  su propio perfil con `(id, display_name)`, pero nada lo crea automáticamente.
- Alta de usuarios en `auth.users` (el flujo de invitación es F18 y está fuera de F1).
- Interfaz, servidor de desarrollo y pruebas de navegación.

## 8. Reproducir en otro proyecto

```bash
supabase link --project-ref <ref>
supabase db push          # aplica supabase/migrations en orden de versión
```

Requiere contraseña de base de datos y red disponible. En el proyecto anterior
(`taevpaknhuoyiujqgjku`) no se usó `db push`: las migraciones se aplicaron por MCP y los
archivos se verificaron por md5 contra el texto guardado en
`supabase_migrations.schema_migrations`.

**Proyecto nuevo (12/11/2026):** el historial `supabase_migrations` está **vacío** y no existe
la tabla, porque las siete migraciones se aplicaron concatenadas con `psql` dentro de una
transacción (`ON_ERROR_STOP=1`) sobre el pooler IPv4. Las migraciones están aplicadas y
verificadas, pero el CLI no las reconoce como aplicadas. Antes de usar `db push` o
`supabase migration list` contra este proyecto hay que decidir cómo registrar el historial:
ver `docs/implementation/f1/03-migracion-remota.md` §5.
