# DEC-12 — Material de decisión: capa de aplicación

**Fecha:** 26/10/2026 · **Estado:** material de evaluación con matriz puntuada y ADR **propuesto**.
**No es una aprobación**: la puntuación no selecciona stack. **Decide:** el propietario.

> **Actualización del 12/11/2026.** DEC-12 está cerrada: el propietario ratificó **FastAPI como
> BFF**. La decisión consta en `decisions/adr/ADR-013-fastapi-bff.md`; ADR-012 (opción B) quedó
> rechazada. Este material se conserva como evidencia y no se reescribe.
Documentos derivados: `decisions/dec-12-matriz-puntuada.md` y
`decisions/adr/ADR-012-capa-de-aplicacion.md`.

---

## 1. Punto de partida (hechos verificados)

- F1 existe **solo en base de datos**: 6 migraciones, 5 tablas con RLS `enable`+`force`, 5 RPC
  `SECURITY DEFINER`, 127 comprobaciones SQL en verde (102 de F1 + 25 del rol `service_role`).
  **No hay `package.json` raíz, ni framework, ni interfaz, ni endpoint**: no existe capa de
  aplicación.
- La escritura de dominio pasa por RPC con guardas; la única escritura directa es
  `profiles`, por columna. `platform_admins` no es accesible por API.
- Presupuesto aprobado: **US$0/mes** (DEC-08). No hay remoto Git configurado.
- Supabase: PostgreSQL 17.11, región `us-east-1` fija, sin backups automáticos en el plan gratuito.
- No hay pruebas de aplicación, navegación ni endpoints. Las 127 pruebas son de base de datos.

## 2. Hecho verificado que condiciona todo: Vercel Hobby

Consultado hoy en la documentación oficial de Vercel (*Fair Use Guidelines*, actualizada el
14/09/2026):

> «**Hobby teams** are restricted to non-commercial personal use only. All commercial usage of the
> platform requires either a Pro or Enterprise plan.»

Y define uso comercial como «cualquier Deployment usado con propósito de lucro de **cualquiera**
involucrado en **cualquier parte** de la producción del proyecto, incluido un empleado o consultor
pagado que escriba el código», con ejemplos: cobrar a visitantes, anunciar venta de un producto o
servicio, cobrar por crear/actualizar/alojar el sitio, enlaces de afiliado como propósito principal
y publicidad.

**Consecuencia:** si VOLTERRA se considera uso comercial, Vercel Hobby **no cumple** y el plan Pro
rompe DEC-08. Esto no lo puede resolver el coordinador: es una calificación del propietario sobre el
destino del producto.

**Resuelto el 26/10/2026:** el propietario calificó VOLTERRA como **no comercial**. La cuenta de
Vercel consultada por API es **Hobby, activa** [H]. Por tanto A es viable a US$0 **mientras** se
mantenga esa calificación; si aparece lucro en cualquier parte de la producción, A sale por el
filtro de costo. Es un hecho revisable, no permanente.

## 3. Opciones (sin selección)

### A. Next.js + React + TypeScript en Vercel

**A favor:** un solo lenguaje y tipos generados desde el esquema; lugar natural para validación,
cabeceras, límites y exportaciones auditadas; buena base para F2–F12; mucha documentación para
OpenCode.
**En contra:** la cláusula no comercial es el riesgo principal; más superficie (dependencias,
sesión, CSRF, middleware); tentación de usar `service_role` en el servidor, que anularía RLS y las
guardas; logs de 1 hora en Hobby.
**US$0:** condicionado a la calificación no comercial.

### B. Sitio estático mínimo (sin framework de UI) contra Supabase directo

**A favor:** superficie de secretos mínima (solo clave publicable, que no es secreto); una sola
frontera de autorización (PostgREST + RLS + RPC); no toca las RPC ni la autorización; portabilidad.
**En contra:** no hay dónde auditar lecturas/exportaciones (T-01 incluye exportar) sin una RPC
nueva; sesión en el navegador expuesta a XSS; la UI crece a mano y probablemente haya reescritura
en F2–F12; el host estático también tiene términos.
**US$0:** el más probable, sujeto a los términos del host elegido.

### C. Backend TypeScript separado (Hono/Fastify o Supabase Edge Functions)

**A favor:** frontera explícita para validación, límites y exportaciones auditadas; Edge Functions
evitan otro proveedor.
**En contra:** dos despliegues y dos CI; deriva de contratos; si usa `service_role` en flujos de
usuario, anula RLS; si solo reenvía el JWT, añade complejidad sin reducir riesgo.
**US$0:** Edge Functions dentro del plan gratuito de Supabase; Node depende de Vercel Hobby.

### D. Python / FastAPI

**A favor:** ecosistema de validación, pruebas y futuro análisis de datos.
**En contra:** dos lenguajes y dos toolchains; el riesgo grave es conectar como `postgres`: se
pierde RLS y habría que reimplementar aislamiento, guardas y auditoría; hosting gratuito frágil.
**US$0:** el más frágil de los cuatro.
**Nota:** ninguna funcionalidad del MVP actual requiere Python.

### Lectura cruzada

| Opción | Servidor propio | US$0 | Riesgo dominante |
|---|---|---|---|
| A | Sí | Condicionado | Cláusula de Vercel y `service_role` |
| B | No | Probable | Auditoría de exportaciones y XSS de sesión |
| C | Sí | Condicionado | Duplicación de la autorización |
| D | Sí | Frágil | Bypass de RLS |

**Invariante en las cuatro:** la autoridad real es la base de datos. Todas preservan RLS si el JWT
del usuario llega a PostgREST/RPC; todas la pierden si el camino de usuario usa `service_role` o un
rol privilegiado.

**Matiz probado el 26/10/2026** (`supabase/tests/f1_service_role.test.sql`, 25/25): con
`service_role` las 5 RPC **deniegan** (`28000`), pero las tablas **no** están protegidas: el rol
tiene `BYPASSRLS` y `SELECT`/`INSERT` sobre las 5 (incluida `platform_admins`), lee y escribe sin
identidad, y si la conexión fija `request.jwt.claims` puede suplantar a cualquier usuario. Por
tanto la frase correcta no es «las RPC deniegan» sino **«la clave secreta no debe existir en el
camino de usuario»**. Ninguna de las cuatro opciones cambia este hecho: es una regla de uso, no
una propiedad del framework.

## 4. Hipótesis declaradas

1. ~~Llamar a las RPC con `service_role` hará que `auth.uid()` sea nulo y las guardas denieguen.~~
   **Verificada el 26/10/2026** (`f1_service_role`, P1–P5 = `28000`). Con el matiz de §3: la
   denegación de las RPC no protege las tablas, porque `service_role` tiene `BYPASSRLS`.
2. `supabase start` (entorno local) exige Docker, que no está instalado. No verificado.
3. El volumen inicial (Q-03) cabe en los planes gratuitos. **Cifra respondida el 26/10/2026: 1–3
   clubes y menos de 100 atletas.** Que quepa en las cuotas gratuitas sigue sin verificar: no se
   consultó ninguna cuota en esta sesión.
4. El proveedor de correo integrado de Supabase Auth limita los envíos (el subagente leyó 2/hora).
   **No re-verificado por mí**; afecta a altas y recuperación de contraseña.

## 5. Lo que no se puede decidir todavía

| Bloqueo | Efecto sobre DEC-12 | Estado 26/10/2026 |
|---|---|---|
| **E-6 / DEC-19** (región y transferencia) | Se puede comparar la capa de aplicación, pero no declarar «stack aprobado» | Abierto |
| **DEC-06** (nivel ASVS) | Sin nivel fijado, la puntuación de seguridad es provisional y puede cambiar el veredicto | Abierto |
| **O-03 / DEC-07** (respaldo) | Ninguna opción de aplicación resuelve la falta de restauración probada | Abierto |
| **Calificación comercial de Vercel** | Si es comercial, la opción A no cumple DEC-08 | **Resuelto: no comercial** |
| **Q-03** (volumen) | Sin cifras no se evalúan límites ni costo | **Resuelto: 1–3 clubes, <100 atletas** |
| **A-03** (interpretación) | ¿PostgREST + RLS cuenta como «servidor y capa de datos»? | **Resuelto: sí basta** |

## 6. Método confirmado (propietario, 26/10/2026) y resultado

Las dos correcciones al documento `decisions/stack-evaluation.md` se mantienen:

1. **La matriz lista 10 criterios, no 11.** El «11» contaba la fila de total. Se puntúa sobre 10
   criterios con denominador 100.
2. **El costo es filtro eliminatorio, además de peso.** Con US$0 aprobado, una opción que cuesta
   US$20/mes no es «un poco peor»: queda fuera.

**Pesos confirmados** (suman 100): seguridad y aislamiento multi-club 25 · modelo de datos,
historial y auditoría 15 · costo 10 · facilidad con OpenCode 12 · despliegue y operación 10 ·
mantenibilidad 10 · autenticación y archivos 7 · portabilidad 6 · integraciones 3 · analítica
futura 2.

**Filtros confirmados:** seguridad < 4 elimina; costo distinto de 0 elimina; cualquier opción que
requiera `service_role` en el camino de usuario elimina.

**Resultado:** la puntuación, la justificación por criterio, el cálculo, el análisis de sensibilidad
y las condiciones que invalidan el resultado están en `decisions/dec-12-matriz-puntuada.md`. El ADR
propuesto (estado **Propuesto — no aprobado**) está en
`decisions/adr/ADR-012-capa-de-aplicacion.md`. Resumen: B 4,06 · A 3,96 · C 3,65 · D 2,58
(eliminada por el filtro de seguridad), con **empate técnico** entre A y B.

La puntuación **no decide**: el propietario aprueba, rechaza o pide recálculo. Tampoco queda
elegido el host estático concreto, que es una decisión aparte.

## 7. Respuestas del propietario y pendientes

Respondidas el 26/10/2026:

| Pregunta | Respuesta |
|---|---|
| ¿Uso comercial? | **No comercial.** Vercel Hobby queda viable mientras se mantenga esa calificación |
| ¿Pesos y filtros de §6? | **Confirmados tal como están** |
| ¿PostgREST + RLS basta como «servidor y capa de datos» (A-03)? | **Sí basta.** La opción B pasa a ser evaluable |
| ¿Volumen inicial (Q-03)? | **1–3 clubes, menos de 100 atletas** |
| ¿Se autoriza puntuar? | **Sí**, sin que la puntuación seleccione el stack |

Siguen pendientes y **bloquean el cierre de DEC-12**, no la comparación:

1. **Decisión sobre el resultado:** aprobar B, aprobar A (alternativa de reserva), rechazar ambas o
   pedir recálculo. Sin esto, DEC-12 sigue sin decidir.
2. **Host estático concreto** si se elige B: no está elegido ni verificado en cuanto a términos y
   cuotas.
3. **DEC-06 (nivel ASVS):** si fija L2/L3 con sesión y límites en servidor, la nota de seguridad de
   B baja y el orden puede invertirse.
4. **E-6 / DEC-19, E-4 / DEC-05 y O-03 / DEC-07:** siguen abiertos. Ninguna opción de capa de
   aplicación los resuelve; impiden declarar «stack aprobado» y, sobre todo, operar con datos reales.
5. **Revocación de privilegios de `service_role`** sobre las 5 tablas: no decidida. La propuesta de
   ADR la trata como riesgo estructural, no como cambio aplicado.

## 8. Qué no hace este documento

- No selecciona stack, no aprueba proveedor, no crea archivos de configuración, no instala nada,
  no despliega y no genera costos.
- No cierra DEC-12 ni ninguno de los bloqueos citados.
- **Pruebas ejecutadas:** ninguna de software para este material. Verificación documental: política
  de uso justo de Vercel (26/10/2026), plan de la cuenta consultado por API (**Hobby, activo**),
  revisión de documentos del repositorio y las 127 comprobaciones SQL ya registradas en
  `supabase/README.md`. No se consultó ninguna cuota de plan gratuito en esta sesión.
