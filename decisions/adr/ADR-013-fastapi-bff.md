# ADR-013 — FastAPI como BFF de VOLTERRA

**Estado:** **Aprobada** por el propietario el 12/11/2026. Cierra DEC-12.
**Fecha:** 12/11/2026 · **Versión:** 1.0 · **Sustituye a:** ADR-012 (opción B, rechazada).
**Relacionado:** DEC-06, DEC-07/O-03, DEC-08, DEC-12, DEC-19/E-6.
**Insumo:** `decisions/dec-12-matriz-puntuada.md`, `decisions/dec-12-material-decision.md`,
`docs/architecture/backend-choice.md` (elección provisional del 31/10/2026) y el código existente en
`volterra/apps/`.

> Este documento registra una decisión de arquitectura. **No autoriza despliegue, contratación,
> gasto ni acceso a datos reales.** Las condiciones jurídicas y operativas siguen abiertas.

---

## 1. Contexto

DEC-12 estaba sin decidir. La matriz puntuada comparó cuatro opciones y recomendó la **B**
(estático + PostgREST) con 4,06 frente a 3,96 de A, en empate técnico. La opción **D**
(Python/FastAPI) obtuvo 2,58 y quedó eliminada por el filtro de seguridad: la variante puntuada
abría una conexión directa como rol propietario, lo que anula RLS, las guardas de las RPC y la
atribución de auditoría. **[H]**

Desde el 31/10/2026 existe, sin embargo, un backend FastAPI **provisional** documentado en
`docs/architecture/backend-choice.md`, y código en `volterra/apps/` que **no** usa conexión directa
ni `service_role`: recibe el JWT del usuario, crea un cliente por petición con la clave publicable y
propaga el token a PostgREST (`volterra/apps/integrations/supabase/per_request.py`). La autorización
efectiva sigue en Postgres (RLS + RPC). **[H]**

El propietario decidió el 12/11/2026 **ratificar FastAPI como BFF**. Esta ADR registra esa
decisión y sus condiciones; no la justifica por la matriz, porque la variante aprobada no fue la
variante puntuada. **[H]**

## 2. Decisión

**Adoptar FastAPI (Python 3.11+) como capa de aplicación en patrón BFF (Backend-for-Frontend),
delgada y subordinada a la base de datos.**

Invariantes de la decisión:

1. **Identidad del usuario, no del servidor.** Cada petición usa el JWT del usuario y un cliente
   PostgREST por petición con la clave publicable. El backend no dispone de una identidad propia
   con privilegios sobre los datos. **[H]**
2. **`service_role` prohibida en todo camino de usuario.** No se usa en peticiones, tareas,
   *scripts* ni *bundles*. La clave secreta no puede ser la vía para resolver un flujo; si un flujo
   la necesita, se detiene y se abre una decisión nueva. **[R]**
3. **Sin conexión directa como rol propietario.** El backend no abre conexiones SQL con
   credenciales de propietario ni ejecuta DDL/DML directo. Las escrituras de dominio pasan por las
   RPC existentes; las lecturas por PostgREST con RLS. **[H]**
4. **La autoridad de autorización sigue en Postgres.** RLS `enable`+`force`, políticas por club y
   guardas de las RPC son el control efectivo. Las guardas del BFF son defensa en profundidad y
   mapeo de errores, **nunca** el único control. **[H]**
5. **El BFF no duplica reglas de dominio.** Valida forma, mapea claims y errores, y compone
   respuestas. No reimplementa permisos, transiciones de estado, auditoría ni reglas de negocio ya
   probadas en `app.*`/RPC. **[R]**
6. **Sin privilegios elevados compartidos.** No hay cliente global con token de usuario ni caché de
   identidad entre peticiones. **[H]**
7. **US$0/mes (DEC-08).** La elección no autoriza ningún servicio de pago. El host del BFF no está
   elegido y el despliegue no está autorizado. **[H]**

## 3. Relación con la matriz y con ADR-012

- **ADR-012 queda rechazada** en su propuesta de opción B. Su análisis se conserva como evidencia;
  no se reescribe la historia ni se le atribuye una aprobación que no tuvo. **[H]**
- **La variante aprobada (D-BFF) no fue puntuada.** La matriz puntuó D como conexión directa con
  rol propietario (2,58, eliminada). Por tanto, el total de la matriz **no avala** esta decisión ni
  puede citarse como si lo hiciera. **[H]**
- La decisión es un **acto del propietario** (N-00). En la fuente no consta justificación escrita;
  este documento no la inventa. **[H]**
- Se registra una **desviación declarada** respecto de la recomendación del ADR-012 y del empate
  técnico A/B. La revisión de la matriz sigue siendo el insumo para recalcular si cambian las
  condiciones. **[R]**

## 4. Consecuencias

**Positivas**
- Permite reutilizar el código Python ya escrito y añadir endpoints de escritura sobre las RPC
  probadas, sin tocar migraciones.
- Mantiene una única frontera de autorización efectiva (Postgres) y una superficie de secretos
  acotada a la clave publicable.
- Facilita validación de entrada, mapeo uniforme de errores, cabeceras de seguridad y límites de
  peticiones en servidor, si se implementan.
- El backend es reversible: se puede retirar sin modificar el esquema ni las RPC.

**Negativas**
- Introduce un servidor que **puede** alojar `service_role`; convierte una invariante estructural
  (opción B) en disciplina verificable. Es el riesgo principal de esta decisión.
- Duplica parte de la verificación de permisos y puede derivar de las RLS si se añaden reglas en
  Python. Mitigación: prohibir reglas de dominio en el BFF y probar los caminos negativos en SQL.
- Añade operación y hosting: el host gratuito, los logs y la disponibilidad no están resueltos.
- No hay límite de peticiones implementado todavía; queda como condición de entrega, no como hecho.
  Las cabeceras de seguridad y `Cache-Control: no-store` ya se aplican a `/api/v1`.
  **(Superado el 13/11/2026: DEC-22 y ADR-015. Ver también §9.)**
- **No cierra ningún bloqueo:** DEC-06 (ASVS), DEC-07/O-03 (respaldo), DEC-19/E-6 (región y
  transferencia) y DEC-05 (retención) siguen abiertos. El primer dato real los activa.

## 5. Condiciones de validez

Si alguna deja de cumplirse, esta ADR queda suspendida y DEC-12 vuelve a revisión:

1. `service_role` no aparece en ningún camino de usuario, ni en el código, ni en el artefacto
   desplegado. `SUPABASE_SERVICE_ROLE_KEY` debe eliminarse de la configuración o demostrarse
   inalcanzable.
2. La autorización efectiva sigue en RLS + RPC; las pruebas negativas de aislamiento y de rol
   siguen en verde.
3. El BFF no ejecuta SQL directo ni usa credenciales de propietario.
4. El coste se mantiene en US$0/mes (DEC-08).
5. El BFF no asume reglas de dominio ni sustituye la auditoría de la base.
6. DEC-06 no fija un nivel ASVS que exija una arquitectura incompatible con esta capa.
7. El MVP sigue sin requerir tareas en segundo plano, webhooks ni procesamiento de archivos. Si
   F17/F18 los exigen, se abre una decisión nueva.

## 6. Disparadores de revisión

- **D-1.** Cualquier intento de resolver un flujo con `service_role`: **detención**, no revisión.
- **D-2.** Necesidad de conexión directa a la base o de DDL/DML desde el backend.
- **D-3.** Aparición de F17 (archivos con procesamiento) o F18 (correo/invitaciones).
- **D-4.** El host del BFF deja de ser gratuito o introduce condiciones no evaluadas.
- **D-5.** DEC-06 fija ASVS L2/L3 y exige controles que esta capa no pueda cumplir.
- **D-6.** E-6/DEC-19 impone residencia o condiciones de transferencia incompatibles.
- **D-7.** Dos sprints muestran deriva entre las guardas del BFF y las RLS.
- **D-8.** Q-03 cambia de orden de magnitud.
- **D-9.** Fecha de revisión propuesta: **12/02/2027**, o antes si se cumple un disparador.

## 7. Criterios de aceptación de la primera entrega (no ejecutados)

- Las 127 comprobaciones SQL existentes siguen en verde sin modificar migraciones aplicadas.
- Los endpoints de escritura solo llaman a RPC existentes; no hay SQL directo ni `service_role`.
- Prueba negativa: un JWT de otro club no lee ni escribe datos ajenos.
- Prueba negativa: `anon` no lee `platform_admins` ni ejecuta funciones no expuestas.
- El backend rechaza `role=service_role` y tokens sin emisor/audiencia esperados.
- El artefacto desplegado no contiene la cadena de la clave secreta.
- No se despliega ni se conecta a datos reales hasta cerrar los bloqueos aplicables.

## 8. Evidencia

**Hechos comprobados**
- `volterra/apps/integrations/supabase/per_request.py` — cliente por petición con
  `SUPABASE_ANON_KEY` y `postgrest.auth(access_token)`; sin `service_role`.
- `volterra/apps/auth/deps.py` — validación del JWT y verificación de permisos vía RPC
  `fn_is_platform_admin`; error `503` si la RPC no está disponible.
- `volterra/apps/core/security.py` — validación de algoritmo, `exp`, `iss`, `aud`, `sub`; rechazo
  explícito de `role=service_role` y de roles distintos de `authenticated`; configuración
  incompleta o JWKS no disponible falla cerrado con `503`. Un token malformado sigue siendo `401`
  aunque falte configuración.
- `volterra/apps/core/config.py` — `SUPABASE_SERVICE_ROLE_KEY` eliminada de `Settings`; CORS
  acepta lista JSON o valores separados por comas y rechaza `*`.
- `volterra/main.py` — cabeceras `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`,
  `Permissions-Policy` y `Cache-Control: no-store` en `/api/v1`.
- `docs/architecture/backend-choice.md` — elección del 31/10/2026, ratificada el 12/11/2026.
- `decisions/dec-12-matriz-puntuada.md` — puntuaciones y filtros del 26/10/2026.
- `decisions/adr/ADR-012-capa-de-aplicacion.md` — propuesta de opción B, rechazada.
- `supabase/README.md` — 6 migraciones aplicadas, 5 tablas con RLS `enable`+`force`, 127/127
  comprobaciones SQL documentadas.

**Hipótesis (no verificadas en esta sesión)**
- Existe un host gratuito para FastAPI que admite el uso previsto y mantiene US$0/mes.
- El volumen de 1–3 clubes y menos de 100 atletas cabe en las cuotas gratuitas.
- Las guardas del BFF no derivarán de las RLS si se limita a mapear claims y errores.

**Pruebas ejecutadas para este documento**
- `pytest` completo del BFF: **49 passed, 1 warning** (`2026-11-12`, Python 3.12, dependencias en
  `/tmp/opencode/volterra-deps`; el warning es una deprecación de `starlette.testclient`).
- Cobertura añadida: JWT válido, `service_role`, `anon`, `refresh_token`, rol y `sub` ausentes,
  `aud` ausente, emisor incorrecto, token expirado, configuración sin emisor/audiencia, HS256 sin
  secreto, algoritmo no permitido, token malformado, CORS (lista JSON, comas, `*` rechazado),
  ausencia de `SUPABASE_SERVICE_ROLE_KEY` en `Settings`, cabeceras de seguridad, `no-store` y
  mapeo `401/503` en `deps`.
- No se ejecutaron pruebas contra Supabase. No se aplicaron migraciones remotas, no se desplegó
  nada y no se accedió a datos reales. La migración
  `20261102120000_f1_is_platform_admin.sql` sigue pendiente de aplicar en el proyecto remoto; sin
  ella, las peticiones autenticadas devuelven `503`.
- Validación SQL local (12/11/2026): PostgreSQL 16.15 desechable con `auth` y roles simulados,
  siete migraciones aplicadas y **134/134** comprobaciones (65 + 37 + 25 + 7). No sustituye la
  ejecución remota: no reproduce los roles, ACL ni esquemas administrados de Supabase.

## 9. Actualización posterior (14/11/2026)

Se implementaron condiciones **operativas** de esta ADR sin cambiar la decisión ni sus
invariantes:

- `main.py` expone `create_app()` y un `lifespan` que valida configuración al arrancar, marca
  readiness y libera la caché JWKS al apagar.
- `/health/live` (proceso vivo) y `/health/ready` (configuración esencial presente). El readiness
  **no** consulta Supabase a propósito.
- En `prod`/`staging` el arranque falla si faltan `SUPABASE_URL`/`SUPABASE_ANON_KEY`, si
  `COOKIE_SECURE=false`, si `TRUSTED_HOSTS` contiene `*` o si solo se permite HS256 sin secreto.
- `TrustedHostMiddleware` con `TRUSTED_HOSTS`; OpenAPI/Swagger desactivados fuera de producción
  salvo `ENABLE_DOCS=true`.
- Cliente Supabase por petición con timeout de PostgREST (`SUPABASE_POSTGREST_TIMEOUT_SECONDS`).
  Los reintentos de supabase-py solo aplican a `GET`/`HEAD`, así que no duplican escrituras.

Evidencia y límites: `docs/implementation/f1/05-robustez-operativa.md`. `pytest`: **157 passed,
1 warning** (14/11/2026), incluidas 20 pruebas nuevas.

**No autoriza** despliegue, host, datos reales ni gasto, y **no cierra** DEC-05, DEC-06 ni
DEC-19/E-6. El límite de peticiones y el logging estructurado siguen en ADR-015 (DEC-22).

---

## 10. Actualización posterior (14/11/2026): estructura interna

Refactor de implementación que **no cambia la decisión, los invariantes ni el contrato con la
base de datos**:

- **Errores de dominio:** `apps/core/errors.py` define una taxonomía con `code` estable y las
  únicas tablas `STATUS_BY_CODE` / `TITLE_BY_CODE`. Servicios y guardas dejan de conocer HTTP;
  `main.py` traduce una sola vez a JSON (`{"detail","code"}`) o a HTML (`error.html`, 401 → login).
  El middleware de límite usa el mismo traductor. Se eliminaron `WriteError`,
  `DataUnavailableError` y `AuthServiceError`.
- **Composición:** `apps/integrations/supabase/deps.py` reutiliza un solo cliente por petición
  (`request.state.data_client`). Se eliminó `volterra/integrations/`, cliente global sin identidad
  y sin uso, que contradecía el invariante 6.
- **Rutas web:** `apps/web/routes.py` (552 líneas) se dividió en un paquete por área y
  `apps/web/viewmodels.py` declara los datos que consume cada plantilla. Las 17 rutas y su orden
  se conservan.
- **Autoridad:** RLS + RPC sigue siendo la única autoridad. El refactor no añade permisos ni
  consultas nuevas.

Evidencia: `docs/implementation/f1/06-arquitectura-backend.md`. `pytest`: **177 passed, 1 warning**
(14/11/2026), incluidas 21 pruebas nuevas de errores y composición. **No se desplegó** y no se
verificó ningún host; Vercel sigue sin configuración ni proyecto en el repositorio.

**No autoriza** despliegue, host, datos reales ni gasto, y **no cierra** DEC-05, DEC-06 ni
DEC-19/E-6. El límite de peticiones y el logging estructurado siguen en ADR-015 (DEC-22).
