# F1 — Hardening del BFF y pulido de interfaz (13–14/11/2026)

**Estado:** implementado en local, sin commit, sin push y sin despliegue. Solo datos ficticios.
**Decisiones:** DEC-22 (`decisions/adr/ADR-015-hardening-f1.md`) y DEC-21 v1.5.
**Alcance acordado:** «terminar el back» = hardening mínimo (límite de peticiones + logging);
«empezar el front» = pulir F1 (accesibilidad, responsive y estados). **No** incluye F2, MFA,
recuperación de contraseña, rediseño visual ni despliegue.

---

## 1. Backend

### 1.1 Límite de peticiones

`apps/core/ratelimit.py` implementa una **ventana fija en memoria por proceso** con cerrojo y
reloj monótono. Perfil **estricto** aprobado:

| Ámbito | Clave | Cupo / ventana |
|---|---|---|
| `POST /login` | IP | 5 / 5 min |
| `POST /auth/refresh` | IP | 15 / 5 min |
| `POST /logout` | IP | 15 / 5 min |
| Escritura sin sesión | IP | 15 / 1 min |
| Escritura autenticada | `sub` | 15 / 1 min |
| Lectura autenticada | `sub` | 120 / 1 min |

- Los ámbitos anónimos se aplican en un middleware; los autenticados, en `get_auth_context`,
  **antes** de consultar Supabase.
- `X-Forwarded-For` **no se confía por defecto**. Solo se usa con
  `RATE_LIMIT_TRUST_FORWARDED_FOR=true`, tomando el último valor de la cadena.
- La respuesta es `429` con `Retry-After`: JSON en `/api/v1/` y `/auth/`; página de error en el
  resto. La cabecera se conserva en ambos casos.
- El estado se poda al alcanzar `max_keys`; si no basta, se descarta y se registra el evento.
- **No autoriza**: un `429` no sustituye a un `403`; la autorización sigue en RLS + RPC.

### 1.2 Logging estructurado

`apps/core/logging.py` escribe **una línea JSON por evento** en stdout:

```json
{"ts":"…","level":"INFO","logger":"volterra.http","message":"request","event":"request","request_id":"…","method":"GET","path":"/me","status":200,"duration_ms":12.3}
```

- `X-Request-ID` se acepta solo con forma segura (`[A-Za-z0-9._-]{8,64}`); si no, se genera y se
  devuelve en la respuesta.
- No se registran correos, contraseñas, cookies, cabeceras, cuerpos, consultas ni IP en claro.
  IP y usuario se sustituyen por una huella no reversible de 16 caracteres.
- Los rechazos por límite generan `event=rate_limited` con ámbito y `retry_after`.

### 1.3 Configuración

Nuevas variables en `apps/core/config.py` y `.env.example`: `RATE_LIMIT_ENABLED`,
`RATE_LIMIT_TRUST_FORWARDED_FOR`, los seis cupos y sus ventanas, `LOG_LEVEL` y `LOG_FORMAT`.
Los valores por defecto son el perfil estricto; no hay constantes ocultas.

## 2. Frontend

Cambios en `base.html`, `login.html`, `clubs.html`, `club_detail.html`, `members.html`,
`club_form.html`, `me.html`, `app.css` y `app.js`:

- **Navegación:** `aria-current="page"` en la sección activa; enlace «Saltar al contenido» con
  destino enfocable (`tabindex="-1"` en `<main>`).
- **Tablas:** `caption` para lectores de pantalla y contenedor `role="region"` con
  `aria-label` y `tabindex="0"` para desplazamiento por teclado.
- **Formularios:** `aria-invalid` y `aria-describedby` en el error de login; ayuda descrita para
  el UUID de miembro y el código de país; `autocomplete` e `inputmode` adecuados.
- **Acciones destructivas:** confirmación explícita al cerrar una pertenencia con `<dialog>`
  nativo (`data-confirm` + `data-confirm-action`), que aporta foco atrapado, capa superior, cierre
  con `Esc` y devolución del foco; las etiquetas incluyen el nombre del miembro. Queda
  `window.confirm` solo como respaldo si el navegador no soporta `showModal()`.
- **Estados:** vacíos con `role="status"`; región `aria-live` para anunciar la actualización de
  la lista por HTMX; `aria-busy` durante la petición.
- **Errores HTMX:** una respuesta `4xx` no sustituye el panel por una página completa; se anuncia
  el fallo y se mantiene la vista.
- **Fechas:** los `timestamptz` se convierten de UTC a `America/Bogota` antes de formatear; antes
  se mostraba el día UTC, que puede ser el siguiente.
- **CSS:** `select` con el mismo estilo que `input`, objetivos táctiles de 48 px, foco visible en
  botones y tablas, tarjetas apiladas en móvil, `prefers-reduced-motion` y
  `-webkit-text-size-adjust`.

## 3. Pruebas ejecutadas realmente

| Prueba | Resultado |
|---|---|
| `pytest` completo | **137 passed, 1 warning** (14/11/2026) |
| Nuevas de límite y logging | **21** (`tests/test_ratelimit.py`, `tests/test_logging.py`) |
| Nuevas de interfaz | **7** (`tests/test_web_ui.py`) |
| `compileall` de `apps/` y `main.py` | Sin errores |
| `git diff --check` | Sin errores de espacio |
| Comprobación manual con `TestClient` | `429` de login con `Retry-After`, CSP y `X-Request-ID`; `429` de refresh en JSON |

Cobertura de las pruebas nuevas: ventana fija, expiración, aislamiento de claves, poda,
confianza en `X-Forwarded-For`, bloqueo de login, escritura anónima, lectura autenticada por
usuario, desactivación del límite, formato JSON, descarte de campos no permitidos, huella no
reversible, saneado de `X-Request-ID`, ausencia de consulta en el registro, evento de rechazo y
las garantías de HTML servido (regiones, captions, etiquetas, estados y confirmación).

**No ejecutado:** navegador real, axe/Lighthouse, lector de pantalla, prueba de carga, varios
workers y E2E contra Supabase tras el cambio. No se declara conformidad WCAG ni ASVS.

## 4. Límites y riesgos

1. **Multi-worker:** el cupo efectivo se multiplica por el número de procesos y los contadores se
   reinician al reiniciar. Revisar al elegir host (ADR-015 §6).
2. **IP compartida:** el perfil estricto puede afectar a varias personas tras un NAT; los
   umbrales son configurables.
3. **Proxy:** sin `RATE_LIMIT_TRUST_FORWARDED_FOR`, todos los clientes comparten la IP del proxy.
4. **Logs:** destino y retención sin decidir; no usar datos reales hasta resolverlo.
5. **E2E de escrituras:** el guion hace menos de 15 escrituras por usuario, pero no se reejecutó
   tras el cambio; si se ejecuta, conviene espaciar los intentos de login (5/5 min por IP).
6. **Datos residuales:** el E2E anterior dejó un club ficticio; no se elimina sin aprobación.

## 5. Siguiente paso

1. Revisar este documento y el diff; decidir qué se commitea (sin `git add .`).
2. Elegir host y topología (DEC-19/E-6 y `docs/operations/o-04-plan-host.md`).
3. Crear la matriz ASVS `requisito → estado` (DEC-06).
4. Ejecutar pruebas con navegador real, axe/Lighthouse y lector de pantalla.
5. Solo después: valorar MFA, recuperación de contraseña y F2 (bloqueada por P-13, DEC-04,
   E-7/E-8).
