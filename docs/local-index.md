# VOLTERRA — Índice organizado del conocimiento local

**Generado:** 16/11/2026  
**Fuente:** Documentación del repositorio `/root/volterra` (sin NotebookLM).  
**Objetivo:** Mapa navegable de la documentación del proyecto, organizada por categoría.

---

## 1. Arquitectura y decisiones técnicas

### 1.1 Backend: FastAPI como BFF (DEC-12, aprobada 12/11/2026)
- **Documento:** `docs/architecture/backend-choice.md`
- **Decisión:** FastAPI (Python 3.11+) como Backend-for-Frontend. JWT del usuario por petición, PostgREST/RLS, sin `service_role`.
- **Invariantes clave:**
  - Cada petición usa el JWT del usuario y un cliente PostgREST por petición.
  - `service_role` prohibida en todo camino de usuario.
  - Sin conexión directa como rol propietario ni SQL/DDL desde el backend.
  - Reglas de autorización en Postgres (RLS `enable`+`force`, `app.*` y RPC).
  - BFF no duplica reglas de dominio.
  - US$0/mes (DEC-08). Host no elegido, sin despliegue sin autorización.
- **ADR:** `decisions/adr/ADR-013-fastapi-bff.md` (aprobado), `ADR-012-capa-de-aplicacion.md` (rechazado).
- **Nota:** La matriz de DEC-12 puntuó la variante D (conexión directa) como 2,58 (eliminada), no esta variante BFF. La aprobación es un acto del propietario.

### 1.2 Frontend: Jinja2 + HTMX (DEC-21, aprobada 12/11/2026)
- **ADR:** `decisions/adr/ADR-014-frontend-jinja-htmx.md`
- **Stack:** Jinja2 + HTMX, sesión con cookie `HttpOnly` + CSRF, F1 en solo lectura, español `es-CO`.
- **Rutas HTML:** `/login`, `/logout`, `/auth/refresh`, `/me`, `/clubs`, `/clubs/{id}`, `/clubs/{id}/members`, `/platform`, páginas de error.
- **Cookies:** `volterra_access` y `volterra_refresh` `HttpOnly`; CSRF double-submit en formularios y cabecera `X-CSRF-Token`.

### 1.3 Decisiones registradas (22 DEC)
- **Archivo:** `decisions/decision-register.md`
- **Aprobadas:** DEC-01, DEC-02, DEC-03, DEC-06, DEC-07, DEC-08, DEC-12, DEC-18 (Opción C), DEC-19 (Opción A), DEC-21, DEC-22.
- **Pendientes:** DEC-04, DEC-05, DEC-09, DEC-10, DEC-11, DEC-13, DEC-14, DEC-15, DEC-16, DEC-17, DEC-20.
- **DEC-18 (resuelta 16/11/2026):** Alcance y retención de bitácora de auditoría → Opción C (riesgo aceptado, sin cambio RLS). `club_admin` mantiene visibilidad de `audit_events`.
- **DEC-19 (resuelta 16/11/2026):** Región de hosting → Opción A (hosting en región LATAM). Simplifica cumplimiento art. 26 Ley 1581/2012.

---

## 2. Seguridad

### 2.1 ASVS v5 Nivel 2 — Matriz acotada de F1
- **Documento:** `docs/security/asvs-l2-f1.md`
- **Decisión de referencia:** DEC-06 (OWASP ASVS v5 nivel 2, aprobada 13/11/2026)
- **Naturaleza:** documento de evidencia, no certificación. No declara conformidad.
- **Hallazgos resueltos:** F-01 (Baja, corregido), F-03 (Media, corregido), F-05 (Media, corregido), F-06 (Baja, corregido), F-09 (Baja, corregido), F-12 (Baja, corregido).
- **Hallazgos aceptados como riesgo:** F-02 (Media, Opción C), F-08 (Baja, logs), F-11 (Baja, privilegios — pendiente de decisión).
- **Hallazgos pendientes:** F-04 (parcial, HSTS), F-07 (Baja, HSTS), F-10 (Baja, lockfile).
- **Controles positivos confirmados:** JWT estricto, cookies `HttpOnly`/`Secure`/`SameSite`, RLS `enable`+`force`, auditoría append-only, cliente por petición sin `service_role`, fallo cerrado en producción.

### 2.2 F-01 — Mensajes de error controlados (corregido 16/11/2026)
- **Archivo:** `volterra/apps/services/postgrest_errors.py`
- **Fix:** `SQLSTATE_MESSAGES` (mensaje fijo por código SQLSTATE). Ya no propaga `exc.message` al cliente.
- **Pruebas:** `tests/test_f1_reads.py`, `tests/test_f1_writes.py`, `tests/test_web_writes.py` (197 passed).
- **Trade-off:** Se pierde detalle específico de RPC (ej. "solo puede gestionar entrenadores"). Aceptado por seguridad.

### 2.3 F-02 — Visibilidad de auditoría para club_admin (riesgo aceptado)
- **Decisión:** DEC-18, Opción C. Sin cambio de RLS.
- **Riesgo:** `club_admin` puede ver UUIDs, rol y fechas en `audit_events` de membresías cerradas. No hay nombres ni correos en claro.

### 2.4 Necesidades de validación pendientes (8 items)
1. Trusted hosts wildcard
2. XFF trust
3. HSTS (F-07)
4. JWKS HTTP
5. In-memory rate limit topology (multi-worker)
6. HS256 algorithm confusion
7. No lockfile (F-10)
8. Cookie secure dev default

---

## 3. Implementación (F1)

### 3.1 Autorización y alcance
- **Documento:** `docs/implementation/f1/00-autorizacion-y-alcance.md`

### 3.2 Platform admin RPC
- **Documento:** `docs/implementation/f1/01-platform-admin-rpc.md`

### 3.3 Demo local
- **Documento:** `docs/implementation/f1/02-demo-local.md`

### 3.4 Migración remota
- **Documento:** `docs/implementation/f1/03-migracion-remota.md`
- **Estado:** Esquema aplicado en `tioeoswnhwrlbovkxocd` el 12/11/2026 (7 migraciones, 134/134 pruebas). E2E verificado (37/37). Smoke OK.
- **Residuo:** Un club ficticio en la base (no eliminado sin aprobación).

### 3.5 Hardening y UI
- **Documento:** `docs/implementation/f1/04-hardening-y-ui.md`
- **Rate limiting:** Ventana fija en memoria por proceso. Perfil estricto: login 5/5 min, refresh/logout 15/5 min, escrituras 15/min, lecturas 120/min. Limitación: multi-worker multiplica cupo.
- **Logging:** Una línea JSON por petición en stdout. Sin cuerpos, cookies ni IP en claro.

### 3.6 Arquitectura backend
- **Documento:** `docs/implementation/f1/06-arquitectura-backend.md`

### 3.7 Contrato API
- **Documento:** `docs/implementation/f1/07-contrato-api.md`

### 3.8 Robustez operativa
- **Documento:** `docs/implementation/f1/05-robustez-operativa.md`
- **Componentes:** `create_app()` + `lifespan`, `/health/live` y `/health/ready`, configuración fail-fast, `TrustedHostMiddleware`, OpenAPI desactivado fuera de producción, timeout de PostgREST.

---

## 4. Operaciones

### 4.1 Pendientes bloqueantes
- **Documento:** `docs/operations/pendientes-bloqueantes.md`
- **Estado:** §1 cerrada (DEC-12), frontend implementado (DEC-21), respaldo decidido (DEC-07), hardening implementado (DEC-22). O-03 abierta (restauración en proyecto Supabase real). Sin despliegue.

### 4.2 Plan de host
- **Documento:** `docs/operations/o-04-plan-host.md`
- **Estado:** No elige proveedor. Candidatos, requisitos y trabajo previo documentados. Host no elegido.

### 4.3 Respaldo y restauración (O-03)
- **Documento:** `docs/operations/o-03-respaldo-restauracion.md`
- **Política (DEC-07):** RPO 24h, RTO 8h, frecuencia diaria, retención 30 días, destino fuera del proveedor (sin coste), responsable: propietario.
- **Estado:** Volcado real + ensayo local 127/127 OK. Falta restaurar en otro proyecto Supabase autorizado.

---

## 5. Investigación (Fase 1 Colombia)

### 5.1 Plan de investigación
- **Documento:** `docs/research/fase1-colombia/00-plan-investigacion.md`

### 5.2 Problemas de clubes y entrenadores
- **Documento:** `docs/research/fase1-colombia/01-problemas-clubes-entrenadores.md`

### 5.3 MVP vs futuro
- **Documento:** `docs/research/fase1-colombia/02-mvp-vs-futuro.md`

### 5.4 Requisitos de arquitectura, seguridad, privacidad, permisos y trazabilidad
- **Documento:** `docs/research/fase1-colombia/03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md`

### 5.5 Preguntas antes de elegir tecnologías
- **Documento:** `docs/research/fase1-colombia/04-preguntas-antes-elegir-tecnologias.md`
- **Estado:** 38 preguntas (P1=20, P2=14, P3=4). Relación con decisiones documentada.

### 5.6 Bitácora de fuentes
- **Documento:** `docs/research/fase1-colombia/05-bitacora-fuentes.md`
- **Estado:** DEC-18 y DEC-19 marcados como aprobados. Resto pendientes.

---

## 6. Recuperación y diagnóstico

### 6.1 Diagnóstico (23/10/2026)
- **Documento:** `docs/recovery/diagnostico-2026-10-23.md`

### 6.2 Estado de recuperación
- **Documento:** `docs/recovery/estado-recuperacion.md`

### 6.3 Informe de recuperación (21/10/2026)
- **Documento:** `docs/recovery/informe-recuperacion-2026-10-21.md`

---

## 7. Análisis documental y auditoría legal

- **Documento:** `docs/analysis/2026-11-02-analisis-documental-y-auditoria-legal.md`
- **Contenido:** Análisis de cumplimiento legal colombiano, retención de logs/auditoría, acceso del titular.

---

## 8. Código fuente clave

### 8.1 Superficie de seguridad
| Archivo | Propósito |
|---------|-----------|
| `volterra/main.py` | App FastAPI, middleware, cabeceras, fail-fast |
| `volterra/apps/core/config.py` | Configuración, `runtime_config_problems()` |
| `volterra/apps/core/security.py` | JWT estricto, validación `iss`/`aud`/`exp`/`iat`/`sub`/`role` |
| `volterra/apps/core/ratelimit.py` | Rate limiting en memoria por proceso |
| `volterra/apps/core/logging.py` | Logging estructurado JSON |
| `volterra/apps/core/errors.py` | Errores de dominio |
| `volterra/apps/auth/session.py` | Sesión por cookie, CSRF, login/logout/refresh |
| `volterra/apps/auth/deps.py` | Dependencias de autenticación |
| `volterra/apps/services/postgrest_errors.py` | Traducción SQLSTATE → error de dominio (F-01 corregido) |
| `volterra/apps/integrations/supabase/per_request.py` | Cliente PostgREST por petición con JWT |

### 8.2 Pruebas
| Archivo | Propósito |
|---------|-----------|
| `volterra/tests/test_f1_reads.py` | Lecturas F1 (SQLSTATE mapping) |
| `volterra/tests/test_f1_writes.py` | Escrituras F1 (SQLSTATE mapping) |
| `volterra/tests/test_web_writes.py` | Web writes (CSRF, traducción de errores) |
| `volterra/tests/test_jwt_security.py` | JWT strict validation |
| `volterra/tests/test_ratelimit.py` | Rate limiting |
| `volterra/tests/test_api_contract.py` | Contrato API |
| `volterra/tests/test_operational.py` | Robustez operativa |
| `volterra/tests/test_web_ui.py` | UI/accesibilidad |

### 8.3 Migraciones SQL
- **Directorio:** `supabase/migrations/`
- **F1 RLS isolation:** `20261026025346_f1_rls_isolation.sql`
- **F1 mutations and audit:** `20261026025413_f1_mutations_and_audit.sql`
- **F1 hardening:** `20261026040817_f1_hardening.sql`
- **F1 is platform admin:** `20261102120000_f1_is_platform_admin.sql`
- **F1 update club profile:** `20261026035037_f1_update_club_profile.sql`

---

## 9. Decisiones pendientes (post-16/11/2026)

| ID | Título | Estado |
|----|--------|--------|
| DEC-04 | Región de hosting (parcial) | Pendiente — bloqueado por E-7/E-8 |
| DEC-05 | Retención de datos | Pendiente |
| DEC-09 | Stack de frontend (parcial) | Pendiente |
| DEC-10 | Herramienta de gestión de proyecto | Pendiente |
| DEC-11 | Estrategia de testing | Pendiente |
| DEC-13 | Política de privacidad | Pendiente |
| DEC-14 | Consentimiento informado | Pendiente |
| DEC-15 | Figura de cumplimiento interno | Pendiente |
| DEC-16 | Datos de salud (E-3) | Pendiente |
| DEC-17 | Plan de validación con clubes | Pendiente |
| DEC-20 | Estándar de evidencia | Pendiente |
| F-07 | HSTS | Pendiente — requiere HTTPS extremo a extremo + host |
| F-10 | Lockfile | Pendiente — requiere fijar versiones |
| F-11 | Privilegios supabase_admin | Pendiente — cambio de arquitectura |

---

## 10. Bloqueos jurídicos abiertos (E-1 a E-10)

| Bloqueo | Descripción | Afecta |
|---------|-------------|--------|
| E-1 | Alcance por edades | DEC-01 (F7) |
| E-2 | Reservas/pagos/WhatsApp | Fuera de F1 |
| E-3 | Datos de salud | DEC-16 |
| E-4 | Transferencia internacional | DEC-05, DEC-19 (resuelto con Opción A) |
| E-5 | Costo operativo | Host, despliegue |
| E-6 | Región de hosting | DEC-19 (resuelto con Opción A) |
| E-7 | Reservas/pagos | Fuera de F1 |
| E-8 | WhatsApp | Fuera de F1 |
| E-9 | Figura de cumplimiento | DEC-15 |
| E-10 | Alcance por edades | DEC-01 |

---

## 11. Reglas operativas

- **No desplegar** sin autorización.
- **No generar costos.**
- **No exponer secretos.**
- **Solo datos ficticios** hasta nuevo aviso.
- **Commits selectivos** — sin `git add .`
- **MCP en solo lectura** — el volcado/restauración requiere credencial y permiso explícito.
- **No modificar código sin presentar hallazgos primero.**
- **Aplicar permisos en servidor y datos.**

---

*Índice generado a partir de la documentación del repositorio. Sin dependencia de NotebookLM.*