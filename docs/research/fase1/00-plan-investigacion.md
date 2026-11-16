# FASE 1 de investigación de VOLTERRA — Plan y estado

> **SUPERADO — este no es el corpus vigente.** Investigación original de FASE 1 para **España/UE** (20/10/2026). El corpus vigente es **[`../fase1-colombia/`](../fase1-colombia/)** (Colombia, 21/10/2026), que sustituye la jurisdicción, las fuentes, los plazos y las decisiones. Este documento se conserva íntegro por trazabilidad histórica: **no usar sus requisitos, plazos ni base jurídica como vigentes**. Índice y alcance: [`README.md`](README.md).

**Estado:** propuesta para revisión humana — **no aprobada**.
**Fecha:** 20/10/2026.
**Modo de ejecución:** solo lectura; ningún archivo existente fue modificado; ninguna tecnología seleccionada ni aprobada.

## Objetivos de la FASE 1 (encargo original)

1. Identificar los problemas principales que VOLTERRA debe resolver para clubes y entrenadores de voleibol de playa.
2. Delimitar las funcionalidades candidatas del MVP y separarlas de las futuras.
3. Identificar requisitos de arquitectura, seguridad, privacidad, permisos y trazabilidad.
4. Identificar preguntas que debemos resolver antes de elegir tecnologías.
5. Utilizar fuentes verificables, registrar enlaces y fechas de consulta, y distinguir hechos, inferencias y recomendaciones.
6. No asumir que las tecnologías propuestas en documentos anteriores están aprobadas.
7. No inventar resultados de investigación ni afirmar que se consultaron fuentes no consultadas.
8. No sobrescribir documentos existentes; presentar primero el plan y las preguntas pendientes para revisión humana.

## Áreas, responsables y criterios de aceptación

| # | Área | Responsable | Entregable | Criterios de aceptación | Estado |
|---|------|-------------|------------|------------------------|--------|
| A1 | Problemas de clubes y entrenadores | `researcher` (+apoyo `product-analyst`) | `01-problemas-clubes-entrenadores.md` | ≥3 fuentes verificables por problema; URL + fecha de consulta; clasificación Hecho/Hallazgo/Inferencia/Recomendación/Pendiente; problemas priorizados sin inventar datos | Cumplido con limitaciones declaradas |
| A2 | Delimitación MVP vs. futuro | `product-analyst` (+apoyo `researcher`) | `02-mvp-vs-futuro.md` | Cada funcionalidad etiquetada MVP/futuro/pendiente; recorrido vertical con criterios de aceptación; ambigüedades señaladas, no resueltas; sin elegir stack | Cumplido con reservas (propuesta) |
| A3 | Requisitos de arquitectura, seguridad, privacidad, permisos y trazabilidad | `governance-analyst` (+`researcher` para fuentes) | `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` | Requisitos verificables con fuente; permisos por rol como pendiente de aprobación; sin declarar cumplimiento legal | Cumplido con reservas (propuesta) |
| A4 | Preguntas antes de elegir tecnologías | `researcher` (consolida; aportan los 3) | `04-preguntas-antes-elegir-tecnologias.md` | Cada pregunta con dueño, categoría, estado y decisión que desbloquea; ninguna respondida | Cumplido |
| A5 | Bitácora de evidencia (transversal) | `researcher` revisado por `governance-analyst` | `05-bitacora-fuentes.md` | Formato obligatorio por fuente; registro completo; sin citas fabricadas | Cumplido con vacíos declarados |

## Contexto de ejecución confirmado

- Jurisdicción confirmada por el usuario: **España/UE, con menores de edad entre los atletas**.
- Ruta de entregables aprobada por el usuario: `docs/research/fase1/`.
- Aprobación del plan: el usuario aprobó iniciar la FASE 1 en modo solo lectura.

## Orden de ejecución utilizado

1. Paralelo: `researcher` (A1) + `governance-analyst` (A3).
2. `product-analyst` (A2) con los resultados de A1.
3. `researcher` (A4 + A5) consolidando A1–A3.
4. Síntesis presentada a revisión humana antes de escribir este directorio.

## Documentos de esta FASE 1

- `00-plan-investigacion.md` (este archivo).
- `01-problemas-clubes-entrenadores.md` — A1.
- `02-mvp-vs-futuro.md` — A2.
- `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` — A3.
- `04-preguntas-antes-elegir-tecnologias.md` — A4.
- `05-bitacora-fuentes.md` — A5.

## Decisiones que requieren aprobación humana (consolidado D-01…D-20)

Ver detalle en `05-bitacora-fuentes.md`. Ninguna decisión de esta lista está aprobada.

D-01 alcance del MVP · D-02 multi-club desde el MVP · D-03 matriz de permisos por rol · D-04 registro de consentimiento de menores · D-05 base jurídica por tratamiento y EIPD · D-06 nivel ASVS · D-07 RPO/RTO y respaldos · D-08 presupuesto mensual máximo · D-09 ámbito federado o libre · D-10 imágenes/difusión de menores · D-11 riesgos R-01…R-08 · D-12 stack/ADR (NO aprobado) · D-13 proveedor/modelo de OpenCode · D-14 revalidación normativa · D-15 DPD · D-16 datos de salud en fases futuras · D-17 plan de entrevistas a clubes y datos de mercado · D-18 alcance de bitácora de auditoría · D-19 región de alojamiento · D-20 adopción formal del estándar de evidencia y de los requisitos de A3.

## Limitaciones generales de la FASE 1

- Evidencia normativa basada en **extractos de búsqueda**, no en PDFs íntegros.
- **Sin validación con clubes ni entrenadores reales** (sin entrevistas).
- Sin datos de mercado del sector.
- El acceso a EUR-Lex para el RGPD falló en A1 (URL localizada después, sin descarga íntegra).
- Divergencia de esquemas de permisos de OpenCode v1 (`permission`) vs. v2 (`permissions`): verificar la versión instalada antes de configurar.

## Reglas aplicadas durante la ejecución

- No se modificó, creó ni borró ningún archivo hasta que el usuario salió del modo plan y pidió la escritura.
- No se instaló dependencias ni se escribió código.
- No se seleccionó ni recomendó tecnología ni proveedor.
- No se declaró aprobado ningún documento existente (`README.md`, `product/volterra-scope.md`, `decisions/stack-evaluation.md`, `governance/*` siguen en su estado previo).
- No se imprimieron claves, contraseñas ni variables de entorno.
