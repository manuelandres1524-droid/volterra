# FASE 1 (Colombia) — 00: Plan de investigación

**Área:** transversal · **Estado:** propuesta — no aprobada · **Fecha:** 21/10/2026.
**Jurisdicción:** **Colombia** (corrección de la FASE 1 original, que asumía España/UE).
**Modo:** solo lectura. No se instala, escribe código, selecciona tecnología ni despliega.

---

## 1. Decisiones confirmadas por el usuario (21/10/2026)

| # | Decisión | Estado |
|---|---|---|
| 1 | Mercado inicial: **Colombia** | ✅ Confirmada |
| 2 | La plataforma **gestionará datos de atletas menores de edad desde el MVP** | ✅ Confirmada |
| 3 | El **stack tecnológico sigue sin decidirse** | ✅ Confirmada (negativa) |
| 4 | La **gobernanza es transversal** a todos los módulos y agentes | ✅ Confirmada |
| 5 | La investigación debe cubrir clubes y deportistas de **distintas edades, no exclusivamente menores**; protección de menores desde el MVP cuando corresponda, junto con privacidad y seguridad de **todos los usuarios** | ✅ Confirmada (instrucción 21/10/2026) |

> Las decisiones 1, 2, 4 y 5 provienen del usuario (hecho verificado del proyecto). La 3 confirma que sigue pendiente la selección de tecnología (DEC-12, sin aprobar; `D-xx` se renombraron a `DEC-xx` en la bitácora para no colisionar con las fuentes deportivas).

## 2. Cambio de jurisdicción: España/UE → Colombia

La FASE 1 original (docs/research/fase1/) partía de jurisdicción española/UE: RGPD, LOPDGDD, AEPD, RFEVB, RNVP. La versión revisada:

1. **No traslada por analogía** umbrales, obligaciones ni procedimientos españoles (instrucción 5 del encargo).
2. **Conserva** los hallazgos deportivos generales útiles (reglas FIVB, evidencia científica de duplas/carga/lesión, principios multi-club).
3. **Identifica como exclusivos de España** las normas y procedimientos que no son requisito colombiano (apéndice en 01-problemas).
4. **Investiga fuentes oficiales colombianas** con verificación de texto íntegro cuando sea posible (Ley 1581 de 2012, Decreto 1074 de 2015, Ley 1098 de 2006, orientaciones SIC, marco deportivo: Ley 181 de 1995, DL 1228 de 1995, Res. 1286 de 2024, FVCV).

## 3. Áreas de investigación

| Área | Contenido | Fuente base |
|---|---|---|
| A1 — Problemas | 12 problemas de clubes/entrenadores, reclasificados para Colombia | 01-problemas |
| A2 — MVP vs. futuro | Funcionalidades F1–F24, con protección de menores **dentro del MVP** | 02-mvp-vs-futuro |
| A3 — Requisitos | Arquitectura, seguridad (OWASP, no jurisdiccional), privacidad (Ley 1581/Decreto 1074), permisos, trazabilidad | 03-requisitos |
| A4 — Preguntas | Preguntas antes de elegir tecnologías, actualizadas a Colombia | 04-preguntas |
| A5 — Bitácora | Fuentes, vacíos, decisiones DEC-01…DEC-20 revisadas | 05-bitacora |

## 4. Clasificación obligatoria de evidencia (extiende `research-evidence-standard.md`)

Toda afirmación se etiqueta como:

- **Requisito jurídico confirmado** — texto íntegro de fuente oficial colombiana leído y citado (artículo + fuente).
- **Hallazgo de fuente** — extracto o búsqueda sin íntegra; no se afirma verificado.
- **Recomendación de diseño** — no es obligación legal; propuesta sujeta a aprobación.
- **Inferencia** — razonamiento propio, marcado como tal.
- **Requiere asesoría jurídica** — punto que solo un abogado colombiano puede resolver.

## 5. Criterios de aceptación de la FASE 1 (Colombia)

1. Problemas identificados y reclasificados (sin atribuir requisitos españoles a Colombia).
2. MVP delimitado, con protección de menores desde el MVP cuando corresponda, y con privacidad y seguridad de **todos los usuarios**; la investigación cubre clubes y deportistas de distintas edades (instrucción 21/10/2026).
3. Requisitos identificados, separando confirmados / recomendaciones / pendientes.
4. Preguntas antes de elegir tecnologías, actualizadas.
5. Fuentes verificables con URL y fecha de consulta; sin inventar.
6. Hechos, inferencias y recomendaciones claramente separados.
7. Sin asumir tecnologías aprobadas.
8. Sin inventar resultados.

## 6. Limitaciones conocidas

- Fuentes fetiche españolas (RFEVB, RNVP) no aplican; las equivalentes colombianas (reglamentos FVCV de playa) **no se pudieron extraer** del sitio oficial (JS) → vacío declarado.
- La guía SIC sobre NNA (2021) se localizó pero no se leyó íntegramente (Issuu/PDF no parseable).
- El umbral RNBD (>100.000 UVT, Decreto 090 de 2018) es hallazgo de fuente, no texto íntegro leído.
- Ningún texto sustituye asesoría jurídica colombiana (preguntas **E-1…E-10** en `03-requisitos…`).

**Siguiente paso:** aprobación humana del plan y de los requisitos/resultados; ninguna tecnología seleccionada.
