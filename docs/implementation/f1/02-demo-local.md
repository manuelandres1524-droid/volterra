# F1 — Demo local del flujo autenticado

**Fecha:** 02/11/2026
**Estado:** guía operativa; requiere datos ficticios y credenciales locales.
**Objetivo:** verificar de extremo a extremo el backend local contra el Supabase de desarrollo.

---

## 1. Requisitos previos

- El esquema de F1 está aplicado en Supabase (`tioeoswnhwrlbovkxocd`, 12/11/2026; ver
  `03-migracion-remota.md`).
- El backend local está corriendo en `http://127.0.0.1:8000`.
- Existen dos usuarios ficticios en **Authentication → Users**:
  - `demo-pa@example.com`
  - `demo-coach@example.com`

  **Estado (12/11/2026):** creados por SQL en `tioeoswnhwrlbovkxocd` con correo
  confirmado, contraseña ficticia y fila en `auth.identities`; verificados con
  `crypt()`. La contraseña se comunica fuera del repositorio y puede restablecerse en el
  panel. `supabase/seed/f1_demo.sql` ya se ejecutó: 2 perfiles, 1 club, 2 pertenencias,
  1 `platform_admin` y 6 eventos de auditoría.

Crea o restablece las contraseñas desde el panel. No las guardes en el repositorio.

## 2. Sembrar datos ficticios

1. Abre Supabase → **SQL Editor**.
2. Pega el contenido de `supabase/seed/f1_demo.sql`.
3. Ejecútalo.

El script es idempotente y crea:

- perfil para los dos usuarios;
- `demo-pa` como `platform_admin`;
- club ficticio `Club Demo Volterra`;
- `demo-pa` como `club_admin` y `demo-coach` como `coach` del club.

Si usas otros correos, cambia las dos variables al inicio del bloque `do $$`.

## 3. Configurar el backend

Copia `.env.example` a `.env` dentro de `volterra/` y rellena **localmente**:

```dotenv
SUPABASE_URL=https://tioeoswnhwrlbovkxocd.supabase.co
SUPABASE_ANON_KEY=<anon key del proyecto>
COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=lax
```

`COOKIE_SECURE=false` es obligatorio para la demo local sobre `http://127.0.0.1:8000`.
En producción debe ser `true`. No versiones `.env` (ya está en `.gitignore`). Reinicia el backend:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

cd D:\proyectos\volterra\volterra
& "C:\Users\Jesus\AppData\Local\Temp\opencode\volterra-venv\Scripts\python.exe" -m uvicorn main:app --reload --port 8000
```

## 4. Probar el frontend

Abre `http://127.0.0.1:8000/` en el navegador. La raíz redirige a `/me`; sin sesión,
redirige a `/login`.

1. Inicia sesión con `demo-pa@example.com` y su contraseña local.
2. Comprueba `/me`: nombre visible, correo, insignia **Administrador de plataforma** y
   el club `Club Demo Volterra` con rol `club_admin`.
3. Abre `/clubs`, entra al club y revisa `/clubs/{id}/members`: deben aparecer los dos
   miembros con nombre visible.
4. Abre `/platform`: solo debe funcionar con `demo-pa`.
5. Cierra sesión con el botón **Cerrar sesión**. Debe volver a `/login` y dejar de acceder
   a `/me`.
6. Repite con `demo-coach@example.com`: no debe ver el enlace **Plataforma** ni entrar en
   `/platform` (403). En miembros solo verá su propia pertenencia y su propio perfil: RLS no
   le permite leer los perfiles de sus compañeros.
7. Con `demo-pa`, prueba las escrituras: **Crear club** en `/clubs`, **Editar club** en el
   detalle, y en **Miembros** añade un UUID, cambia un rol y cierra una pertenencia. El club
   demo conserva siempre un administrador activo: cerrar al último devuelve `400`. Con
   `demo-coach`, las acciones de gestión no aparecen y la API responde `403`.

**Sesión y CSRF**

- Los tokens viajan en cookies `volterra_access` y `volterra_refresh` con `HttpOnly`; no
  aparecen en la URL, el HTML ni `localStorage`.
- La cookie `volterra_csrf` es legible por el navegador y se envía en el campo oculto
  `csrf_token` de los formularios o en la cabecera `X-CSRF-Token`.
- Un formulario sin CSRF válido devuelve `403`.
- `app.js` renueva la sesión cada 45 minutos mientras la página está abierta. Sin JavaScript,
  la sesión dura lo que dure el access token y luego redirige a `/login`.

## 5. Ejecutar el smoke test de la API

En otra terminal, desde la raíz del repositorio:

```powershell
$env:SUPABASE_URL="https://tioeoswnhwrlbovkxocd.supabase.co"
$env:SUPABASE_ANON_KEY="<anon key>"
$env:VOLTERRA_EMAIL="demo-pa@example.com"
$env:VOLTERRA_PASSWORD="<contraseña de prueba>"
& "C:\Users\Jesus\AppData\Local\Temp\opencode\volterra-venv\Scripts\python.exe" scripts\smoke_f1.py
```

El script:

1. inicia sesión contra Supabase Auth y obtiene un `access_token`;
2. llama a `/api/v1/me/`;
3. llama a `/api/v1/clubs/me`;
4. recorre cada club y consulta `/clubs/{id}` y `/clubs/{id}/members`;
5. si el usuario es `platform_admin`, consulta `/platform/overview`.

No imprime el token ni la contraseña.

## 6. Resultado esperado

Para `demo-pa`:

- `/api/v1/me/` → `is_platform_admin: true`, `display_name` y una membership de `club_admin`;
- `/api/v1/clubs/me` → el club ficticio con `club_name`, `city` y `status`;
- `/api/v1/clubs/{id}` → datos del club con campos explícitos;
- `/api/v1/clubs/{id}/members` → dos miembros activos con `display_name`;
- `/api/v1/platform/overview` → `{"ok": true, ...}`;
- salida final: `SMOKE OK`.

Repite con `demo-coach@example.com`: debe ver el club, pero `is_platform_admin` debe ser
`false`, `/platform/overview` debe devolver 403 y la lista de miembros solo incluirá su propia
pertenencia.

### 6.1 Resultado real (12/11/2026)

Este recorrido **se ejecutó** contra `tioeoswnhwrlbovkxocd`:

| Prueba | Resultado |
|---|---|
| `scripts/smoke_f1.py` (demo-pa) | `token 200`, `/me/ 200`, `/clubs/me 200`, `/clubs/{id} 200`, `/members 200`, `/platform/overview 200` → **SMOKE OK** |
| Frontend (httpx, 37 comprobaciones) | login, CSRF, `/me`, `/clubs`, club, miembros, `/platform`, refresh con rotación, logout y `demo-coach` sin ámbito de plataforma → **37/37** |
| `pytest` del BFF | **76 passed, 1 warning** |

Detalle completo: `03-migracion-remota.md` §9.6. Las pruebas E2E con **navegador real**, axe,
Lighthouse y lector de pantalla **siguen sin ejecutarse**.

## 7. Si falla

| Síntoma | Causa probable |
|---|---|
| 503 en `/api/v1/me/` o en `/me` | La RPC no responde, el backend no se reinició tras crear `.env`, o `SUPABASE_URL`/`anon key` no son del proyecto correcto. |
| 401 | Token inválido, `SUPABASE_URL` incorrecta o algoritmo JWT no soportado. |
| 403 en `/api/v1/clubs/...` o `/clubs/...` | El usuario no tiene membership activa en el club. |
| 404 en `/api/v1/clubs/...` o `/clubs/...` | Club o membership inexistente, o RLS lo oculta. |
| 403 al enviar un formulario | Cookie CSRF ausente o token del formulario caducado; recarga la página. |
| El login vuelve a `/login` | `COOKIE_SECURE=true` sobre HTTP local: cámbialo a `false`. |
| Login con `401 Invalid API key` | `SUPABASE_ANON_KEY` es una `sb_publishable_…`: GoTrue la rechaza. Usa la legacy `anon` (`eyJ…`). |
| Error de login | Usuario no confirmado o contraseña incorrecta. |
| `429` con `Retry-After` | Límite de peticiones (DEC-22): login 5/5 min por IP, refresh/logout 15/5 min, escrituras 15/min, lecturas 120/min. Espera la ventana o reinicia el BFF para vaciar los contadores en memoria. |
| `/health/ready` devuelve `503` | Faltan `SUPABASE_URL` o `SUPABASE_ANON_KEY` en `.env`, o el proceso está apagándose. `/health/live` debe seguir en `200`. |
| `/docs` devuelve `404` | `ENABLE_DOCS=false` o `APP_ENV` es `prod`/`staging`. Es el comportamiento esperado fuera de desarrollo. |

## 8. Alcance y límites

Esta demo **incluye escrituras desde el 13/11/2026**: crear y editar club, añadir miembro, cambiar
rol y cerrar pertenencia se hacen desde la interfaz y la API FastAPI, que llaman a las RPC
`SECURITY DEFINER` ya existentes. No se añadió ninguna migración.

La interfaz **solo oculta** acciones según el rol; no autoriza. Cada lectura y cada escritura
vuelven a pasar por el JWT del usuario y RLS + RPC. El BFF solo valida formato y traduce errores.

El alta de miembro pide el UUID del usuario a mano: F1 no incluye buscador ni invitaciones.
Un administrador de club solo gestiona entrenadores.

No usar datos reales. No desplegar. No commitear `.env` ni capturas con tokens.

## 9. Siguiente paso

Si el frontend y el smoke test pasan:

1. ~~aplicar la migración remota pendiente~~ — **hecho el 12/11/2026** (`03-migracion-remota.md`);
2. ~~añadir los endpoints de escritura de F1~~ — **hecho el 13/11/2026**, con E2E real **45/45**
   (`scripts/e2e_f1_writes.py`, §9.7 de `03-migracion-remota.md`);
3. ~~probar el recorrido completo con `demo-pa` y `demo-coach`~~ — **hecho** (lecturas 37/37,
   escrituras 45/45);
4. ~~decidir el stack definitivo (DEC-12)~~ — **cerrado el 12/11/2026**: FastAPI como BFF
   (`decisions/adr/ADR-013-fastapi-bff.md`);
5. ~~decidir el frontend (DEC-21)~~ — **cerrado el 12/11/2026**: Jinja2 + HTMX y sesión por
   cookie (`decisions/adr/ADR-014-frontend-jinja-htmx.md`). El host y el despliegue siguen sin
   autorizar; plan de análisis en `docs/operations/o-04-plan-host.md`;
6. ~~cerrar el hardening mínimo~~ — **hecho el 13/11/2026** (DEC-22): límite de peticiones en
   memoria con perfil estricto y logging JSON con `X-Request-ID`
   (`decisions/adr/ADR-015-hardening-f1.md`). Con varios workers el cupo se multiplica; se revisa
   al elegir host. Quedan pendientes el host, las pruebas con navegador real y axe/Lighthouse, la
   matriz ASVS y las decisiones jurídicas (DEC-05, DEC-19/E-6).
