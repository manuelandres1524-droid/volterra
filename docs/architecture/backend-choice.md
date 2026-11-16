# Elección técnica de backend — VOLTERRA MVP

| | |
|---|---|
| **Fecha** | 31/10/2026 · **Ratificado:** 12/11/2026 |
| **Estado** | **Aprobado** por el propietario al cerrar DEC-12. Documento de decisión: `decisions/adr/ADR-013-fastapi-bff.md`. |
| **Motivo** | DEC-12 se cerró ratificando FastAPI como BFF. Se mantiene el esquema, las RPC y las RLS existentes; la decisión es reversible sin tocar migraciones. |

## Criterios
- Minimizar desviación del esquema validado (6 migraciones, 127/127 pruebas)
- Mantener autorización en servidor y respetar RLS/Postgres
- Modular, testeable, USD 0/mes
- Fácil de aislar por club
- Evitar duplicar lógica ya existente en `app.*` / RPC
- Reversible sin tocar migraciones

## Comparativa
| Aspecto | **FastAPI (BFF aprobado)** | **Django + DRF** |
|---|---|---|
| Acoplamiento al modelo actual | Alto encaje. Llama RPC, usa claims, respeta RLS. | Funciona, pero tiende a imponer su propio sistema de auth/permisos. |
| Velocidad para integrar con Supabase/Postgres | Muy ágil | Ágil, algo más pesado para este patrón |
| Modularidad por dominio | Nativo con routers/depends | Apps Django, también válido |
| Testing | Sencillo (`TestClient`, `httpx`) | Sólido pero más configuración |
| Riesgo de duplicar reglas RLS/RPC | Bajo si se forza a usar RPC/guards | Mayor si se abstrae mal |
| Curva / ajustes | Mínimos para API REST acotada | Más framework |

## Decisión
**Adoptar FastAPI (Python 3.11+) como BFF (Backend-for-Frontend) del MVP.**

## Invariantes
- Cada petición usa el **JWT del usuario** y un cliente PostgREST por petición con la clave
  publicable (`volterra/apps/integrations/supabase/per_request.py`). No hay identidad de servidor
  con privilegios sobre los datos.
- **`service_role` prohibida en todo camino de usuario.** No se usa en peticiones, tareas, scripts
  ni artefactos. La clave secreta no puede ser la vía para resolver un flujo.
- **Sin conexión directa como rol propietario** ni SQL/DDL desde el backend. Las escrituras de
  dominio pasan por las RPC existentes; las lecturas por PostgREST con RLS.
- Las reglas de autorización críticas siguen en **Postgres** (RLS `enable`+`force`, `app.*` y RPC).
  FastAPI valida forma, mapea claims y errores, y aplica guardas como defensa en profundidad;
  **nunca** es el único control.
- El BFF **no duplica reglas de dominio** ni reimplementa permisos, auditoría o transiciones.
- US$0/mes (DEC-08). El host del BFF no está elegido y **no se despliega** sin autorización.

## Notas
- Si aparecen impedimentos reales que justifiquen cambio, se migrará con contratos API estables y
  sin tocar `supabase/migrations/`.
- La matriz de DEC-12 puntuó la variante D como conexión directa (2,58, eliminada), **no** esta
  variante BFF. La aprobación es un acto del propietario y se registra como desviación declarada
  en `decisions/decision-register.md` y `decisions/adr/ADR-013-fastapi-bff.md`.
- Esta decisión **no cierra** DEC-06, DEC-07/O-03, DEC-19/E-6 ni DEC-05.
