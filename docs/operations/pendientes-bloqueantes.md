# Pendientes bloqueantes — VOLTERRA

**Fecha:** 26/10/2026 · **Actualizado:** 16/11/2026

**Estado:** §1 cerrada (DEC-12), frontend de F1 implementado (DEC-21), política de respaldo decidida (DEC-07, §2), hardening mínimo de F1 implementado (DEC-22: límite de peticiones y logging) y robustez operativa del BFF (14/11/2026: salud, fail-fast, hosts y timeouts). Sigue abierta O-03 (§3) por la restauración en un proyecto Supabase real. No hay despliegue.

## 1) DEC-12 — Capa de aplicación (cerrada el 12/11/2026)

**Estado:** **Aprobada.** El propietario ratificó **FastAPI como BFF**. ADR vigente:
`decisions/adr/ADR-013-fastapi-bff.md`. ADR-012 (opción B) queda **rechazada**.

- [x] **Elección:** FastAPI como BFF (JWT de usuario, PostgREST/RLS, sin `service_role`).
- [x] **Registro:** DEC-12 aprobada en `decisions/decision-register.md` (v1.2).
- [x] **Endurecimiento del BFF:** rechazo de `role=service_role`, `SUPABASE_SERVICE_ROLE_KEY`
  eliminada de `Settings`, CORS sin `*`, cabeceras de seguridad, `no-store` y mapeo `401/503`.
  Suite `pytest`: **76 passed** (12/11/2026). Ver `decisions/adr/ADR-013-fastapi-bff.md` §8.
- [ ] **Host del BFF:** no elegido. **No se despliega** sin autorización y sin evaluar coste/condiciones.
  Plan de análisis (familias, requisitos, checklist previo y bloqueos): `docs/operations/o-04-plan-host.md`.
- [x] **Verificación contra Supabase:** esquema aplicado en `tioeoswnhwrlbovkxocd` el 12/11/2026
  (preflight vacío → 7 migraciones en una transacción → **134/134** en las cuatro suites). El
  frontend autenticado funcionó de extremo a extremo (**37/37**) y `scripts/smoke_f1.py` terminó en
  **SMOKE OK**. Detalle: `docs/implementation/f1/03-migracion-remota.md` §9.
- [ ] **Historial de migraciones:** `supabase_migrations.schema_migrations` no existe; el CLI no
  reconoce las migraciones aplicadas. Falta decidir si se registra o se reconstruye con
  `supabase db push`.
- [x] **Límite de peticiones (13/11/2026):** ventana fija **en memoria por proceso**, perfil
  **estricto** (login 5/5 min, refresh y logout 15/5 min, escrituras 15/min, lecturas 120/min;
  escrituras sin sesión 15/min por IP). Cierra la condición de entrega. **Limitación declarada:**
  con varios workers el cupo efectivo se multiplica y los contadores se reinician al reiniciar;
  se revisa al elegir host. Registro: DEC-22, `decisions/adr/ADR-015-hardening-f1.md`. Detalle y
  pruebas: `docs/implementation/f1/04-hardening-y-ui.md`.
- [x] **Logging estructurado (13/11/2026):** una línea JSON por petición en stdout, con
  `X-Request-ID`, método, ruta sin consulta, estado y duración. No registra correos, contraseñas,
  cookies, cuerpos ni IP en claro (huella no reversible). Destino y retención de logs **sin
  decidir** para datos reales.
- [x] **Robustez operativa (14/11/2026):** `create_app()` + `lifespan`, `/health/live` y
  `/health/ready` (sin consultar Supabase a propósito), configuración fail-fast en
  `prod`/`staging`, `TrustedHostMiddleware`, OpenAPI desactivado fuera de producción y timeout
  de PostgREST. Detalle: `docs/implementation/f1/05-robustez-operativa.md`.
- [ ] **Condiciones abiertas:** DEC-19/E-6 (región y transferencia) y DEC-05 (retención). El
  primer dato real las activa. DEC-06 (ASVS nivel 2) y DEC-07 (RPO/RTO) quedaron aprobadas el
  13/11/2026. La **matriz ASVS acotada** existe en `docs/security/asvs-l2-f1.md` (16/11/2026),
  pero **no declara conformidad** y deja brechas abiertas; DEC-22 no declara conformidad.

**Evidencia:** `decisions/dec-12-material-decision.md`, `decisions/dec-12-matriz-puntuada.md`,
`decisions/adr/ADR-012-capa-de-aplicacion.md` (rechazada), `decisions/adr/ADR-013-fastapi-bff.md`
(aprobada), `docs/architecture/backend-choice.md`.

## 2) DEC-07 — RPO/RTO y política de respaldo (cerrada el 13/11/2026)

**Estado:** **Aprobada** (registro v1.4). Necesario para cerrar O-03, que sigue abierta por la
restauración en un proyecto Supabase real.

| Campo | Valor decidido | Notas |
|---|---|---|
| **RPO** | **24 h** | Máxima pérdida aceptable: un día de trabajo |
| **RTO** | **8 h** en horario laboral | Tiempo máximo para restaurar |
| **Frecuencia** | **Diaria** | Volcado en formato custom y cifrado |
| **Retención** | **30 días** | 30 copias diarias |
| **Destino fuera del proveedor** | **Sí**, sin coste | El destino concreto no está elegido; no autoriza gasto (DEC-08) |
| **Responsable** | **El propietario** | Ejecuta, verifica y conserva el volcado |
| **Volcado de roles** | **Sí**, cuando el clúster lo permita | Documental; no bloquea el volcado de datos/esquema |

**Pendiente de verificar:** qué retención de respaldos incluye el plan gratuito de Supabase. Si no
alcanza los 30 días, el volcado propio es la única garantía.

**Evidencia:** `docs/operations/o-03-respaldo-restauracion.md` · `decisions/decision-register.md`
(DEC-07)

## 3) O-03 — Restauración en proyecto Supabase real

**Estado:** Parcialmente probado. Volcado real + ensayo local con **127/127** OK. Falta restaurar en **otro proyecto Supabase** autorizado.

- [ ] **Segundo proyecto autorizado**: Sí/No. Si Sí, indicar `project ref` (solo el ref, **nunca** claves/secretos) y región.
- [ ] **Sin gasto / dentro de lo permitido**: Confirmado por el propietario.
- [ ] **Restauración ejecutada**: usando `workspace/backups/volterra-20261026-211832/volterra.dump`
- [ ] **Verificación con 127 pruebas**: `f1_rls_isolation` 65/65 + `f1_hardening` 37/37 + `f1_service_role` 25/25
- [ ] **Registro**: fecha/hora, tamaño, SHA256, exit codes, resultado de pruebas, quién ejecutó.

**Regla:** No crear nuevo proyecto. Solo usar uno ya existente y autorizado. MCP sigue en **solo lectura**; el volcado/restauración requiere credencial, pg_dump/pg_restore y ejecución local con permiso explícito.

## 4) Frontend de F1 — DEC-21 (implementado, sin desplegar)

**Estado:** **Aprobada e implementada en local.** ADR vigente:
`decisions/adr/ADR-014-frontend-jinja-htmx.md`. Stack: Jinja2 + HTMX, sesión con cookie
`HttpOnly` + CSRF, F1 en solo lectura, UI funcional mínima, español `es-CO`.

- [x] **Registro:** DEC-21 aprobada en `decisions/decision-register.md` (v1.3).
- [x] **Rutas HTML:** `/login`, `/logout`, `/auth/refresh`, `/me`, `/clubs`,
  `/clubs/{id}`, `/clubs/{id}/members`, `/platform` y páginas de error.
- [x] **Sesión:** cookies `volterra_access` y `volterra_refresh` `HttpOnly`; CSRF
  double-submit en formularios y cabecera `X-CSRF-Token`.
- [x] **Contrato de lecturas:** nombres de club, `display_name` de miembros y campos
  explícitos sin `select *`.
- [x] **Pruebas:** **76 passed, 1 warning** (12/11/2026), incluidas 27 nuevas de web,
  sesión, CSRF y servicios de lectura.
- [x] **Verificación contra Supabase:** esquema aplicado y verificado en
  `tioeoswnhwrlbovkxocd` el 12/11/2026 (preflight vacío → 7 migraciones en una transacción →
  **134/134** en las cuatro suites). Detalle: `docs/implementation/f1/03-migracion-remota.md`.
- [x] **Usuarios ficticios y seed:** creados `demo-pa@example.com` y
  `demo-coach@example.com` en `auth.users` + `auth.identities` (correo confirmado, contraseña
  ficticia) y ejecutado `supabase/seed/f1_demo.sql` (2 perfiles, 1 club, 2 pertenencias,
  1 `platform_admin`, 6 eventos). Verificado con RLS por rol.
- [x] **BFF contra Supabase:** cerrado el 12/11/2026. Con la legacy anon key en `volterra/.env`
  (GoTrue rechaza la `sb_publishable_…`), login `200`, **37/37** comprobaciones E2E del frontend
  (login, CSRF, `/me`, `/clubs`, miembros, `/platform`, refresh con rotación y logout, más
  `demo-coach` sin ámbito de plataforma). `scripts/smoke_f1.py` terminó en **SMOKE OK**. Detalle:
  `docs/implementation/f1/03-migracion-remota.md` §9.6.
- [ ] **Host y despliegue:** no autorizados. Siguen abiertos DEC-19/E-6 y la elección de host.
  Candidatos, requisitos y trabajo previo: `docs/operations/o-04-plan-host.md` (no elige proveedor).
- [x] **Escrituras de F1 (13/11/2026):** endpoints API y formularios HTML para crear/editar club,
  añadir miembro, cambiar rol y cerrar pertenencia, sobre las RPC `SECURITY DEFINER` existentes.
  CSRF obligatorio con sesión por cookie; la autorización sigue en RLS + RPC. Pruebas del BFF:
  **109 passed, 1 warning** (76 previas + 33 nuevas de escrituras). Alcance: local y datos
  ficticios; sin despliegue. Registro: DEC-21 v1.1.
- [x] **E2E de escrituras contra el BFF real (13/11/2026):** `scripts/e2e_f1_writes.py` contra
  `127.0.0.1:8011` y el Supabase del proyecto, con usuarios ficticios: **45/45 OK**. Cubre alta y
  edición de club, alta de miembro, cambio de rol, cierre de pertenencia, CSRF, negativas por rol
  y la invariante del último administrador. Deja **un club ficticio** como residuo (no se elimina
  sin aprobación). Detalle: `docs/implementation/f1/03-migracion-remota.md` §9.7.
- [ ] **Pruebas E2E y accesibilidad:** pendientes con navegador real, axe/Lighthouse y lector
  de pantalla. **Hecho el 13/11/2026:** pulido de accesibilidad, responsive y estados en
  plantillas, CSS y JS (navegación con `aria-current`, regiones de tabla con `caption` y
  `tabindex`, estados vacíos con `role="status"`, errores de formulario con `aria-invalid` y
  `aria-describedby`, confirmación de cierre de pertenencia, objetivos táctiles de 44 px,
  `prefers-reduced-motion` y región `aria-live` para HTMX). Verificado con **7 pruebas de
  interfaz** (`tests/test_web_ui.py`), no con navegador real.

## Reglas operativas

- **No desplegar.**
- **No generar costos.**
- **No exponer secretos.**
- **Solo datos ficticios** hasta nuevo aviso.
- **Commits selectivos.** Sin `git add .`
