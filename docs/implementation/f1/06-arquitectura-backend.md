# F1 — Arquitectura del backend: errores, composición y rutas (14/11/2026)

**Estado:** implementado y probado en local. **Sin despliegue, sin push y sin datos reales.**
**Decisiones de referencia:** ADR-013 (FastAPI como BFF), DEC-12, DEC-21, DEC-22, DEC-08.
**Naturaleza:** refactor de implementación dentro de decisiones ya aprobadas. **No crea una
decisión nueva**, no elige host ni proveedor y no cambia RLS, RPC ni el modelo de datos.

---

## 1. Qué se implementó

Tres incrementos, en este orden:

1. **Errores de dominio con una sola traducción a HTTP/HTML.**
2. **Retirada del cliente heredado y composición única por petición.**
3. **División de las rutas web y separación de la presentación.**

### 1.1 Errores de dominio

Nuevo `volterra/apps/core/errors.py`:

| Clase | `code` | Estado HTTP | Título HTML |
|---|---|---|---|
| `InvalidInputError` | `invalid_input` | 400 | Solicitud inválida |
| `UnauthenticatedError` | `unauthenticated` | 401 | Acceso denegado |
| `ForbiddenError` | `forbidden` | 403 | Acceso denegado |
| `NotFoundError` | `not_found` | 404 | Página no encontrada |
| `ConflictError` | `conflict` | 409 | Conflicto con el estado actual |
| `RateLimitedError` | `rate_limited` | 429 | Demasiados intentos |
| `UnavailableError` | `unavailable` | 503 | Servicio no disponible |
| `DomainError` (base) | `error` | 500 | No se pudo completar la operación |

- `STATUS_BY_CODE` y `TITLE_BY_CODE` son las **únicas** tablas de traducción.
- `http_status()`, `title()` y `headers()` resuelven estado, título y cabeceras.
- Un código no registrado cae en **500**, no en un estado inventado.
- Solo `RateLimitedError` aporta `Retry-After`; el resto no añade cabeceras.
- Las capas de servicios y las guardas de autenticación **ya no conocen HTTP**:
  `f1_reads.py` lanza `UnavailableError`; `f1_writes.py` traduce SQLSTATE a clase de error
  (`_SQLSTATE_ERRORS`); `auth/session.py` traduce fallos de GoTrue a
  `UnauthenticatedError` / `RateLimitedError` / `UnavailableError`.
- Se eliminaron `WriteError`, `DataUnavailableError` y `AuthServiceError`. **No hay shim de
  compatibilidad**: cualquier código que importe los nombres antiguos falla de forma visible.

`main.py` registra `domain_error_handler` para `DomainError`:

| Petición | Respuesta |
|---|---|
| `/api/v1/*` o `/auth/*` | JSON `{"detail": "...", "code": "..."}` con el estado de la tabla |
| Página HTML, 401 | `303` a `/login?next_url=<ruta>` |
| Página HTML, resto | `error.html` con el título del catálogo y el mensaje |
| Cualquier 429 | cabecera `Retry-After` |

El middleware de límite de peticiones **usa el mismo traductor** (`_rate_limited_response`
construye un `RateLimitedError` y delega en `domain_error_handler`), así que el 429 anónimo de
`/api/v1` también devuelve `code`. Antes existían dos contratos distintos para el mismo fallo.

`http_exception_handler` se conserva solo para fallos del framework (404 de ruta, 405, host no
permitido). `validation_exception_handler` conserva el 422 de FastAPI.

### 1.2 Composición del cliente de datos

- Nuevo `volterra/apps/integrations/supabase/deps.py` con `get_data_client()`.
- `get_auth_context()` crea el cliente con el JWT del usuario y lo guarda en
  `request.state.data_client`; `get_data_client()` lo reutiliza.
- Resultado: **un solo cliente Supabase por petición**, también cuando la ruta necesita datos
  después de autenticar.
- Se eliminó `volterra/integrations/` (`client.py` y `rpc.py`): era un cliente global sin
  identidad de usuario, sin uso real y contrario al invariante 6 de ADR-013.
- No se usa `service_role` ni un cliente global. La autorización sigue en RLS + RPC.

### 1.3 Rutas web y presentación

`apps/web/routes.py` (552 líneas, 17 rutas) se sustituyó por un paquete:

| Archivo | Contenido | Rutas |
|---|---|---|
| `routes/__init__.py` | composición del `APIRouter` y reexporte de `_safe_next` | — |
| `routes/auth.py` | login, logout, refresh | 5 |
| `routes/me.py` | `/me` y `/clubs` | 2 |
| `routes/clubs.py` | alta, edición y detalle de club | 5 |
| `routes/members.py` | listado, alta, cambio de rol y cierre | 4 |
| `routes/platform.py` | panel de plataforma | 1 |
| `routes/common.py` | utilidades compartidas | — |
| `viewmodels.py` | dataclasses de presentación con `context()` | — |

- Las plantillas reciben un **view-model** con campos declarados, no diccionarios sueltos.
- `common.py` concentra `safe_next`, `club_role`, `assignable_roles`, `normalize_country`,
  `ensure_uuid`, `membership_in_club` y `render_members`.
- El orden de registro se conserva: `/clubs/new` antes que `/clubs/{club_id}`.
- La UI sigue **ocultando** acciones según el rol, pero no autoriza: cada lectura y escritura
  vuelve a pasar por el BFF, el JWT y RLS + RPC.

---

## 2. Archivos

**Nuevos**

- `volterra/apps/core/errors.py`
- `volterra/apps/integrations/supabase/deps.py`
- `volterra/apps/web/routes/` (`__init__`, `auth`, `common`, `clubs`, `me`, `members`, `platform`)
- `volterra/apps/web/viewmodels.py`
- `volterra/tests/test_errors.py`

**Modificados**

- `volterra/main.py` (manejador de dominio, traducción única del 429, helpers de API/login)
- `volterra/apps/auth/deps.py`, `volterra/apps/auth/session.py`
- `volterra/apps/services/f1_reads.py`, `volterra/apps/services/f1_writes.py`
- `volterra/apps/api/v1/endpoints/me.py`, `volterra/apps/api/v1/endpoints/clubs.py`
- Pruebas: `test_auth_context.py`, `test_f1_reads.py`, `test_f1_writes.py`, `test_ratelimit.py`,
  `test_web_session.py`, `test_web_ui.py`, `test_web_writes.py`

**Eliminados**

- `volterra/apps/web/routes.py`
- `volterra/integrations/` (`__init__.py`, `supabase/__init__.py`, `client.py`, `rpc.py`)

---

## 3. Pruebas ejecutadas

| Comprobación | Resultado |
|---|---|
| `pytest` (suite completa) | **177 passed, 1 warning** |
| `tests/test_errors.py` (nuevo) | **21 passed** |
| `ruff check apps main.py tests --select F,E9` | **All checks passed** |
| `python -m compileall apps main.py` | sin errores |
| `git diff --check` | sin espacios ni conflictos |
| Rutas web cargadas (`TestClient`) | `/login` 200, `/me` 303, `/api/v1/me` 307, `/clubs/new` 303, `/platform` 303 |

El único warning es `StarletteDeprecationWarning` de `fastapi.testclient` (dependencia del
entorno de pruebas), ya presente antes de este incremento. **No se ejecutaron** pruebas con
navegador real, axe/Lighthouse ni lector de pantalla.

Cobertura nueva de `tests/test_errors.py`:

- tabla código → estado y fallback a 500;
- `Retry-After` solo en 429;
- títulos HTML sin códigos internos;
- API sin sesión → JSON con `code`; página sin sesión → 303 al login;
- 403 y 404 con JSON o HTML según el tipo de petición;
- límite por usuario y límite anónimo con el mismo contrato;
- un solo cliente Supabase por petición.

---

## 4. Verificación de Vercel (sin desplegar)

**Hechos comprobados en el repositorio:**

- **No existe** `vercel.json` ni `volterra/vercel.json`.
- **No existe** el directorio `.vercel/` ni en la raíz ni en `volterra/`.
- No hay documentación de un despliegue en Vercel ni un proyecto asociado en `docs/`,
  `decisions/` o `workspace/`. Las únicas menciones son el plan de host
  (`docs/operations/o-04-plan-host.md`) y la restricción de **uso no comercial** de Vercel Hobby
  registrada en `decisions/dec-12-material-decision.md` §2.
- `opencode.json` configura un MCP remoto de Vercel, pero en esta sesión **no expone recursos**
  (`list_mcp_resources` devuelve listas vacías) y sus herramientas no están disponibles en el
  catálogo de herramientas del agente. Por tanto **no se pudo consultar** si existe un proyecto
  o un despliegue en la cuenta.
- **No se desplegó nada.** No se creó proyecto, no se subió código y no se generó coste.

**Consecuencia técnica (hipótesis, no verificada aquí):** el BFF es una aplicación ASGI con
proceso persistente (`uvicorn main:app`), plantillas Jinja2 y estado en memoria (límite de
peticiones por proceso). Ejecutarlo en Vercel exigiría un adaptador ASGI (por ejemplo Mangum),
**no probado en este proyecto**, y cambiaría el comportamiento del límite de peticiones: cada
instancia tendría su propio contador. Los límites de duración y el arranque en frío de las
funciones tampoco están medidos. Nada de esto se ha validado.

**Recomendación:** no tratar Vercel como «servidor verificado». La elección de host sigue
abierta en `docs/operations/o-04-plan-host.md` y sujeta a DEC-08, DEC-19/E-6 y autorización
explícita del propietario.

**Hallazgo menor, no corregido:** `opencode.json` apunta el MCP de Supabase al `ref`
`taevpaknhuoyiujqgjku`, que ya no existe en DNS; el proyecto vigente es `tioeoswnhwrlbovkxocd`.
No se editó porque es configuración del entorno del propietario.

---

## 5. Límites y riesgos

- **Contrato de error no uniforme al 100 %:** los errores de dominio devuelven
  `{"detail", "code"}`, pero el 422 de validación y los 404/405 del framework devuelven solo
  `{"detail"}`. Unificarlo exige decidir si el `code` es obligatorio en todo el contrato.
- **Mensajes de PostgREST:** un SQLSTATE desconocido se traduce a 503 con un mensaje genérico;
  no se filtra el texto crudo de la base. Si la base devuelve un mensaje propio en un SQLSTATE
  conocido, ese mensaje sí llega al usuario. Es el comportamiento anterior, no una regresión.
- **`request.state.data_client`:** si una ruta futura sustituye el cliente a mitad de petición,
  la reutilización podría devolver el anterior. Hoy solo lo escribe la guarda de autenticación.
- **Límite de peticiones:** sigue en memoria por proceso (ADR-015). Con varios workers el cupo se
  multiplica y se reinicia al reiniciar.
- **Sin pruebas de navegador real** ni de accesibilidad automatizada tras el refactor.

---

## 6. Decisiones pendientes

1. ¿El `code` debe ser obligatorio también en 422 y en los errores del framework?
2. ¿Se actualiza el `ref` del MCP de Supabase en `opencode.json`?
3. Host y despliegue: sin decidir; no autorizado en este incremento.
4. Matriz ASVS (DEC-06) y pruebas con navegador real: siguen pendientes.
