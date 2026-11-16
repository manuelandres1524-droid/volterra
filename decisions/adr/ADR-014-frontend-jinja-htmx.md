# ADR-014 — Frontend de F1 con Jinja2 + HTMX y sesión por cookie

**Estado:** **Aprobada** por el propietario el 12/11/2026. Cierra DEC-21.
**Fecha:** 12/11/2026 · **Versión:** 1.0 · **Sustituye a:** —
**Relacionado:** DEC-08, DEC-12, DEC-21, DEC-06, DEC-19/E-6.
**Insumo:** plan de frontend presentado el 12/11/2026, `decisions/adr/ADR-013-fastapi-bff.md`,
`docs/implementation/f1/02-demo-local.md` y el código de `volterra/apps/`.

> Este documento registra una decisión de arquitectura y su primera entrega. **No autoriza
> despliegue, contratación, gasto, escrituras de dominio ni acceso a datos reales.** Las
> condiciones jurídicas y operativas siguen abiertas.

---

## 1. Contexto

El BFF FastAPI expone lecturas de F1: identidad, clubes, detalle de club, miembros y un resumen
de plataforma. No existía frontend ni stack de presentación aprobado. La demo exigía llamadas
manuales o `scripts/smoke_f1.py`. **[H]**

Las restricciones vigentes son: US$0/mes (DEC-08), solo datos ficticios, sin despliegue
autorizado, autorización efectiva en RLS + RPC (ADR-013) y migración remota pendiente
`20261102120000_f1_is_platform_admin.sql`. Sin esa migración, cualquier pantalla autenticada
recibe `503`. **[H]**

El propietario aprobó el plan con la respuesta «Apruebo»: **Jinja2 + HTMX**, **cookie
`HttpOnly` + CSRF**, **F1 en solo lectura primero**, **UI funcional mínima**, **español
`es-CO`** y **navegadores modernos**. **[H]**

## 2. Decisión

**Adoptar Jinja2 + HTMX servido por el mismo FastAPI, con sesión en cookies `HttpOnly` y
protección CSRF, para las páginas de F1 en solo lectura.**

Invariantes:

1. **Un solo servicio y un solo host.** El frontend se renderiza en el BFF; no hay SPA ni
   segundo despliegue. **[H]**
2. **El navegador nunca recibe el token.** El access token y el refresh token viajan en cookies
   `HttpOnly`; la cookie de CSRF es legible y se usa con el patrón double-submit. **[H]**
3. **La UI no autoriza.** El rol solo decide qué enlaces y acciones se muestran. Cada lectura
   vuelve a pasar por el JWT del usuario, PostgREST y RLS + RPC. **[H]**
4. **Solo lectura en esta entrega.** Crear club, añadir miembro, cambiar rol y cerrar
   pertenencia siguen fuera: no existen endpoints de escritura en el BFF. **[H]**
5. **Sin reglas de dominio en Python.** Los servicios de lectura componen respuestas y evitan
   `select *`, pero no reimplementan permisos, estados ni auditoría. **[R]**
6. **Sin terceros en tiempo de ejecución.** HTMX 2.0.4 se sirve localmente desde
   `apps/web/static/`; no hay CDN, analítica ni fuentes externas. **[H]**
7. **Español `es-CO`, interfaz funcional mínima y navegadores modernos.** Sin branding ni
   sistema de diseño aprobado. **[H]**
8. **US$0/mes (DEC-08).** La decisión no autoriza hosting ni servicios de pago. **[H]**

## 3. Alternativas descartadas

| Alternativa | Motivo para no elegirla en F1 |
|---|---|
| SPA React + TypeScript + Vite | Segundo servicio/host, CORS y token accesible desde JavaScript; más piezas para una demo de solo lectura. |
| Next.js | Duplica la capa servidor que ya es el BFF; otro host y más complejidad. |
| SvelteKit/Astro | Menos habitual en el proyecto y no resuelve por sí solo la sesión. |
| Token en `localStorage` | Expone el token a XSS y contradice el patrón BFF. |
| Token solo en memoria | Pierde la sesión al recargar; aceptable en una demo, no como base. |
| Cookie de sesión con estado en servidor | Requeriría almacén de sesiones y otra dependencia; las cookies de token firmadas por Supabase bastan para F1. |

## 4. Diseño de sesión y CSRF

**Cookies**

| Cookie | Contenido | `HttpOnly` | Uso |
|---|---|---|---|
| `volterra_access` | access token de Supabase | Sí | Autenticación del BFF. |
| `volterra_refresh` | refresh token de Supabase | Sí | Renovación de sesión. |
| `volterra_csrf` | token aleatorio | No | Double-submit en formularios y cabecera. |

Las cookies usan `SameSite=Lax`, `Secure` configurable (`COOKIE_SECURE`) y `Path=/`. En local
sobre HTTP debe ponerse `COOKIE_SECURE=false`; el valor por defecto es `true`.

**Flujo**

1. `GET /login` emite la cookie CSRF y muestra el formulario.
2. `POST /login` valida CSRF, llama a Supabase Auth y, si es correcto, fija las cookies de
   sesión, rota el CSRF y redirige a `next_url` (solo rutas internas).
3. `POST /logout` valida CSRF, revoca la sesión en Supabase si es posible y borra las cookies.
4. `POST /auth/refresh` valida la cabecera `X-CSRF-Token`, renueva con el refresh token y
   actualiza las cookies. Un pequeño `app.js` lo invoca cada 45 minutos mientras la página
   está abierta.
5. Las páginas HTML usan `get_auth_context`, que acepta `Authorization: Bearer` o la cookie.
   La cabecera tiene prioridad; una cabecera malformada no cae a la cookie.

**CSRF**

- Formularios: campo oculto `csrf_token` comparado con la cookie en tiempo constante.
- HTMX y refresh: cabecera `X-CSRF-Token`.
- El token CSRF se rota al iniciar y cerrar sesión.
- `next_url` rechaza URLs externas, `//`, barras invertidas y saltos de línea.

## 5. Alcance de la primera entrega

| Ruta | Contenido | Autorización |
|---|---|---|
| `/login` | Correo y contraseña; sin registro público | Pública |
| `/me` | Identidad, nombre visible, correo, insignia de plataforma y clubes con rol | Autenticado |
| `/clubs` | Clubes con pertenencia activa | Autenticado |
| `/clubs/{id}` | Nombre, ciudad, país, estado y alta | `club_admin`/`coach` del club o `platform_admin` |
| `/clubs/{id}/members` | Miembros activos visibles según RLS | `club_admin`/`coach` del club o `platform_admin` |
| `/platform` | Resumen mínimo | `platform_admin` |
| `*` | Error 404/403/503 en HTML | — |

**HTMX** se usa en el botón «Actualizar lista» de miembros (`hx-get` + `hx-select`). El resto
son enlaces y formularios HTML normales; no se fuerza HTMX donde no aporta.

**Contrato de lecturas**

- `/clubs/me` devuelve `club_name`, `city` y `status` además de `club_id`, `role` y
  `started_at`; evita N+1 y UUID ilegibles.
- `/clubs/{id}` usa campos explícitos, sin `select *`.
- `/clubs/{id}/members` devuelve `display_name` cuando RLS permite ver el perfil. Si no,
  `display_name` es `null` y la UI muestra «Miembro del club».
- Un entrenador solo ve su propia pertenencia y su propio perfil; la página lo declara.

## 6. Consecuencias

**Positivas**

- Un solo servicio, un solo host y menos superficie de ataque.
- El token no queda accesible a JavaScript; el CSRF cubre formularios y refresh.
- Reutiliza el JWT del usuario y RLS; no introduce `service_role`.
- Los servicios de lectura eliminan N+1 y `select *` sin cambiar migraciones.
- La UI se puede probar con `TestClient` y HTML renderizado, sin navegador ni Supabase.

**Negativas**

- HTML acoplado al BFF y menos interactividad que una SPA.
- La renovación automática depende de JavaScript; sin él, la sesión dura lo que dure el access
  token y luego redirige a `/login`.
- No hay límite de peticiones, MFA ni recuperación de contraseña en esta entrega.
- La migración remota pendiente impide probar el flujo real contra Supabase.
- Sigue sin haber branding ni sistema de diseño.

## 7. Condiciones de validez

Si alguna deja de cumplirse, esta ADR queda suspendida y DEC-21 vuelve a revisión:

1. El token no aparece en HTML, JavaScript, URL ni logs.
2. Las cookies de token siguen siendo `HttpOnly` y el CSRF se valida en todo POST.
3. La UI no autoriza: RLS + RPC siguen siendo la autoridad y las pruebas negativas pasan.
4. No se añaden escrituras de dominio sin endpoints y autorización expresa.
5. No se introduce `service_role`, CDN, analítica ni servicio de pago.
6. El coste sigue en US$0/mes (DEC-08).
7. La migración remota se aplica antes de probar contra Supabase.

## 8. Disparadores de revisión

- **D-1.** Se necesita una SPA o una interactividad que Jinja2 + HTMX no cubra con claridad.
- **D-2.** Se añaden escrituras de F1 y hay que revisar CSRF, idempotencia y errores.
- **D-3.** Se elige host o se autoriza despliegue (DEC-19/E-6, DEC-06).
- **D-4.** Aparece F17 (archivos) o F18 (correo/invitaciones).
- **D-5.** Se exige MFA, recuperación de contraseña o sesiones con estado.
- **D-6.** Dos sprints muestran deriva entre la UI y RLS.
- **D-7.** Fecha de revisión propuesta: **12/02/2027**, o antes si se cumple un disparador.

## 9. Criterios de aceptación

**Ejecutados**

- `pytest` completo del BFF: **76 passed, 1 warning** (12/11/2026, Python 3.12, dependencias en
  `/tmp/opencode/volterra-deps`). El warning es una deprecación de `starlette.testclient`.
- CSRF: falta o token incorrecto devuelve `403`; login correcto rota el token y fija cookies
  `HttpOnly`; logout exige CSRF y borra cookies; refresh exige cabecera y refresh token.
- Sesión: sin cookie, `/me`, `/clubs` y `/platform` redirigen a `/login`; con cookie válida se
  renderizan; `/platform` devuelve `403` para un usuario que no es `platform_admin`.
- Aislamiento de UI: un club fuera de las pertenencias devuelve `403`; la página de miembros no
  muestra correos ni perfiles no devueltos por RLS.
- Cabecera malformada con cookie válida devuelve `401`: no se mezclan identidades.
- Cabeceras: CSP `default-src 'self'`, `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Permissions-Policy` y `Cache-Control: no-store`.
- Lecturas: los servicios piden campos explícitos, componen nombres de club y `display_name`,
  y envuelven fallos de PostgREST en `503`.
- Redirección segura: `next_url` externo, `//`, barra invertida y salto de línea se rechazan.

**No ejecutados**

- Pruebas contra el proyecto Supabase remoto: no hay credenciales de escritura ni migración
  aplicada en esta sesión.
- Pruebas E2E con navegador real, axe/Lighthouse y lectores de pantalla.
- Pruebas de carga, límite de peticiones y renovación tras expiración real del token.
- Despliegue: no autorizado y sin host elegido.

## 10. Evidencia

**Archivos**

- `volterra/apps/auth/session.py` — cookies, CSRF, login, refresh, logout y mapeo de errores.
- `volterra/apps/auth/deps.py` — `Bearer` o cookie, con prioridad de la cabecera.
- `volterra/apps/web/routes.py` — rutas HTML, redirección segura y formularios.
- `volterra/apps/web/templates.py` y `apps/web/templates/` — plantillas y filtros.
- `volterra/apps/web/static/` — CSS, JS de refresh, HTMX 2.0.4 y su licencia.
- `volterra/apps/services/f1_reads.py` — lecturas compartidas sin `select *`.
- `volterra/apps/api/v1/endpoints/` — API JSON usando los mismos servicios.
- `volterra/main.py` — montaje de estáticos, CSP y errores HTML/JSON.
- `volterra/tests/test_web_session.py` y `volterra/tests/test_f1_reads.py` — 27 pruebas nuevas.
- `volterra/pyproject.toml` — dependencia `jinja2>=3.1.4` (ya existía `python-multipart`).

**Limitaciones**

- La simulación de Supabase en pruebas usa clientes falsos; no sustituye RLS real.
- La migración `20261102120000_f1_is_platform_admin.sql` sigue pendiente en remoto.
- No se accedió a datos reales, no se desplegó y no se hizo commit ni push.
