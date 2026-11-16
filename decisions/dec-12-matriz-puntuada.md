# DEC-12 · Matriz puntuada de la capa de aplicación

**Fecha:** 26/10/2026 · **Estado:** evaluación. **No es una aprobación ni un ADR.**
**Insumo:** borrador del agente `architect`, revisado por el coordinador.
**Decide:** el propietario. La puntuación no selecciona stack por sí sola.

> **Actualización del 12/11/2026.** DEC-12 se cerró ratificando **FastAPI como BFF** (ADR-013).
> Esa variante **no es la D puntuada aquí**: D se puntuó como conexión directa con rol propietario
> (2,58, eliminada). La matriz se conserva como insumo; **no avala** la decisión y no se recalcula
> en este documento.

Escala 1–5, ordinal, sin calibración entre evaluadores. Pesos **confirmados por el propietario el
26/10/2026** y suman 100. Etiquetas: **[H]** hecho comprobado · **[P]** hipótesis ·
**[R]** recomendación.

---

## 1. Puntuaciones

| Criterio | Peso | A Next.js/Vercel | B Estático+PostgREST | C Backend TS aparte | D Python/FastAPI |
|---|---:|---:|---:|---:|---:|
| Seguridad y aislamiento multi-club | 25 | 4 | 5 | 4 | 2 |
| Modelo de datos, historial y auditoría | 15 | 4 | 4 | 4 | 3 |
| Costo | 10 | 3 | 4 | 4 | 2 |
| Facilidad con OpenCode | 12 | 5 | 4 | 3 | 3 |
| Despliegue y operación | 10 | 3 | 4 | 3 | 2 |
| Mantenibilidad | 10 | 4 | 3 | 3 | 2 |
| Autenticación y archivos | 7 | 5 | 3 | 4 | 3 |
| Portabilidad | 6 | 3 | 5 | 3 | 4 |
| Integraciones | 3 | 5 | 2 | 5 | 4 |
| Analítica futura | 2 | 4 | 3 | 4 | 5 |

## 2. Justificación

**Seguridad y aislamiento (25).** Las cuatro conservan RLS si el JWT del usuario llega a
PostgREST/RPC [H: 127/127]. **A = 4**: gana sesión en cookie `httpOnly`, cabeceras y límite de
peticiones en servidor, pero añade una capa que *puede* alojar `service_role`. **B = 5**: no existe
capa donde guardar la clave secreta; la invariante probada pasa de regla de uso a propiedad
estructural. Residual: token en el navegador (XSS) y sin *rate limiting* de servidor. **Discutible**
con DEC-06 en ASVS L2/L3. **C = 4**: frontera propia, pero duplica la autorización; si solo reenvía
el JWT, añade complejidad sin reducir riesgo. **D = 2**: la forma habitual conecta como rol
propietario y anula RLS, guardas y atribución de auditoría; la variante con reenvío de JWT sería C
en otro lenguaje y no es la forma declarada.

**Modelo de datos, historial y auditoría (15).** El modelo, `ended_at` y los triggers son los
mismos en las cuatro [H]. El diferencial es dónde se audita una exportación. **A = B = C = 4.**
Corrección a una hipótesis del material: la objeción «B no tiene dónde auditar exportaciones sin
una RPC nueva» **aplica igual a A, C y D**, porque en las tres el navegador puede llamar a
PostgREST con el mismo JWT [H: requisitos T-01]. Un log de aplicación es eludible; la garantía
verificable es una RPC que escriba en `audit_events`, y hace falta en las cuatro. A y C podrían
cortar el acceso directo del navegador, pero eso es un cambio de arquitectura, no de framework [R].
**D = 3**: sin claims no hay actor atribuible y `request.jwt.claims` es falsificable desde esa
conexión.

**Costo (10).** El filtro es binario y va en §3; esta nota mide **fragilidad del cero**. A = 3
(US$0 condicionado a la calificación no comercial de Vercel Hobby [H]); B = 4 (host estático
gratuito, términos por verificar [P]); C = 4 (Edge Functions dentro de Supabase, sin la cláusula de
Vercel [P]); D = 2 (no hay plan gratuito estable para un proceso Python permanente [P, no
verificado]).

**Facilidad con OpenCode (12).** A = 5 (patrón con más documentación, tipos generables desde el
esquema [H]); B = 4 (trivial de generar, sin convenciones que frenen la deriva; con Vite+TS sube a
5); C = 3 (dos despliegues, dos CI, contratos que se desincronizan); D = 3 (segundo lenguaje y
toolchain sobre un proyecto cuyo único artefacto es SQL [H]).

**Despliegue y operación (10).** A = 3 (plataforma única y *preview*, pero logs de 1 hora en
Hobby [H] y sin remoto Git [H]); B = 4 (publicar archivos, sin build obligatorio; sin logs de
servidor); C = 3 (dos artefactos en orden; el fallo caro es el desfase de contratos); D = 2 (runtime
y pipeline adicionales sin resolver el primero).

**Mantenibilidad (10).** A = 4 (un lenguaje y tipos, contra dependencias y cadencia de framework);
B = 3 (pocas dependencias, UI manual con probabilidad alta de reescritura en F2–F12 [H]); C = 3
(más código propio y dos fuentes de verdad para validación); D = 2 (dos lenguajes y reglas de
autorización en dos sitios).

**Autenticación y archivos (7).** Prospectivo: Storage no está configurado y DEC-10 sigue abierto
[H]. A = 5 (`@supabase/ssr`, cookies `httpOnly`, subida/descarga en servidor); B = 3 (subida directa
con políticas; token expuesto a XSS); C = 4; D = 3.

**Portabilidad (6).** La base es portable en las cuatro (PostgreSQL + `pg_dump`, O-03) [H]. A = 3
(corre fuera de Vercel, con acoplamiento real); B = 5 (archivos estáticos); C = 3 (Edge Functions son
Deno; Hono/Fastify serían portables); D = 4.

**Integraciones (3).** A = 5 (rutas de API y webhooks en el mismo despliegue); B = 2 (sin servidor no
hay receptor de webhooks ni correo saliente; `pg_cron`/`pg_net` son otra decisión [P]); C = 5 (su
razón de ser); D = 4.

**Analítica futura (2).** A = 4; C = 4; B = 3 (todo en SQL, informes pesados vía RPC o job externo);
D = 5 (único criterio donde gana, y pesa 2).

## 3. Filtros

| Filtro | A | B | C | D | Resultado |
|---|---|---|---|---|---|
| **F1** Seguridad < 4 elimina | 4 pasa | 5 pasa | 4 pasa | **2 elimina** | **Elimina D** |
| **F2** Costo distinto de 0 elimina | 0 hoy, condicionado | 0 | 0 (Edge) | 0 no acreditado | **No elimina a nadie hoy** |
| **F3** Requiere `service_role` en camino de usuario | no requiere | no puede tenerlo | no requiere | no requiere | **No elimina a nadie** |

**F2 no elimina hoy, y hay que decirlo:** las cuatro pueden operar a US$0 con los hechos
confirmados (VOLTERRA no comercial, Hobby activo) [H]. El filtro **sí eliminaría** A y la variante
Node de C si la calificación cambia a comercial. Es un filtro **diferido** con disparador conocido.

**F3 tampoco elimina hoy:** ninguna lo *exige*; tres lo *permiten* (A, C, D). Es el riesgo más caro
si se materializa [H: 25/25: lee y escribe las 5 tablas, incluida `platform_admins`, y suplanta con
`request.jwt.claims`]. Por eso la propuesta incluye un control verificable, no una recomendación de
estilo.

## 4. Cálculo y orden

```
A: 4×25=100 +4×15=60 +3×10=30 +5×12=60 +3×10=30 +4×10=40 +5×7=35 +3×6=18 +5×3=15 +4×2=8  = 396 → 3,96
B: 5×25=125 +4×15=60 +4×10=40 +4×12=48 +4×10=40 +3×10=30 +3×7=21 +5×6=30 +2×3=6  +3×2=6  = 406 → 4,06
C: 4×25=100 +4×15=60 +4×10=40 +3×12=36 +3×10=30 +3×10=30 +4×7=28 +3×6=18 +5×3=15 +4×2=8  = 365 → 3,65
D: 2×25=50  +3×15=45 +2×10=20 +3×12=36 +2×10=20 +2×10=20 +3×7=21 +4×6=24 +4×3=12 +5×2=10 = 258 → 2,58
```

| Puesto | Opción | Total | Estado |
|---:|---|---:|---|
| 1 | **B** | **4,06** | evaluable |
| 2 | A | 3,96 | evaluable |
| 3 | C | 3,65 | evaluable |
| — | D | 2,58 | **eliminada** por F1 |

**B supera a A por 0,10 puntos**, menos que una sola nota en cualquier criterio de peso ≥ 10. **No es
un veredicto técnico: es un empate técnico.**

### Sensibilidad (una nota, un criterio)

| Cambio | Efecto |
|---|---|
| Seguridad de A = 5 (se valora `httpOnly` + cabeceras + límite) | A = 4,21 → **gana A** |
| Seguridad de B = 4 (DEC-06 exige controles en servidor) | B = 3,81 → **gana A** |
| OpenCode de B = 5 (B con Vite + TS) | B = 4,18 → gana B con holgura |
| Datos/auditoría de A = 5 | A = 4,11 → **gana A** |
| Mantenibilidad de B = 2 (reescritura de UI casi segura) | B = 3,96 → **empate** |
| D con seguridad 4 | D ≤ 3,08 → sigue última |

Intervalo plausible: B 3,96–4,18; A 3,84–4,21. La recomendación del ADR no se sostiene en 0,10
puntos, sino en dos propiedades ajenas a la escala: (a) en B la invariante de seguridad es
**estructural**, no disciplinaria; (b) el US$0 de B **no depende** de la calificación no comercial
de un proveedor.

## 5. Límites de esta puntuación

1. No hay código de aplicación en ninguna opción: se puntúan costes y riesgos futuros, no medidos [H].
2. Las cuotas de los planes gratuitos **no se verificaron en esta sesión** [P].
3. DEC-06 sigue abierto: la nota de seguridad es provisional y puede mover el veredicto [H].
4. Una sola nota discutible de peso ≥ 10 invierte el orden A/B.
5. **Pruebas ejecutadas para este documento:** ninguna de software. Es análisis documental.

## 6. Condiciones que invalidarían el resultado

| # | Condición | Efecto |
|---|---|---|
| C-1 | VOLTERRA pasa a uso comercial | **A y C-Node salen por F2**; DEC-08 exige decisión nueva |
| C-2 | Se necesita `service_role` en un flujo de usuario | **F3 elimina la opción** |
| C-3 | Tareas en segundo plano reales (correo, recordatorios, webhooks) | B pierde 2 en integraciones y 1 en despliegue |
| C-4 | Archivos con procesamiento en servidor | B pierde en autenticación y archivos |
| C-5 | Auditoría de exportaciones con control fuera de la base | A y C suben; B exige RPC nueva |
| C-6 | DEC-06 fija ASVS L2+ con sesión/CSRF/límites en servidor | B cae a 4 o menos; F1 podría eliminarla |
| C-7 | El volumen supera las cuotas gratuitas | Ninguna capa de aplicación lo resuelve [P] |
| C-8 | E-6/DEC-19 fija residencia o condiciones de transferencia | Migración de proyecto; no cambia el orden |
| C-9 | No hay remoto Git antes de construir | Sin CI ningún despliegue es reproducible [H] |
| C-10 | La UI de F2–F12 cuesta más de dos sprints manuales | B baja a 2 → empate |
| C-11 | Aparecen datos reales sin respaldo probado | Invalida la operación, no la elección |
| C-12 | Alguien introduce `service_role` "solo para una ruta" | Convierte la opción en no conforme a F3 |
