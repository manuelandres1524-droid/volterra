# F1 — Contrato de la API JSON y paginación opcional (14/11/2026)

**Estado:** implementado y probado en local. **Sin commit, sin push, sin despliegue y sin datos
reales.**
**Decisiones de referencia:** ADR-013 (FastAPI como BFF), DEC-12, DEC-21, DEC-22, DEC-08.
**Naturaleza:** incremento de implementación dentro de decisiones ya aprobadas. **No crea una
decisión nueva**, no cambia RLS, RPC, el modelo de datos ni el host. La uniformidad del `code`
en los fallos del framework y la forma de paginar son **decisiones de implementación
provisionales**, sujetas a revisión del propietario.

---

## 1. Objetivo

Cerrar la brecha declarada en `06-arquitectura-backend.md` §5: el contrato de error no era
uniforme (422 y 404/405 del framework devolvían solo `detail`) y los endpoints JSON no
declaraban modelos de respuesta ni paginación. El cambio es **aditivo**:

- los errores del framework usan el mismo vocabulario `code` que los errores de dominio;
- OpenAPI documenta el cuerpo real de cada respuesta;
- el listado de miembros admite `limit`/`offset` opcionales sin romper a los clientes actuales.

No se añadió autorización nueva: RLS + RPC siguen siendo la autoridad y los modelos solo
describen datos que la base ya filtró.

---

## 2. Qué cambió

### 2.1 Un solo vocabulario de `code`

- `apps/core/errors.py` añade `CODE_BY_STATUS` y `code_for_status()`.
- `http_exception_handler` (404 de ruta, 405, host no permitido) devuelve
  `{"detail": "...", "code": "..."}`.
- `validation_exception_handler` devuelve `{"detail": [...], "code": "invalid_input"}`.
- El título HTML de los fallos del framework se resuelve con `TITLE_BY_CODE`, la misma tabla
  que usan los errores de dominio. Se eliminó la tabla duplicada `_ERROR_TITLES` de `main.py`.

| Origen | Estado | `code` | `detail` |
|---|---|---|---|
| `DomainError` | tabla `STATUS_BY_CODE` | `code` de la clase | texto mostrable |
| Ruta inexistente | 404 | `not_found` | texto del framework |
| Método no permitido | 405 | `method_not_allowed` | texto del framework |
| Validación de cuerpo/query | 422 | `invalid_input` | lista estructurada por campo |
| Límite de peticiones | 429 | `rate_limited` | texto mostrable + `Retry-After` |

`method_not_allowed` no tiene traducción a `DomainError` a propósito: solo lo produce el
framework y no se lanza desde servicios.

### 2.2 Modelos de respuesta

Nuevo `apps/api/v1/schemas.py` con `ErrorOut`, `ValidationErrorOut`, `MeOut`, `MyClubsOut`,
`ClubOut`, `MemberOut`, `MembersOut`, `IdOut`, `PlatformOverviewOut` y `HealthOut`.

- `response_model` declarado en `health`, `me`, `platform` y en los endpoints de `clubs`.
- Las respuestas de error comunes se declaran una vez en `apps/api/v1/router.py`
  (`AUTH_RESPONSES`, `COMMON_RESPONSES`) y se pasan a `include_router(responses=...)`.
  `/me` documenta 401/429/503; clubs y platform documentan además 400/403/404/409/422.
- Las fechas se declaran como `str` para **no alterar** la representación que ya devuelve
  PostgREST. Cambiar a `datetime` habría modificado el JSON observable.
- `response_model` valida la salida: si un servicio devolviera un campo obligatorio ausente, la
  respuesta fallaría en pruebas en lugar de degradar el contrato en silencio.

### 2.3 Paginación opcional de miembros

`GET /api/v1/clubs/{club_id}/members`:

| Parámetro | Tipo | Regla |
|---|---|---|
| `limit` | entero o ausente | `1..200`; ausente = sin límite |
| `offset` | entero | `>= 0`; por defecto `0` |

- `offset > 0` sin `limit` → `400 invalid_input` antes de consultar la base.
- La consulta usa `.range(offset, offset + limit - 1)` solo cuando hay `limit`.
- Se añadió orden secundario por `id` para que la paginación sea estable cuando varias
  pertenencias comparten `started_at`.
- La respuesta incluye `limit` y `offset` junto a `club_id` y `members`.
- Sin `limit`, la respuesta conserva el comportamiento anterior (lista completa).

---

## 3. Archivos

**Nuevos**

- `volterra/apps/api/v1/schemas.py`
- `volterra/tests/test_api_contract.py`

**Modificados**

- `volterra/apps/core/errors.py` (`CODE_BY_STATUS`, `code_for_status()`)
- `volterra/main.py` (manejadores 404/405 y 422 con `code`; sin `_ERROR_TITLES`)
- `volterra/apps/api/v1/router.py` (respuestas comunes documentadas)
- `volterra/apps/api/v1/endpoints/health.py`, `me.py`, `platform.py`, `clubs.py`
- `volterra/apps/services/f1_reads.py` (`list_club_members` con `limit`/`offset`)

No se tocaron migraciones, políticas RLS, RPC, plantillas ni variables de entorno.

---

## 4. Pruebas ejecutadas

| Comprobación | Resultado |
|---|---|
| `pytest` (suite completa) | **186 passed, 1 warning** |
| `tests/test_api_contract.py` (nuevo) | **9 passed** |
| `ruff check apps main.py tests --select F,E9` | **All checks passed** |
| `python -m compileall -q apps main.py tests` | sin errores |
| `git diff --check` | sin espacios ni conflictos |

El warning es `StarletteDeprecationWarning` de `fastapi.testclient`, ya presente antes de este
incremento. **No se ejecutaron** pruebas con navegador real, axe/Lighthouse ni lector de
pantalla; tampoco se reejecutó el E2E de escrituras.

Cobertura nueva de `tests/test_api_contract.py`:

- OpenAPI referencia `MeOut`, `MyClubsOut`, `ClubOut`, `MembersOut`, `PlatformOverviewOut` y
  `HealthOut`, y documenta `ErrorOut`/`ValidationErrorOut` en las respuestas de error;
- `/me` devuelve exactamente las claves del modelo;
- 404 de ruta y 405 devuelven `not_found` y `method_not_allowed`;
- 422 devuelve `invalid_input` con `detail` estructurado;
- `limit`/`offset` aplican `.range()` y reflejan los parámetros en el cuerpo;
- `offset` sin `limit` se rechaza antes de consultar;
- `limit=201` devuelve 422 con `invalid_input`.

Los 177 tests previos siguen en verde; los dobles de prueba existentes no necesitan `.range()`
porque solo se llama con `limit` explícito.

---

## 5. Límites y riesgos

- **`detail` del 422 es una lista**, no un texto. Es el formato que ya exponía FastAPI y se
  documenta con `ValidationErrorOut`; no se normalizó a texto para no perder el detalle por
  campo. Si se quiere un `detail` siempre textual, es una decisión de contrato pendiente.
- **`method_not_allowed` no es un `DomainError`:** no aparece en `STATUS_BY_CODE` ni se puede
  lanzar desde un servicio. Es deliberado.
- **La paginación no informa del total.** Un `total` exigiría un `count` adicional por consulta;
  no se añadió para no duplicar viajes a PostgREST.
- **La respuesta completa sigue siendo el valor por defecto.** Un cliente que no envía `limit`
  recibe todos los miembros visibles; el límite de 200 solo aplica cuando se pagina.
- **Sin pruebas de navegador real** ni verificación contra el Supabase remoto en este
  incremento. Las pruebas usan dobles de cliente; la suite SQL no se reejecutó.

---

## 6. Decisiones pendientes

1. ¿Se acepta `detail` como lista en el 422 o se normaliza a texto? Provisional: lista.
2. ¿Se añade `total` a la paginación de miembros? Provisional: no.
3. ¿Se replica la paginación en las páginas HTML? (no incluido; la UI sigue mostrando la lista
   completa).
4. Host, despliegue, matriz ASVS y pruebas con navegador real siguen pendientes y sin autorizar.

> **Actualización del 16/11/2026.** La matriz ASVS acotada ya existe en
> `docs/security/asvs-l2-f1.md`. No declara conformidad: documenta brechas abiertas (auditoría de
> exmiembros, mensajes de SQLSTATE, HSTS, lockfile y privilegios por defecto).
