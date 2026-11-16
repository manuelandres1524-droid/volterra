# ADR-012 — Capa de aplicación de VOLTERRA

**Estado:** **Rechazada** el 12/11/2026 (opción B no adoptada). **Sustituida por ADR-013.**
**Fecha:** 26/10/2026 · **Versión:** borrador 1 · **Sustituye a:** nada.
**Relacionado:** DEC-06, DEC-07/O-03, DEC-08, DEC-12, DEC-18, DEC-19/E-6.
**Insumo:** borrador del agente `architect`; matriz en `decisions/dec-12-matriz-puntuada.md`.

> **Actualización del 12/11/2026.** El propietario cerró DEC-12 ratificando **FastAPI como BFF**
> (`decisions/adr/ADR-013-fastapi-bff.md`). La opción B propuesta aquí **no fue adoptada**. Este
> documento se conserva como evidencia de la evaluación; no es una decisión vigente.
>
> Este documento no autoriza implementación, despliegue, contratación ni gasto.

---

## 1. Contexto

F1 está implementado **solo en base de datos**: 6 migraciones, 5 tablas con RLS `enable`+`force`,
5 RPC `SECURITY DEFINER` y 127 comprobaciones SQL en verde. No existe capa de aplicación, no hay
`package.json` raíz y no hay remoto Git. La autoridad real es la base: toda escritura de dominio
pasa por RPC con guardas y auditoría; la única escritura directa es `profiles`, por columna;
`platform_admins` no es accesible por API con JWT de usuario. **[H]**

El hecho que más condiciona la elección se probó el 26/10/2026: con la clave `service_role` las 5 RPC
**deniegan** (`28000`), pero las tablas **no** están protegidas —`BYPASSRLS` y `SELECT`/`INSERT`
sobre las 5, incluida `platform_admins`— y fijando `request.jwt.claims` se suplanta a cualquier
usuario. Conclusión: **la clave secreta no puede existir en ningún camino de usuario.** **[H]**

Restricciones confirmadas por el propietario el 26/10/2026: VOLTERRA es **no comercial**, con Vercel
Hobby activo (cuya política admite solo uso personal no comercial); presupuesto **US$0/mes**
(DEC-08); **A-03: PostgREST + RLS basta** como «servidor y capa de datos»; pesos y filtros
confirmados; volumen inicial **1–3 clubes y menos de 100 atletas** (Q-03). **[H]**

Siguen abiertos y **no se afirman resueltos**: nivel ASVS (DEC-06), región y transferencia
internacional (E-6/DEC-19), retención (E-4/DEC-05) y respaldo probado (O-03/DEC-07). Ninguna opción
de capa de aplicación los resuelve. **[H]**

## 2. Decisión propuesta

**Adoptar la opción B: un sitio estático mínimo, sin framework de UI y sin servidor propio, que
consume Supabase con la clave publicable y llama a las RPC existentes; sin `service_role` en ningún
punto del repositorio ni del navegador.**

Sujeto a aprobación:

1. **Un solo artefacto**: HTML, CSS y TypeScript compilado servidos por un host estático gratuito.
   No hay servidor de aplicación.
2. **Una sola frontera de autorización**: PostgREST + RLS + las 5 RPC ya probadas. La interfaz no
   implementa autorización; la refleja.
3. **`service_role` prohibida** en cliente, *bundles*, scripts y cualquier flujo de usuario, con
   verificación automática del artefacto construido. **[R]**
4. **Exportaciones (F23/T-01) con RPC nueva** que escriba en `audit_events` antes de devolver datos,
   con `revoke all … from public, anon` en la misma migración y pruebas negativas. **[R]**
5. **Sin límite de peticiones en servidor** en la primera entrega: residual aceptado, mitigado con
   caducidad corta de sesión y CSP estricta. **[R]**
6. **Sin tareas en segundo plano, webhooks ni procesamiento de archivos** en esta capa. Cuando
   F17/F18 los exijan se abre una decisión nueva; no se improvisa un servidor.

**Fundamento (recomendación, no hecho).** B obtiene 4,06 frente a 3,96 de A, pero la ventaja es de
0,10 puntos y cabe en el ruido de una sola nota. La propuesta se sostiene en dos razones ajenas al
total: es la única opción en la que la invariante de seguridad probada es **estructural** —no hay
capa que pueda guardar la clave— y es la única cuyo US$0 **no depende** de una calificación
comercial ajena. El propietario puede preferir A sin que la matriz lo contradiga: hay empate técnico.

## 3. Alternativas no seleccionadas

**A — Next.js + React + TS en Vercel (3,96).** No se descarta: es la **alternativa de reserva** y la
primera en el disparador D-2. Aporta mejor encaje para F2–F12, tipos generados desde el esquema,
sesión en cookie `httpOnly`, cabeceras y un punto único de control de exportaciones. No se propone
porque (i) añade una capa que *puede* alojar `service_role` y convierte una invariante probada en
disciplina; (ii) su US$0 depende de la calificación no comercial; (iii) los logs de Hobby duran una
hora.

**C — Backend TypeScript separado (Hono/Fastify o Edge Functions) (3,65).** Duplica la autorización
sin reducir riesgo: si reenvía el JWT añade complejidad y deriva de contratos; si usa `service_role`
queda eliminada por F3. Su ventaja (integración y webhooks) no la necesita el MVP. Es la opción
natural **cuando** F17/F18 exijan procesamiento en servidor.

**D — Python/FastAPI (2,58, eliminada por F1).** La conexión directa como rol propietario anula RLS,
guardas y atribución de auditoría, y obligaría a repetir en otra capa lo ya probado con 127
comprobaciones. Su única ventaja (analítica) pesa 2 sobre 100.

## 4. Consecuencias

**Positivas**
- La invariante de seguridad pasa de regla de uso a **propiedad estructural**: no existe dónde poner
  la clave secreta.
- Superficie de secretos mínima: solo la clave publicable, que no es secreta.
- US$0 sin depender de la cláusula no comercial de un proveedor; portabilidad máxima.
- Camino más corto a una interfaz sobre datos ya probados; ninguna migración nueva para leer/escribir.
- No se toca el esquema, las RPC ni las 127 pruebas.

**Negativas**
- No hay dónde auditar lecturas ni exportaciones salvo la base: cada exportación auditada exige RPC
  nueva y prueba.
- UI escrita a mano: probabilidad alta de reescritura en F2–F12 (mantenibilidad 3, la nota más baja).
- Sesión en el navegador expuesta a XSS; sin límite de peticiones en servidor.
- Sin logs de servidor, webhooks, correo saliente ni procesamiento de archivos: F17/F18 fuerzan una
  decisión posterior y probablemente un segundo artefacto.
- Migrar después a A o C no reutiliza entero el código de interfaz.
- **No cierra ningún bloqueo**: DEC-06, E-6, E-4 y O-03 siguen abiertos; el primer dato real los activa.

## 5. Condiciones y disparadores de revisión

**Condiciones de validez** (si alguna deja de cumplirse, el ADR queda suspendido):
1. VOLTERRA sigue siendo no comercial y el host elegido admite el uso previsto.
2. A-03 se mantiene: PostgREST + RLS se acepta como «servidor y capa de datos».
3. Q-03 se mantiene en 1–3 clubes y menos de 100 atletas.
4. El volumen cabe en las cuotas gratuitas de Supabase, **no verificadas en esta sesión**.
5. Nadie introduce `service_role` en el camino de usuario.
6. El MVP no requiere tareas en segundo plano, webhooks ni procesamiento de archivos.
7. DEC-06 no fija un ASVS que exija sesión y límites en servidor.

**Disparadores** (revisión obligatoria, con recálculo de la matriz):
- **D-1.** VOLTERRA pasa a comercial → recalcular con F2.
- **D-2.** Se necesita exportación auditada con control fuera de la base, o un punto único de
  validación y límites → reconsiderar A o C.
- **D-3.** Aparecen F17 (archivos con procesamiento) o F18 (correo/invitaciones) → decisión de segunda
  capa.
- **D-4.** DEC-06 fija ASVS L2/L3 → re-puntuar la seguridad de B; podría quedar eliminada.
- **D-5.** El volumen supera las cuotas gratuitas o Q-03 cambia de orden de magnitud.
- **D-6.** E-6/DEC-19 impone residencia o condiciones de transferencia.
- **D-7.** Dos sprints muestran que el coste manual de la interfaz supera el ahorro de superficie.
- **D-8.** Cualquier intento de resolver un flujo con `service_role`: **detención**, no revisión.
- **D-9.** Fecha de revisión propuesta: **26/01/2027**, o antes si se cumple un disparador.

**Criterios de aceptación propuestos para la primera entrega** (no ejecutados, no autorizados):
- El artefacto construido no contiene la cadena de la clave secreta; solo la publicable.
- Las 127 comprobaciones SQL siguen en verde sin modificar migraciones aplicadas.
- Al menos una prueba negativa nueva: `anon` no lee `platform_admins` ni ejecuta funciones no
  expuestas.
- Toda exportación escribe su evento en `audit_events` antes de devolver datos, verificado en SQL.
- Sin `package.json` con dependencias de servidor; el despliegue es copia de estáticos.

## 6. Evidencia

**Hechos comprobados**
- `supabase/README.md` §2–§3 y §5 — 6 migraciones, 5 tablas, RLS `enable`+`force`, 127/127
  (65 + 37 + 25), 0 residuos; `service_role` con `BYPASSRLS`, acceso a las 5 tablas y suplantación
  con `request.jwt.claims`.
- `docs/implementation/f1/00-autorizacion-y-alcance.md` §8 — mismos resultados; revocar privilegios
  de `service_role` no se hizo y no está decidido.
- `docs/operations/o-03-respaldo-restauracion.md` — tubería validada en local; **ningún** volcado ni
  restauración contra Supabase.
- `decisions/dec-12-material-decision.md` — estado de F1, política de Vercel y caracterización de las
  cuatro opciones.
- `decisions/dec-12-matriz-puntuada.md` — puntuación, filtros, sensibilidad y condiciones.
- Hechos del propietario del 26/10/2026: no comercial; Hobby activo; A-03; pesos y filtros; Q-03.

**Hipótesis (no verificadas)**
- Los planes gratuitos de host estático admiten el uso previsto y no imponen cláusulas equivalentes.
- Los planes gratuitos de hosting Python para D son inestables.
- `pg_cron`/`pg_net` cubrirían parte de las necesidades futuras de B sin servidor.
- El correo integrado de Supabase Auth limita los envíos (~2/hora); no re-verificado.
- Las cuotas gratuitas de Supabase bastan para 1–3 clubes y menos de 100 atletas.

**Recomendaciones (del propietario, no tomadas)**
- Aprobar B con estas condiciones, sabiendo que la ventaja es de desempate.
- Fijar DEC-06 antes de la primera entrega con datos reales.
- Decidir si se revocan los privilegios de `service_role` sobre las 5 tablas.
- Cerrar O-03 antes del primer dato real.
- Crear el remoto Git antes de cualquier despliegue.

**Pruebas ejecutadas para este documento:** ninguna de software. Verificación documental; no se
consultó ninguna cuota de proveedor en esta sesión.
