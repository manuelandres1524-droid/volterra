# F1 — RPC de ámbito de plataforma

**Fecha:** 02/11/2026 · **Actualizado:** 12/11/2026
**Estado:** implementado y **aplicado** en el proyecto Supabase `tioeoswnhwrlbovkxocd`; suite SQL
ejecutada en remoto (7/7).
**Autorizante:** propietario del proyecto · **Ejecutor:** agente de desarrollo

---

## 1. Problema

`get_auth_context()` consultaba `public.platform_admins` directamente por PostgREST:

```python
client.table("platform_admins").select("user_id")...
```

Pero el diseño de la base niega esa lectura a `authenticated`:

- la migración `f1_rls_isolation` no concede `SELECT` sobre `platform_admins`;
- la tabla tiene RLS activa y **cero políticas**;
- la suite `f1_rls_isolation` espera `42501` para `pa_lee_platform_admins`.

El backend capturaba el error y devolvía **503**. Con un JWT válido, cualquier petición
fallaba antes de llegar al endpoint. Los tests existentes no lo detectaban porque solo
probaban peticiones sin token.

## 2. Cambio aplicado

| Archivo | Cambio |
|---|---|
| `supabase/migrations/20261102120000_f1_is_platform_admin.sql` | Nueva RPC `public.fn_is_platform_admin()`: `SECURITY DEFINER`, `search_path` vacío, devuelve solo un booleano. |
| `volterra/apps/auth/deps.py` | `get_auth_context()` usa `client.rpc("fn_is_platform_admin")`; normaliza la respuesta escalar con `_as_bool()`. |
| `volterra/tests/test_auth_context.py` | 13 comprobaciones con token simulado: RPC usada, tabla `platform_admins` no consultada, 503 si falla la RPC, 401 sin token o con token inválido. |
| `supabase/tests/f1_platform_admin_rpc.test.sql` | 7 comprobaciones SQL de la RPC. **Ejecutada** en local y en remoto (12/11/2026). |

No se modificaron los privilegios ni las políticas de `platform_admins`: la tabla sigue
inaccesible por PostgREST. La RPC solo revela el ámbito del propio llamador.

## 3. Pruebas ejecutadas

```
pytest: 21 passed, 1 warning (Python 3.14.3)
```

Incluye las 8 pruebas existentes y las 13 nuevas de `test_auth_context.py`.

**Validación SQL local (02/11/2026).** Se levantó un contenedor PostgreSQL 17.11
(desechable) con un `auth` simulado (`auth.users` mínima y `auth.uid()`), los roles
`anon`, `authenticated`, `service_role` y `supabase_admin`, y se aplicaron las **siete**
migraciones en orden. Resultado:

| Suite | Comprobaciones | Resultado local |
|---|---:|---:|
| `f1_rls_isolation.test.sql` | 65 | 65/65 |
| `f1_hardening.test.sql` | 37 | 37/37 |
| `f1_service_role.test.sql` | 25 | 25/25 |
| `f1_platform_admin_rpc.test.sql` | 7 | 7/7 |
| **Total** | **134** | **134/134** |

La simulación reproduce roles, ACL y `auth` mínimos; **no sustituye** una ejecución contra
el proyecto Supabase real. `f1_service_role.test.sql` se ajustó para contar las cinco RPC
originales por nombre, de modo que la sexta RPC no altere su expectativa.

**Revalidación (12/11/2026).** Repetida tras el endurecimiento del BFF (sin cambios en SQL)
sobre PostgreSQL 16.15 desechable, con las siete migraciones y los mismos roles simulados:
**134/134** (65 + 37 + 25 + 7), comparando el JSON de resultados contra los valores
esperados. La migración pendiente se aplicó sin errores en local.

La suite SQL **se ejecutó contra el proyecto Supabase remoto el 12/11/2026**, pero no en el
proyecto previsto inicialmente: el propietario indicó `tioeoswnhwrlbovkxocd`, el preflight
mostró que estaba **vacío**, y con su aprobación explícita se aplicaron las **siete**
migraciones en una transacción. Resultado remoto:

| Suite | Comprobaciones | Resultado remoto |
|---|---:|---:|
| `f1_rls_isolation.test.sql` | 65 | 65/65 |
| `f1_hardening.test.sql` | 37 | 37/37 |
| `f1_service_role.test.sql` | 25 | 25/25 |
| `f1_platform_admin_rpc.test.sql` | 7 | 7/7 |
| **Total** | **134** | **134/134** |

Las cuatro terminaron con `exit 0`; sus JSON se compararon contra los valores esperados
(0 faltantes, 0 sobrantes, 0 distintos). Terminan en `ROLLBACK`: no dejaron fixtures.
Procedimiento y preflight: `03-migracion-remota.md`.

## 4. Pendiente

1. ~~**Aplicar la migración** al proyecto Supabase de desarrollo.~~ Hecho el 12/11/2026
   (secuencia completa 1→7; ver arriba).
2. ~~Ejecutar `f1_platform_admin_rpc.test.sql` y registrar el resultado real.~~ Hecho: 7/7.
3. Probar con un token de usuario real el flujo `/api/v1/me/`. **Pendiente**: no hay usuarios
   en `auth.users` ni `volterra/.env` con la `anon key`.
4. Decidir cómo registrar el historial en `supabase_migrations.schema_migrations` (el SQL
   Editor y `psql` no lo hacen). **Pendiente**: ver `03-migracion-remota.md` §5.
5. Crear los usuarios ficticios y ejecutar `supabase/seed/f1_demo.sql`. **Pendiente**.

**Vía manual (ya no necesaria):** se conserva como referencia. En el panel de Supabase, *SQL
Editor*, pegar el contenido de `supabase/migrations/20261102120000_f1_is_platform_admin.sql` y
ejecutarlo. Después pegar `supabase/tests/f1_platform_admin_rpc.test.sql`, ejecutarlo y
comprobar que el JSON final tiene los siete valores esperados. El test termina en `ROLLBACK`:
no deja fixtures.

## 5. Riesgos

| Riesgo | Estado |
|---|---|
| ~~Mientras la migración no se aplique, el backend sigue devolviendo 503 con token válido.~~ | **Cerrado** el 12/11/2026: la RPC está aplicada en el proyecto remoto |
| La RPC es `SECURITY DEFINER`; debe mantenerse con `search_path = ''` y sin parámetros controlables por el cliente. | Mitigado en el diseño |
| Un cambio futuro en `app.is_platform_admin()` afecta a la RPC. | Aceptado; es la misma fuente de verdad que usan las políticas RLS |
| La suite SQL no se había ejecutado en remoto. | **Cerrado**: 7/7 el 12/11/2026 |
