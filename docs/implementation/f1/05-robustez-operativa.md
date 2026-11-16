# F1 — Robustez operativa del BFF (14/11/2026)

**Estado:** implementado en local, sin commit, sin push y sin despliegue. Solo datos ficticios.
**Decisiones de referencia:** ADR-013 (FastAPI como BFF), DEC-22 (hardening), DEC-08 (US$0/mes).
**Naturaleza:** implementación de condiciones ya aprobadas. **No crea una decisión nueva** ni elige
host, proveedor, tecnología o servicio de pago.

---

## 1. Qué se implementó

### 1.1 App factory y ciclo de vida

`main.py` expone `create_app()` y mantiene `app = create_app()` para no romper imports existentes.

- `lifespan` valida la configuración al arrancar, marca `app.state.ready = True`, registra
  `startup` y, al apagar, marca `ready = False`, vacía la caché JWKS y registra `shutdown`.
- En `prod`/`staging` una configuración incompleta **impide arrancar** (fallo cerrado). En
  desarrollo solo se registra `config_incompleta` como aviso.
- El orden de middleware se conserva: `TrustedHost` → logging → cabeceras de seguridad → límite de
  peticiones → aplicación.

### 1.2 Salud

| Ruta | Semántica | Dependencias externas |
|---|---|---|
| `/health` | Compatibilidad: estado y entorno | Ninguna |
| `/health/live` | Liveness: el proceso responde | Ninguna |
| `/health/ready` | Readiness: configuración esencial presente y app en marcha | **Ninguna** a propósito |

`/health/ready` responde `200 {"status":"ready"}` o `503 {"status":"unavailable"}`. No devuelve
nombres de variables ni valores. **No consulta Supabase**: un readiness que depende de un servicio
externo puede amplificar caídas o generar tráfico innecesario. Si el host exige una comprobación
profunda, se añade como decisión aparte.

### 1.3 Configuración fail-fast

`apps/core/config.py` incorpora:

- `TRUSTED_HOSTS` (lista JSON o separada por comas; por defecto `["*"]`).
- `ENABLE_DOCS` (`None` = derivar de `APP_ENV`).
- `SUPABASE_POSTGREST_TIMEOUT_SECONDS` (15 s por defecto).
- `essential_config_problems()`, `runtime_config_problems()`, `validate_runtime_config()` y
  `docs_enabled()`.

| Condición | `dev` | `prod` / `staging` |
|---|---|---|
| Falta `SUPABASE_URL` o `SUPABASE_ANON_KEY` | Aviso en el arranque | **Error de arranque** |
| `COOKIE_SECURE=false` | Permitido (HTTP local) | **Error de arranque** |
| `TRUSTED_HOSTS` contiene `*` | Permitido | **Error de arranque** |
| Solo `HS256` sin `SUPABASE_JWT_SECRET` | Aviso | **Error de arranque** |
| OpenAPI/Swagger | Publicado | **Desactivado** salvo `ENABLE_DOCS=true` |

Los mensajes de error solo nombran campos, nunca valores. No se registran secretos.

### 1.4 Hosts y documentación

- `TrustedHostMiddleware` rechaza con `400` un `Host` no permitido. El valor por defecto `*` es
  solo para desarrollo; en producción debe fijarse explícitamente.
- `docs_url`, `redoc_url` y `openapi_url` quedan en `None` fuera de producción, salvo override.

### 1.5 Cliente de datos

`get_supabase_for_user` y el cliente global heredado usan `ClientOptions` con
`postgrest_client_timeout`. Los reintentos de supabase-py solo aplican a `GET`/`HEAD`, por lo que
**no pueden duplicar escrituras**. Si faltan URL o clave, el error es explícito antes de crear el
cliente.

## 2. Pruebas ejecutadas realmente

| Prueba | Resultado |
|---|---|
| `pytest` completo | **157 passed, 1 warning** (14/11/2026) |
| Nuevas de robustez operativa | **20** (`tests/test_operational.py`) |
| `compileall` de `apps/`, `main.py` e `integrations/` | Sin errores |
| `git diff --check` | Sin errores de espacio |
| Comprobación manual con `TestClient` | `/health` 200, `/health/live` 200, `/health/ready` 200; `/openapi.json` 404 con `ENABLE_DOCS=false`; `Host` no permitido 400 |

Cobertura nueva: configuración de producción (URL/clave, cookies, hosts, HS256), parseo de listas,
derivación de docs, readiness con y sin configuración, estado de apagado, limpieza de JWKS,
`TrustedHost`, desactivación de OpenAPI, timeout del cliente y errores de configuración.

**No ejecutado:** despliegue, host real, varios workers, prueba de carga, navegador real,
axe/Lighthouse ni E2E contra Supabase tras este cambio. No se declara conformidad ASVS ni WCAG.

## 3. Límites y riesgos

1. **Readiness superficial por diseño:** no detecta una caída de Supabase ni de PostgREST. El host
   puede necesitar una comprobación profunda; sería una decisión nueva.
2. **Multi-worker:** el límite de peticiones sigue siendo por proceso (DEC-22). Este cambio no lo
   resuelve.
3. **`TRUSTED_HOSTS=*` en desarrollo:** si se copia a producción, el arranque falla; es intencional.
4. **Documentación OpenAPI:** `ENABLE_DOCS=true` en producción vuelve a exponer `/docs`; debe ser
   una decisión consciente.
5. **Timeout de PostgREST:** 15 s es un valor por defecto; no se probó contra latencias reales.
6. **Sin cambios de dominio:** no se toca RLS, RPC, migraciones ni reglas de autorización.

## 4. Siguiente paso

1. Revisar el diff y decidir qué se commitea (sin `git add .`).
2. Elegir host/topología y revisar el límite multi-worker (ADR-015 §6).
3. Crear la matriz ASVS `requisito → estado` (DEC-06).
4. Ejecutar navegador real, axe/Lighthouse y el E2E de escrituras tras el hardening.
