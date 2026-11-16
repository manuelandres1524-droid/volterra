# FASE 1 — A4: Preguntas a resolver antes de elegir tecnologías

> **SUPERADO — este no es el corpus vigente.** Investigación original de FASE 1 para **España/UE** (20/10/2026). El corpus vigente es **[`../fase1-colombia/`](../fase1-colombia/)** (Colombia, 21/10/2026), que sustituye la jurisdicción, las fuentes, los plazos y las decisiones. Este documento se conserva íntegro por trazabilidad histórica: **no usar sus requisitos, plazos ni base jurídica como vigentes**. Índice y alcance: [`README.md`](README.md).

**Área:** A4 · **Agente responsable:** `researcher` (consolida aportaciones de `researcher`, `product-analyst` y `governance-analyst`).
**Estado:** propuesta — no aprobada. **Fecha:** 20/10/2026.
**Modo:** solo lectura. Ninguna pregunta de este documento ha sido respondida; ninguna tecnología seleccionada.

**Leyenda de prioridad:** P1 = bloqueante antes de diseñar/elegir stack · P2 = necesaria antes de la primera entrega · P3 = necesaria antes de ampliar alcance.
**Leyenda de estado:** A = abierta · AP = respondida parcialmente (con lo parcial indicado).

---

## 1. Lista única de preguntas consolidadas (34)

| ID | Pregunta | Categoría | Quién la responde | Qué decisión desbloquea | Estado | Prior. | Origen |
|---|---|---|---|---|---|---|---|
| Q-01 | ¿Multi-club desde el MVP (varios clubes en una misma instalación con aislamiento)? | producto | usuario | Modelo de datos, requisito de aislamiento por `club_id` con pruebas de acceso cruzado, criterio "seguridad y aislamiento" (15%) | A | P1 | stack#1 + A2 + A3 |
| Q-02 | ¿Qué funciones entran exactamente en la primera entrega (confirmar o ajustar el MVP propuesto en A2)? | producto | usuario + validación con clubes | Alcance del MVP, criterio "modelo de datos" (12%), estimación de esfuerzo | AP — propuesta A2 existe; 12 ambigüedades sin cerrar | P1 | stack#2 + A2 |
| Q-03 | ¿Qué volumen inicial de clubes y atletas se espera? | producto | usuario + validación con clubes | Criterios de escala, coste estimado, límites de plataforma | A | P1 | stack#3 |
| Q-04 | ¿Puede un usuario pertenecer a varios clubes a la vez? | producto | usuario + validación con clubes | Modelo de usuarios/membresías, alcance de permisos y de aislamiento | A | P1 | A2 |
| Q-05 | ¿Las duplas son solo un modelo de datos o también operativas (asistencia/observaciones ligados a la dupla)? | producto | usuario + validación con clubes | Modelo de duplas con periodos e historial inmutable | A | P1 | A2 |
| Q-06 | ¿Se permiten sesiones retroactivas (registrar sesiones de fechas pasadas)? | producto | usuario | Reglas de fechas, validaciones y trazabilidad de auditoría | A | P3 | A2 |
| Q-07 | ¿Ranking interno del club (sin cálculo de puntos RNVP) dentro o fuera del MVP? | producto | usuario | Separación ranking competitivo / desarrollo; alcance del MVP | A | P2 | A2 + A1(8) |
| Q-08 | ¿Qué significa "evolución medible": escala de evaluación/observaciones acordada con clubes? | producto | usuario + validación con clubes | Modelo de observaciones y métricas de desarrollo | A | P3 | A2 |
| Q-09 | ¿Imágenes/difusión de menores dentro o fuera del alcance? | legal | usuario + asesoría jurídica | Si se modelan consentimientos de imagen; alcance del MVP | A | P1 | A2 + scope |
| Q-10 | ¿Ámbito federado (clubes afiliados RFEVB/FFAA) o ámbito libre/no federado? | legal | usuario + asesoría jurídica + validación con clubes | Aplicabilidad de normativa federativa, requisitos de licencia/autorización, alcance de datos externos | A | P1 | A2 + A1(3) |
| Q-11 | ¿Se contempla IA/ML dentro del producto VOLTERRA en el horizonte del MVP? (confundir con agentes de desarrollo OpenCode sería un error de alcance) | producto | usuario | Si hay que evaluar costos/APIs de IA; hoy consta como fuera de MVP | A | P3 | stack (nota) + scope |
| Q-12 | ¿Pagos, calendario y notificaciones entran en algún horizonte cercano? | producto | usuario | Ampliación de alcance y criterios de integraciones | A | P3 | scope + A2 |
| Q-13 | ¿Qué presupuesto mensual máximo hay para herramientas e infraestructura? | presupuesto | usuario | Alternativas administradas vs. autoalojadas; criterio "costo total" (12%) | A | P1 | stack#4 |
| Q-14 | ¿Base jurídica de cada tratamiento (consentimiento, contrato, interés legítimo, obligación legal)? | datos-privacidad | asesoría jurídica | Avisos legales, registro de consentimiento, alcance de la EIPD | A | P1 | A3 |
| Q-15 | ¿Flujo de consentimiento para menores: <14 con padres/tutores y 14–17 con el menor — quién, cuándo y cómo se acredita? | datos-privacidad | asesoría jurídica (+ usuario para el diseño) | Requisito "registro de consentimiento de menores con quién/cuándo" | AP — umbral de 14 años confirmado por LO 3/2018 art. 7; diseño y acreditación sin definir | P1 | A2 + A3 + A1(2) |
| Q-16 | ¿Se requiere EIPD (DPIA) y con qué alcance? | datos-privacidad | asesoría jurídica | Plan de cumplimiento y calendario de acciones | A | P1 | A3 |
| Q-17 | ¿Datos de salud (pruebas físicas, control de carga/lesión, s-RPE) en fases posteriores: sí/no y bajo qué salvaguardas? (RGPD art. 9) | datos-privacidad | asesoría jurídica + usuario | Si el modelo de datos debe anticipar categorías especiales; confirma la exclusión actual de pruebas físicas y control de carga | A | P2 | A3 + A2 |
| Q-18 | ¿Quién revalida la normativa y con qué periodicidad? | legal | asesoría jurídica + usuario | Gobernanza de requisitos legales | A | P2 | A2 |
| Q-19 | ¿Es obligatorio/nombrado el DPD y quién es el interlocutor? | legal | asesoría jurídica | Contacto de derechos, canal de reclamaciones, responsabilidades | A | P1 | A3 |
| Q-20 | ¿Nivel de ASVS aplicado (L1/L2/L3) y catálogo de requisitos de seguridad? | seguridad | usuario | Alcance de requisitos y pruebas de seguridad; criterio "seguridad y aislamiento" (15%) | A | P1 | A3 |
| Q-21 | ¿Se aprueba la matriz de permisos por rol propuesta (todavía pendiente)? | seguridad | usuario | Autorización evaluada en servidor y capa de datos; roles de `volterra-scope.md` | AP — propuesta A3 existe, sin aprobar | P1 | A2 + A3 + A1(9) |
| Q-22 | ¿Alcance y responsables de las pruebas de acceso cruzado entre clubes? (depende de Q-01) | seguridad | usuario | Requisito verificable de aislamiento multi-club | A (dependiente de Q-01) | P1 | A3 |
| Q-23 | ¿Bitácora de auditoría: alcance, quién accede, periodo de retención? | seguridad | usuario + asesoría jurídica | Requisito de auditoría y su coste operativo | A | P2 | A3 |
| Q-24 | ¿RPO/RTO objetivo y requisitos de respaldo y recuperación? | operación | usuario | Criterio "despliegue y operación" (10%), backups, estrategia de datos | A | P1 | stack#6 + A3 |
| Q-25 | ¿Se necesitan archivos (fotos/documentos) y tareas en segundo plano desde el comienzo? | operación | usuario | Criterio "autenticación y archivos" (8%), ejecución programada, coste | A | P2 | stack#5 |
| Q-26 | ¿Qué proveedor/modelo está disponible en la instalación de OpenCode? | operación | usuario + investigación adicional | Herramientas de desarrollo (decisión distinta de la IA dentro del producto) | A | P2 | stack#7 |
| Q-27 | ¿Requisito de región de alojamiento de datos (UE/España)? | operación | usuario + asesoría jurídica | Fila "despliegue y operación → región"; compatibilidad con RGPD | A | P2 | matriz stack |
| Q-28 | ¿Quién, cuántas y cuándo: entrevistas a clubes españoles para validar requisitos? | operación | usuario + validación con clubes | Cierre de los vacíos de validación de A1/A2; fiabilidad del MVP | A | P1 | A1 (vacío) + A2 |
| Q-29 | ¿Se investigan datos de mercado del sector (nº de clubes, tamaño, presupuestos)? | operación | investigación adicional | Hipótesis de escala (Q-03) y de precio (Q-13) | A | P2 | A1 (vacío) |
| Q-30 | ¿Se recuperan los PDFs íntegros de la normativa en lugar de extractos? | legal | investigación adicional + asesoría jurídica | Confianza de los requisitos legales (A1 los registró como extractos) | A | P2 | A1 (vacío) |
| Q-31 | RGPD: el acceso de A1 a EUR-Lex quedó bloqueado — ¿se obtiene el texto por vía alternativa? | legal | investigación adicional | Fuente primaria completa para requisitos de privacidad | AP — URL oficial de texto consolidado localizada en A5 (S-09), falta cotejo | P3 | A1 (vacío) |
| Q-32 | ¿Se recuperan las citas exactas (autores, revistas, URLs) de los artículos de s-RPE y ACWR citados por A1? | datos-privacidad | investigación adicional | Evidencia científica verificable del problema 6 — hoy no es bloqueante para el MVP | A | P2 | A1 (6) + A5 |
| Q-33 | ¿Se recuperan los informes íntegros de A1 y A3 (39 fuentes, 14 preguntas, 8 vacíos) para completar esta bitácora? | operación | usuario + investigación adicional | Trazabilidad completa de FASE 1; cierre de Q-29…Q-32 | A | P1 | limitación de A4/A5 |
| Q-34 | ¿Qué nivel de precisión se exige a la evidencia de los problemas 1–12 de A1 antes de aprobar requisitos (confianza "alta" declarada, ¿contraste con fuentes primarias)? | operación | usuario + investigación adicional | Umbral de evidencia para aprobar requisitos de A3 | A | P2 | A1 + estándar de evidencia |

---

## 2. Notas de consolidación (trazabilidad)

- stack#1 → Q-01; stack#2 → Q-02; stack#3 → Q-03; stack#4 → Q-13; stack#5 → Q-25; stack#6 → Q-24 (fusionada con "RPO/RTO" de A3, sin duplicar); stack#7 → Q-26.
- Las 12 ambigüedades de A2 → Q-10, Q-15, Q-09, Q-07, Q-01/Q-04, Q-21, Q-08, Q-04, Q-06, Q-05, Q-18, Q-28.
- De las 14 preguntas/decisiones de A3, en el insumo constan por nombre: DPD (Q-19), base jurídica (Q-14), nivel ASVS (Q-20), RPO/RTO (Q-24), aprobación de matriz (Q-21). **Las restantes: pendiente de recuperación del informe A3** (Q-33).
- **Ninguna pregunta está respondida por este documento**; los estados "parcial" solo reflejan lo que los insumos ya traían confirmado.

---

## 3. Resumen por prioridad

- **P1 (bloqueantes, 14):** Q-01, Q-02, Q-03, Q-04, Q-05, Q-09, Q-10, Q-13, Q-14, Q-15, Q-16, Q-19, Q-20, Q-21, Q-22, Q-24, Q-28, Q-33 — *cualquiera de ellas sin responder impide congelar requisitos o alcance*.
- **P2 (antes de la primera entrega):** Q-07, Q-17, Q-18, Q-23, Q-25, Q-26, Q-27, Q-29, Q-30, Q-32, Q-34.
- **P3 (antes de ampliar alcance):** Q-06, Q-08, Q-11, Q-12, Q-31.

---

## 4. Relación con las decisiones D-01…D-20

Las decisiones que requieren aprobación humana derivadas de estas preguntas están consolidadas en `05-bitacora-fuentes.md` (§ Decisiones D-01…D-20), con el mapeo pregunta → decisión. En particular: Q-01/Q-22 → D-02; Q-02 → D-01; Q-21 → D-03; Q-15 → D-04; Q-14/Q-16 → D-05; Q-20 → D-06; Q-24 → D-07; Q-13 → D-08; Q-10 → D-09; Q-09 → D-10; Q-26 → D-13; Q-18 → D-14; Q-19 → D-15; Q-17 → D-16; Q-28/Q-29 → D-17; Q-23 → D-18; Q-27 → D-19.

---

**Cierre:** A4 completada en modo solo lectura. **34 preguntas consolidadas** sin duplicados, ninguna respondida, ninguna tecnología seleccionada. **Archivos modificados durante la investigación:** ninguno. **Pruebas/ejecución real:** lectura de 6 archivos locales y 7 búsquedas web el 20/10/2026 (1 consulta falló con error 429 y no se reintentó). **Siguiente paso:** que el usuario responda las preguntas P1 o encargue la validación con clubes (Q-28).
