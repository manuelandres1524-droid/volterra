# O-04 · Plan de host del BFF (propuesta, sin selección ni despliegue)

**Fecha:** 13/11/2026 · **Estado:** **borrador de análisis**. No es una decisión, no elige
proveedor y no autoriza despliegue.

**Qué es:** el plan que faltaba para llevar el BFF de F1 (FastAPI + Jinja2/HTMX) a un host público
**cuando** el propietario lo autorice. Reúne hechos del artefacto, requisitos, familias de opciones,
trabajo técnico previo y bloqueos de gobernanza.

**Qué no es:** una comparación de precios cerrada ni una recomendación vinculante. Los planes
gratuitos cambian de condiciones y de cuota; toda cifra de terceros debe verificarse **en la fecha de
la decisión**, no en la de este borrador.

---

## 0. Cómo leer este documento

| Marca | Significado |
|---|---|
| **Hecho** | Comprobado en el repositorio o en documentación ya registrada del proyecto |
| **Hipótesis [H]** | Razonable pero **no verificada** en la fecha de este documento |
| **Recomendación [R]** | Propuesta del coordinador; no obliga al propietario |
| **Decisión pendiente** | Requiere aprobación humana explícita; no se asume |

Regla del proyecto: aprobar una decisión **no** cierra sus bloqueos. DEC-12 está aprobada y aun así
DEC-19/E-6 y DEC-05 siguen abiertas. Lo mismo aplica a este plan.

---

## 1. Hechos: qué hay que alojar

| Hecho | Evidencia |
|---|---|
| Un único proceso ASGI (`main:app`) servido con `uvicorn` | `volterra/main.py`, `pyproject.toml` |
| Python **≥ 3.11** | `pyproject.toml` (`requires-python`) |
| El mismo proceso sirve HTML (Jinja2), estáticos, API JSON y `/health` | `main.py` líneas 30-32 y 109-111 |
| No hay WebSockets, cron interno, colas ni workers | No existen en el árbol |
| **No hay estado local**: sesión en cookies del navegador, sin caché ni disco persistente | `apps/auth/session.py`, `apps/web/routes.py` |
| La salida a datos es **HTTPS a Supabase** (GoTrue + PostgREST); no abre PostgreSQL | `apps/integrations/supabase/per_request.py` |
| El BFF **no usa `service_role`** y no debe configurarla | ADR-013; `.env.example` |
| Configuración por variables de entorno | `apps/core/config.py`, `.env.example` |
| No hay `requirements.txt` ni lockfile | `ls` del proyecto: solo `pyproject.toml` |
| El servidor local se probó en `127.0.0.1:8011` con datos ficticios | `docs/implementation/f1/03-migracion-remota.md` §9.6 |

**Consecuencia [H]:** el artefacto es un servicio web sin estado, de un solo proceso, apto tanto para
un contenedor/proceso permanente como para un runtime serverless con adaptador. No necesita base de
datos propia, almacenamiento ni Redis.

---

## 2. Requisitos del host

`M` = obligatorio · `D` = deseable. La columna «Cómo se comprueba» evita aceptar un proveedor por
folleto.

| # | Requisito | Nivel | Por qué | Cómo se comprueba |
|---|---|---|---|---|
| 1 | HTTPS con certificado válido | **M** | Cookies `Secure`, CSRF y datos en tránsito | `curl -I` y aviso del navegador |
| 2 | Un solo origen público | **M** | `SameSite=Lax` + double-submit CSRF; sin CORS entre dominios | Cabeceras y flujo de login |
| 3 | Python 3.11+ y ASGI | **M** | `main:app` | Arranque real |
| 4 | Variables/secretos por entorno, fuera de la imagen y del repo | **M** | No exponer `SUPABASE_ANON_KEY` ni cookies | Revisión de configuración y logs |
| 5 | Salida HTTPS a Supabase | **M** | PostgREST/GoTrue | Login y lecturas |
| 6 | Health check | **M** | `/health` ya existe | `GET /health` → 200 |
| 7 | Región declarada y aceptada | **M** | DEC-19/E-6 abierta | Ficha del proveedor + DEC-19 |
| 8 | Coste **US$0/mes** | **M** | DEC-08 | Panel de facturación; sin cargos |
| 9 | Logs consultables | **D** | Diagnóstico sin volcar secretos | Prueba de error controlada |
| 10 | Proceso permanente o cold start tolerable | **D** | UX de login/HTMX | Medición de primera petición |
| 11 | Límite de tamaño y timeout de petición | **D** | Abuso y formularios | Prueba de carga simple |
| 12 | Escalado sin estado compartido | **D** | Futuro; hoy un proceso basta | Diseño (ya sin estado) |
| 13 | Rollback / suspensión | **D** | Volver atrás sin tocar datos | Procedimiento escrito |
| 14 | Sin cuenta de facturación obligatoria | **D** | Evitar cargos accidentales | Alta del proveedor |

**Nota:** «US$0» es un techo, no una autorización (DEC-08). Un plan gratuito con cuenta de
facturación obligatoria **no** cumple el espíritu del techo aunque la cuota sea 0: introduce riesgo
de cargo. Si el propietario quisiera aceptarlo, sería una decisión nueva.

---

## 3. Criterios de evaluación

Sin pesos aprobados todavía. Se ordenan por filtro, no por puntuación:

1. **Filtro de coste:** US$0 real, sin tarjeta ni cargo automático. Si falla, la opción sale.
2. **Filtro de gobernanza:** proveedor y región evaluables dentro de DEC-19/E-6 y con DPA/encargado
   identificable. Si no se puede evaluar, la opción queda **condicionada**, no aprobada.
3. **Filtro técnico:** ejecuta ASGI sin reescribir la aplicación y sirve estáticos.
4. **Criterio de operación:** esfuerzo de despliegue, logs, rollback y cold start.
5. **Criterio de salida:** portabilidad (imagen/contenedor o comando estándar) para no quedar atado.

**Recomendación [R]:** no ponderar numéricamente hasta que el propietario fije qué pesa más
(coste/operación/región). Una matriz con pesos inventados daría una falsa objetividad.

---

## 4. Familias de opciones (sin selección)

Se comparan **familias**, no productos concretos, porque las condiciones gratuitas de cada producto
cambian. Cualquier nombre es un ejemplo, no una elección.

### A. PaaS de proceso permanente con plan gratuito

Ejemplos: Render, Railway, Koyeb, Fly.io, Heroku.

- **A favor:** ejecuta `uvicorn main:app` sin adaptadores; TLS, dominio y variables de entorno
  incluidos; despliegue por Git o imagen; encaja con «un solo servicio y un solo host» (ADR-014).
- **En contra [H]:** los planes gratuitos suelen suspender el proceso por inactividad, limitar horas
  o exigir tarjeta; las condiciones cambian sin aviso; la región gratuita puede no ser elegible.
- **Riesgo de términos [H]:** uso no comercial, límites de ancho de banda y cláusulas de suspensión.
- **Coste [H]:** US$0 posible solo en el plan gratuito vigente; verificar en la fecha de decisión.

### B. Serverless de funciones

Ejemplos: Vercel (Python), AWS Lambda + Function URL/API Gateway, Azure Functions, Netlify Functions.

- **A favor:** US$0 dentro de cuota; TLS gestionado; escala a cero.
- **En contra:** el modelo no es un proceso permanente; exige adaptador ASGI (p. ej. Mangum) **no
  probado en este proyecto**; límites de duración, tamaño de respuesta y arranque en frío; los
  estáticos y el renderizado Jinja2 necesitan verificación; depuración más difícil.
- **Riesgo de términos:** Vercel Hobby está restringido a **uso no comercial** (hecho ya registrado
  en `decisions/dec-12-material-decision.md` §2). AWS/Azure suelen exigir cuenta de facturación.
- **Coste [H]:** US$0 condicionado a cuota y a la calificación de uso no comercial.

### C. Contenedor gestionado con free tier

Ejemplos: Google Cloud Run, Azure Container Apps, Fly Machines.

- **A favor:** la **misma imagen** que se prueba en local; escala a cero; TLS y secretos gestionados;
  portable a otro proveedor de contenedores.
- **En contra [H]:** casi siempre exige **cuenta de facturación** aunque la cuota sea gratuita;
  cold start; configuración de región y de límites; más pasos que un PaaS.
- **Riesgo:** un descuido de configuración puede generar cargo. Choca con DEC-08 si no hay tope duro.
- **Coste [H]:** US$0 dentro de cuota, con riesgo de cargo; verificar tope y alertas.

### D. Servidor propio (VPS)

- **A favor:** control total; región elegible; sin cold start.
- **En contra:** un VPS gratuito real no existe de forma sostenible [H]; exige parches, TLS,
  firewall, backups y monitorización. Aumenta la superficie operativa sin resolver ningún requisito
  que las familias A–C no resuelvan.
- **Recomendación [R]:** **descartar** por DEC-08 y por carga operativa. Es una recomendación, no una
  decisión.

### E. No desplegar (statu quo)

- **A favor:** cumple US$0, no abre un proveedor nuevo ni una transferencia internacional, mantiene
  la excepción de datos ficticios y no requiere autorización.
- **En contra:** no hay URL pública; F1 sigue siendo una demo local.
- **Estado:** es la situación **actual** y la única autorizada hoy.

---

## 5. Comparación resumida

`✔` cumple · `✖` no cumple · `?` por verificar en la fecha de decisión.

| Criterio | A. PaaS permanente | B. Serverless | C. Contenedor gestionado | D. VPS | E. No desplegar |
|---|---|---|---|---|---|
| ASGI sin adaptador | ✔ | ? | ✔ | ✔ | — |
| US$0 sin tarjeta | ? | ? | ✖ / ? | ✖ | ✔ |
| Sin cold start | ? | ✖ | ✖ | ✔ | — |
| Región elegible | ? | ? | ? | ✔ | — |
| Un solo servicio | ✔ | ✔ | ✔ | ✔ | ✔ |
| Esfuerzo operativo bajo | ✔ | ? | ? | ✖ | ✔ |
| Riesgo de términos | ? | ? (Vercel: no comercial) | ? | ✔ | ✔ |
| Autorizable hoy | ✖ | ✖ | ✖ | ✖ | ✔ |

La tabla **no** ordena las opciones: solo muestra qué falta verificar. Ninguna columna A–D está
autorizada.

---

## 6. Recomendación del coordinador (no vinculante)

1. **Mantener E (no desplegar)** hasta que existan DEC-19/E-6, DEC-05 y autorización expresa.
2. Cuando se autorice, **verificar primero A y C** con documentación oficial: A por simplicidad de
   proceso, C por portabilidad de imagen. Son las dos familias que no obligan a reescribir la
   entrada ASGI.
3. **B solo si** se acepta explícitamente el cold start y se prueba un adaptador ASGI en local; hoy
   no hay ninguna prueba de ese adaptador.
4. **D descartada** por coste y operación.
5. **No abrir cuentas ni aceptar términos** en nombre del propietario: el alta de un proveedor es un
   nuevo encargado de tratamiento y requiere su decisión.

---

## 7. Trabajo técnico previo al despliegue (checklist)

Nada de esto se ha ejecutado; es lo que falta **antes** de pedir autorización.

### 7.1 Configuración de producción

- [ ] `APP_ENV=production`.
- [ ] `COOKIE_SECURE=true` (hoy la demo local usa `false`).
- [ ] `CORS_ORIGINS` con **solo** el origen real; sin `localhost` ni comodines.
- [ ] `SESSION_COOKIE_SAMESITE=lax` (un solo origen).
- [ ] `SUPABASE_ANON_KEY` y demás valores por el panel del proveedor, **nunca** en el repositorio.
- [ ] `SUPABASE_SERVICE_ROLE_KEY` **no configurada** (el BFF no la lee).
- [ ] Arranque sin `--reload`, con `--proxy-headers` si hay proxy delante.
- [x] `TrustedHostMiddleware` con `TRUSTED_HOSTS` (14/11/2026). En desarrollo el valor por
  defecto es `*`; en `prod`/`staging` el arranque **falla** si sigue abierto o si falta
  `SUPABASE_URL`/`SUPABASE_ANON_KEY`.
- [x] Timeout de PostgREST (`SUPABASE_POSTGREST_TIMEOUT_SECONDS`, 15 s) y de GoTrue
  (`SUPABASE_AUTH_TIMEOUT_SECONDS`, 10 s). Los reintentos de supabase-py solo aplican a GET/HEAD.
- [ ] Tamaño máximo de formulario [R].
- [x] Endpoints de salud: `/health/live` (proceso vivo) y `/health/ready` (configuración esencial
  presente). El readiness **no** consulta Supabase a propósito.

### 7.2 Cadena de suministro

- [ ] **Lockfile**: hoy no existe. Decidir herramienta (`pip-compile`, `uv lock` u otra) antes de
  fijar versiones. Es una decisión de herramienta, no se toma aquí.
- [ ] Fijar versión de Python y de dependencias para que el host no resuelva distinto que local.
- [ ] Imagen reproducible o build declarado.

### 7.3 Seguridad y operación

- [ ] **Rotar la `sb_secret_…` filtrada** (acción del propietario; aunque el BFF no la use).
- [x] **Límite de peticiones** en login y escrituras (DEC-22, 13/11/2026). Limitación: en memoria
  por proceso; se revisa al elegir topología multi-worker.
- [ ] **MFA y recuperación de contraseña**: no implementados; decidir si entran en F1.
- [x] Logs sin tokens, cookies, correos ni cuerpos de formulario (DEC-22). Destino y retención de
  logs siguen sin decidir para datos reales.
- [ ] Matriz ASVS v5.0.0 nivel 2 (`requisito → estado`): no existe (DEC-06).
- [x] **Documentación OpenAPI** desactivada fuera de producción (`ENABLE_DOCS`); en local sigue
  disponible en `/docs` y `/openapi.json`.
- [ ] Historial de migraciones (`supabase_migrations.schema_migrations`): no existe; decidir entre
  registrarlo o reconstruirlo con `supabase db push`.
- [ ] Procedimiento de rollback: revisión anterior o suspensión del servicio.
- [ ] E2E con navegador real, axe/Lighthouse y lector de pantalla: pendientes.

### 7.4 Verificación local con configuración de producción

Antes de tocar un host remoto se puede repetir el E2E en local con `COOKIE_SECURE=true`, un origen
único y sin `--reload`. Es una prueba local, no un despliegue.

---

## 8. Bloqueos de gobernanza (no técnicos)

| Bloqueo | Estado | Efecto sobre el host |
|---|---|---|
| **DEC-19 / E-6** — región y transferencia internacional | Abierta; requiere asesoría jurídica | No se puede fijar proveedor ni región como conformes |
| **DEC-05 / E-4** — conservación y retención | Abierta; requiere asesoría jurídica | Condiciona logs, auditoría y datos en el host |
| **Elección de host** | No decidida | Este documento no la decide |
| **Autorización de despliegue** | No otorgada | Sin ella no se crea ningún recurso remoto |
| **DEC-08** — techo US$0 | Aprobada | Cualquier plan o cuenta con cargo exige decisión nueva |
| **Datos ficticios** | Regla vigente | El primer dato real invalida la excepción y activa E-4/E-6 |
| **Proveedor como encargado (DPA/subencargados)** | Registro incompleto | Un host nuevo añade un encargado que hay que declarar |

---

## 9. Plan de verificación (solo si se autoriza)

No ejecutado. Serviría para aceptar o rechazar el host elegido.

1. Desplegar en el plan gratuito autorizado, en la región autorizada, **sin datos reales**.
2. Comprobar TLS, cabeceras de seguridad, `Cache-Control: no-store` y `/health` → 200.
3. Verificar cookies `HttpOnly` + `Secure` + `SameSite=Lax` y CSRF double-submit.
4. Ejecutar `scripts/smoke_f1.py` contra la URL.
5. Repetir el E2E de sesión/lecturas y el de escrituras con usuarios ficticios.
6. Pruebas negativas: sin sesión → 303/401; CSRF inválido → 403; club ajeno → 404; `/platform` sin
   rol → 403; `anon` → `42501`.
7. Probar límite de peticiones y timeout.
8. Revisar logs en busca de secretos y datos personales.
9. Ejecutar axe/Lighthouse y una pasada con lector de pantalla.
10. Registrar fecha, proveedor, región, coste real (US$0), códigos de salida y resultado.
11. Probar rollback y dejar el servicio suspendido o en la revisión anterior si algo falla.

---

## 10. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Elegir host por entusiasmo técnico sin cerrar DEC-19/E-6 | Transferencia internacional sin evaluar | Mantener el bloqueo; este plan no elige |
| Plan gratuito que suspende el proceso | Login lento o caído | Medir cold start; preferir proceso permanente si el propietario lo acepta |
| Cuenta de facturación con cuota gratuita | Cargo accidental | Exigir tope duro o descartar la opción |
| Condiciones de uso que cambian | Incumplimiento sobrevenido | Revisar términos en la fecha de decisión y registrar la versión |
| Secretos en el panel o en logs | Exposición | Variables de entorno, logs filtrados, rotación |
| Deriva entre local y host | Fallo en producción | Lockfile, misma versión de Python, misma configuración |
| Proveedor nuevo sin DPA | Brecha de gobernanza | Declararlo como encargado antes de usarlo |
| Desplegar con datos ficticios y luego cargar reales sin cambiar nada | Se activa E-4/E-6 sin control | Bandera explícita y revisión antes del primer dato real |

---

## 11. Preguntas abiertas para el propietario

1. ¿VOLTERRA sigue siendo **no comercial**? Condiciona Vercel Hobby y otros planes gratuitos.
2. ¿Autoriza **abrir cuenta** en un proveedor gratuito? Aunque sea US$0, es un encargado nuevo.
3. ¿Acepta una **cuenta de facturación** con tope US$0, o se descarta por riesgo de cargo?
4. ¿Prefiere **proceso permanente** (sin cold start) o acepta **escalado a cero**?
5. ¿Qué **región** sería aceptable? Sin DEC-19/E-6 no se puede declarar conforme.
6. ¿**Dominio propio** o subdominio del proveedor?
7. ¿Quién **opera** el host (despliegue, logs, rollback) y en qué ventana?
8. ¿El **límite de peticiones**, MFA y recuperación de contraseña entran en F1 o se posponen?

---

## 12. Fuentes y revisión

**Hechos del proyecto:** `volterra/main.py`, `volterra/pyproject.toml`, `volterra/apps/core/config.py`,
`volterra/.env.example`, `docs/implementation/f1/03-migracion-remota.md`,
`decisions/adr/ADR-013-fastapi-bff.md`, `decisions/adr/ADR-014-frontend-jinja-htmx.md`.

**Decisiones:** DEC-08 (US$0), DEC-12 (FastAPI), DEC-21 (un solo servicio), DEC-06 (ASVS L2),
DEC-07 (respaldo), DEC-19/E-6 y DEC-05/E-4 (abiertas).

**Términos de terceros:** `decisions/dec-12-material-decision.md` §2 (Vercel Hobby, no comercial).
El resto de condiciones gratuitas **no** se ha verificado para este documento.

**Revisión:** antes de cualquier despliegue, o el **13/02/2027**, lo que ocurra primero. Si cambia el
stack, el número de servicios o el techo de coste, se reescribe.
