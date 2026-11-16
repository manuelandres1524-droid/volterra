# Registro de decisiones — VOLTERRA

**Estado:** registro creado el 22/10/2026; sincronizado el 26/10/2026 y el 12/11/2026, y actualizado el 13/11/2026. **9 de las 22 decisiones DEC están aprobadas** (DEC-01, DEC-02, DEC-03, DEC-06, DEC-07, DEC-08, DEC-12, DEC-21, DEC-22) y **5 decisiones N-xx** aprobadas constan en §1.1.

> Este archivo importa las decisiones que la carta de gobernanza exige registrar
> (`governance/governance-charter.md` → *Registro mínimo de decisión*). Su creación
> no aprueba ninguna decisión: las 20 se importaron con el estado del corpus.
>
> **La sincronización del 26/10/2026 (v1.1) asienta las aprobaciones que el propietario
> otorgó el 25/10/2026**, transcritas de `workspace/reanudacion-sesion.md` §4. No se han
> rellenado por inferencia los campos que esa fuente no documenta (opciones consideradas,
> justificación escrita, evidencia adicional). Aprobar una DEC **no cierra** los bloqueos
> jurídicos `E-1`…`E-10` que la condicionan.
>
> **La sincronización del 12/11/2026 (v1.2) asienta el cierre de DEC-12** por decisión del
> propietario en la sesión de OpenCode de ese día: ratificar **FastAPI como BFF**. La decisión
> consta como acto del propietario (N-00); **no hay justificación escrita en la fuente** y no se
> rellena por inferencia. El ADR que la documenta es `decisions/adr/ADR-013-fastapi-bff.md`.
>
> **La sincronización del 12/11/2026 (v1.3) añade DEC-21** para el frontend, aprobada por el
> propietario en la misma sesión: **Jinja2 + HTMX**, sesión con cookie `HttpOnly` + CSRF, F1 en
> solo lectura, interfaz funcional mínima, español `es-CO` y navegadores modernos. El ADR que la
> documenta es `decisions/adr/ADR-014-frontend-jinja-htmx.md`.
>
> **La actualización del 13/11/2026 (v1.4) asienta DEC-06 y DEC-07**, elegidas por el propietario
> en una consulta directa de la sesión: **OWASP ASVS v5.0.0 nivel 2** y **RPO 24 h / RTO 8 h** con
> volcado diario cifrado fuera del proveedor, retención 30 días y responsable el propietario. Las
> preguntas P1 asociadas (`Q-24`, `Q-27`) siguen sin responder y no se fija fecha de revisión; se
> declara como desviación en §3. La matriz ASVS `requisito → estado` aún no existe.
>
> **La actualización del 13/11/2026 (v1.5) amplía DEC-21 a las escrituras de F1**, por aprobación
> del propietario en la sesión de OpenCode: crear/editar club, añadir miembro, cambiar rol y cerrar
> pertenencia **en local y con datos ficticios**, sin despliegue. No es una decisión nueva: es una
> enmienda de alcance. La autorización efectiva sigue en RLS + RPC; el frontend solo oculta
> acciones. Host, datos reales y despliegue siguen fuera.
>
> **La actualización del 13/11/2026 (v1.6) añade DEC-22**, aprobada por el propietario en la sesión
> de OpenCode: **límite de peticiones en memoria por proceso** con **perfil estricto** (login 5/5
> min, refresh 15/5 min, escrituras 15/min, lecturas 120/min) y **logging estructurado en JSON**
> sin datos personales. El ADR que la documenta es
> `decisions/adr/ADR-015-hardening-f1.md`. No cierra la matriz ASVS ni autoriza despliegue.

| | |
|---|---|
| **Norma que lo exige** | `governance/governance-charter.md` § *Registro mínimo de decisión* (9 campos) |
| **Origen de los datos** | `docs/research/fase1-colombia/05-bitacora-fuentes.md` §6 (DEC-01…DEC-20) |
| **Creado** | 22/10/2026, v1.0 |
| **Sincronizado** | 26/10/2026, v1.1 (aprobaciones del 25/10/2026); 12/11/2026, v1.2 (cierre de DEC-12); 12/11/2026, v1.3 (DEC-21); 13/11/2026, v1.4 (DEC-06 y DEC-07); 13/11/2026, v1.5 (DEC-21 se amplía a escrituras); 13/11/2026, v1.6 (DEC-22) |
| **Decisiones DEC registradas** | 22 |
| **Aprobadas (DEC)** | **9** — DEC-01, DEC-02, DEC-03, DEC-06, DEC-07, DEC-08, DEC-12, DEC-21, DEC-22 |
| **Aprobadas (N-xx, §1.1)** | **5** — N-00, N-05, N-07, N-09, N-10 |
| **Pendientes (DEC)** | 13 |
| **Sin decidir (DEC)** | 0 |
| **Aprobador** | El usuario, propietario del proyecto (N-00), como aprobador final |

---

## 0. Cómo leer este registro

### 0.1 Vocabulario de estado

La carta define cinco estados: `borrador` / `propuesta` / `aprobada` / `rechazada` / `sustituida`.
El corpus de investigación usa `Pendiente` y `Sin decidir`.

**Este registro conserva el estado del corpus** para no reescribir la evidencia, y añade el
estado `Aprobada` desde la v1.1. El mapeo al vocabulario de la carta es una **propuesta
pendiente de confirmación**:

| Estado en el corpus | Lectura factual | Equivalente en la carta (**propuesto, no confirmado**) |
|---|---|---|
| `Pendiente` | La decisión está identificada y descrita; no ha entrado al ciclo de aprobación. | `borrador` |
| `Sin decidir` | No hay decisión redactada. | *(sin ficha en el ciclo)* |
| `Aprobada` | El propietario la aprobó el 25/10/2026 (asentado en v1.1). | `aprobada` |

El estado `Aprobada` se usa desde la v1.1 solo en las fichas cuya aprobación consta por escrito
en la fuente citada en su campo *Fuente de la aprobación*.

**Tensión con N-09:** la decisión N-09 fija los estados `PENDIENTE` / `PROPUESTA` / `APROBADA` /
`BLOQUEADA`. Este registro **todavía no** usa ese vocabulario; homologarlo exige revisar las 20
fichas y es un trabajo aparte, no hecho en esta sincronización.

### 0.2 Los 9 campos mínimos de la carta y su origen

| # | Campo de la carta | Origen del dato | Vacío en el corpus |
|---|---|---|---|
| 1 | ID y título | `05-bitacora-fuentes.md` §6 | — |
| 2 | Estado | `05-bitacora-fuentes.md` §6 | — |
| 3 | Responsable que propone / Persona que aprueba | — | **Sí** |
| 4 | Contexto y problema | Título + documento fuente | Parcial |
| 5 | Opciones consideradas | `decisions/stack-evaluation.md` (solo DEC-12) | **Sí**, salvo DEC-12 |
| 6 | Evidencia y fuentes | Referencias `Q-xx`, `E-x`, `R-xx`, `C-xx`, `D-xx`, `F-xx`, `P-xx`, `GC-xx` | — |
| 7 | Decisión y justificación | — | **Sí**, salvo las 4 fichas aprobadas, que tienen decisión pero **no justificación escrita en la fuente** |
| 8 | Riesgos y mitigaciones | `03-requisitos` §3 (R-01…R-11) | Parcial |
| 9 | Fecha, versión y fecha de revisión | Fecha de registro | Fecha de revisión no definida |

**Los campos marcados como vacíos se dejan explícitamente vacíos.** No se rellenan por inferencia.

### 0.3 Referencia de identificadores

| Prefijo | Significado | Dónde se definen |
|---|---|---|
| `DEC-xx` | Decisión que requiere aprobación humana | `05-bitacora-fuentes.md` §6 |
| `Q-xx` | Pregunta abierta (P1/P2/P3) | `04-preguntas-antes-elegir-tecnologias.md` |
| `E-x` | Pregunta de asesoría jurídica colombiana | `03-requisitos-...md` §4 |
| `R-xx` | Riesgo | `03-requisitos-...md` §3 |
| `P-xx` | Requisito | `03-requisitos-...md` §2 |
| `F-xx` | Funcionalidad | `02-mvp-vs-futuro.md` |
| `GC-xx` | Vacío de gobernanza | `05-bitacora-fuentes.md` §5 |
| `C-xx` / `D-xx` | Fuente jurídica / deportiva colombiana | `05-bitacora-fuentes.md` §2 / §3 |

### 0.4 Índice de bloqueo

Ningún ciclo de aprobación puede cerrarse mientras sigan abiertos estos vacíos:

- **10 vacíos legales** `E-1`…`E-10` — requieren asesoría jurídica colombiana. Condicionan parte del alcance de DEC-01 (F7) y bloquean DEC-04, DEC-05, DEC-16, DEC-19.
- **20 preguntas de prioridad P1** de 38 (`Q-01`…`Q-38`).
- ~~**DEC-12 sin decidir**~~ — **cerrada el 12/11/2026**: FastAPI como BFF (ADR-013).

> Aprobar una decisión no cierra sus bloqueos: DEC-01 está aprobada y F7 sigue condicionada a `E-1`; DEC-12 está aprobada pero **no cierra** DEC-19/E-6 ni DEC-05 (DEC-06 y DEC-07 quedaron aprobadas el 13/11/2026).

---

## 1. Resumen de las 22 decisiones

| ID | Título (literal del corpus) | Estado | Aprobador | Bloqueada por |
|---|---|---|---|---|
| DEC-01 | Aprobar el alcance del MVP (F1-F12 + F23 mínimo; F7 condicionado a E-1) | **Aprobada** 25/10/2026 | Propietario | E-1 (solo F7) |
| DEC-02 | Multi-club desde MVP + aislamiento por club_id | **Aprobada** 25/10/2026 | Propietario | — |
| DEC-03 | Aprobar matriz de permisos por rol | **Aprobada** 25/10/2026 | Propietario | Q-23 |
| DEC-04 | Flujo de autorización de representante (E-2, E-7, E-8) | Pendiente | — | E-2, E-7, E-8, Q-15/16/17 |
| DEC-05 | Política de conservación/retención (E-4) | Pendiente | — | E-4, Q-19 |
| DEC-06 | Nivel ASVS | **Aprobada** 13/11/2026 | Propietario | Q-24 sin responder (desviación declarada) |
| DEC-07 | RPO/RTO y política de respaldo | **Aprobada** 13/11/2026 | Propietario | Q-27 sin responder (desviación declarada) |
| DEC-08 | Presupuesto mensual máximo | **Aprobada** 25/10/2026 | Propietario | — |
| DEC-09 | Ámbito federado FVCV vs. no federado | Pendiente | — | Q-10, Q-33 |
| DEC-10 | Imágenes/difusión de menores (fuera por defecto) | Pendiente | — | Q-09 |
| DEC-11 | Aceptar/mitigar riesgos R-01…R-11 (03) | Pendiente | — | — |
| DEC-12 | Selección de stack / ADR — FastAPI como BFF | **Aprobada** 12/11/2026 | Propietario | DEC-19/E-6 y DEC-05 (no bloquean la decisión, sí el uso real) |
| DEC-13 | Proveedor/modelo OpenCode (divergencia v1/v2 permisos) | Pendiente | — | Q-29 |
| DEC-14 | Responsable y periodicidad de revalidación normativa | Pendiente | — | — |
| DEC-15 | Figura de cumplimiento interno (manual art. 17.k; no es DPD europeo) | Pendiente | — | E-9 |
| DEC-16 | Datos de salud (pruebas físicas) en fases futuras (E-3) | Pendiente | — | E-3 |
| DEC-17 | Aprobar plan de validación con clubes y mercado | Pendiente | — | — |
| DEC-18 | Alcance y retención de bitácora de auditoría | **Aprobada (Opción C)** | 16/11/2026 | Q-26 |
| DEC-19 | Región de hosting / transferencia internacional (E-6) | **Aprobada (Opción A)** | 16/11/2026 | E-6, Q-21/Q-30 |
| DEC-20 | Adopción formal del estándar de evidencia y de los requisitos de 03 | Pendiente | — | — |
| DEC-21 | Frontend de F1: Jinja2 + HTMX, sesión por cookie, lecturas y escrituras | **Aprobada** 12/11/2026 | Propietario | Host y DEC-19/E-6 (no bloquean la decisión, sí el uso real) |
| DEC-22 | Hardening de F1: límite de peticiones en memoria y logging estructurado | **Aprobada** 13/11/2026 | Propietario | Host y topología (multi-worker); matriz ASVS pendiente |

### 1.1 Decisiones N-xx aprobadas (25/10/2026)

Estas cinco decisiones **no estaban en el registro** — solo constaban en la nota operativa
`workspace/reanudacion-sesion.md` §4, que se declara a sí misma «no es una decisión aprobada».
La sincronización del 26/10/2026 las asienta aquí como decisiones de negocio aprobadas por el
propietario, con **asiento mínimo**: se transcribe el texto disponible y se deja constancia de
que **no hay ficha de 9 campos** porque la fuente no documenta opciones, evidencia ni
justificación. No se rellenan por inferencia.

| ID | Texto asentado | Estado | Notas |
|---|---|---|---|
| **N-00** | El propietario es aprobador final. | Aprobada 25/10/2026 | Base de la autoridad de aprobación de todo el registro. |
| **N-05** | Observaciones privadas legibles solo por su autor. | Aprobada 25/10/2026 — **provisional** | Sujeta a revisión jurídica. Pertenece a F6; F1 no implementa observaciones. Tensión abierta con el derecho de acceso ARCO (Ley 1581 art. 8), sin ID de decisión asignado. |
| **N-07** | F23 exporta el club excluyendo observaciones privadas. | Aprobada 25/10/2026 | Coherente con N-05. F23 está fuera de F1. |
| **N-09** | Estados: `PENDIENTE`, `PROPUESTA`, `APROBADA`, `BLOQUEADA`. | Aprobada 25/10/2026 | **No aplicada retroactivamente** a este registro: el vocabulario de §0.1 sigue siendo el del corpus (`Pendiente` / `Sin decidir`). Homologarlo exige una revisión aparte. |
| **N-10** | No iniciar E-6, E-4, E-1 ni E-10. | Aprobada 25/10/2026 | Sigue vigente. El arranque de F1 se hizo con una **excepción explícita y documentada** (solo datos ficticios) en `docs/implementation/f1/00-autorizacion-y-alcance.md` §3; la excepción **no** cierra ninguno de los cuatro bloqueos. |

---

## 2. Fichas de decisión

> Cada ficha lleva los 9 campos mínimos de la carta. `Referencias` es un campo adicional
> (la carta exige un *mínimo*, no un máximo).

### DEC-01 — Aprobar el alcance del MVP

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-01 — Aprobar el alcance del MVP (F1-F12 + F23 mínimo; F7 condicionado a E-1) |
| **2. Estado** | **Aprobada** el 25/10/2026 por el propietario. |
| **3. Responsable que propone / Persona que aprueba** | Propuesto por los agentes `researcher` / `product-analyst` / `governance-analyst` de la sesión de investigación del 20-21/10/2026. Aprobado por el usuario, propietario del proyecto (N-00), el 25/10/2026. |
| **4. Contexto y problema** | *(Contexto previo a la aprobación.)* El alcance del MVP no estaba aprobado. La investigación propone F1-F12 + F23 como mínimo, con menores integrados desde F2/F3/F10 y titulares mayores de edad mediante alta propia (P-13). F7 (resultados de competiciones, entrada manual) queda condicionado a la respuesta jurídica E-1. |
| **5. Opciones consideradas** | No consta en el corpus. La distribución por fases (MVP vs. futuro vs. fuera) está en `02-mvp-vs-futuro.md`, pero no está contrastada como opciones de decisión. |
| **6. Evidencia y fuentes** | `docs/research/fase1-colombia/02-mvp-vs-futuro.md`; `04-preguntas-antes-elegir-tecnologias.md` Q-37 (alcance por edades: todas las edades). |
| **7. Decisión y justificación** | **Aprobada.** Texto asentado: «MVP = F1–F12 + F23, sin F7 (condicionada a E-1)». La aprobación consta como acto del propietario; **no hay justificación escrita en la fuente**. F7 sigue condicionada: aprobar el alcance no resuelve `E-1`. |
| **8. Riesgos y mitigaciones** | No consta de forma específica. Riesgo transversal asociado: confundir ranking de club con ranking federativo (`01-problemas...md`, cierre). |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. Aprobada 25/10/2026. Asentada en el registro 26/10/2026 (v1.1). Fecha de revisión: no definida. |
| **Referencias** | Q-37 · Q-14 → E-1 (condiciona F7) · F1-F12, F23 · P-13 |
| **Fuente de la aprobación** | `workspace/reanudacion-sesion.md` §4 (25/10/2026) |

### DEC-02 — Multi-club desde MVP + aislamiento por club_id

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-02 — Multi-club desde MVP + aislamiento por club_id |
| **2. Estado** | **Aprobada** el 25/10/2026 por el propietario. |
| **3. Responsable que propone / Persona que aprueba** | Propuesto por los agentes de la sesión de investigación del 20-21/10/2026. Aprobado por el usuario, propietario (N-00), el 25/10/2026. |
| **4. Contexto y problema** | *(Contexto previo a la aprobación.)* No estaba decidido si el producto nace multi-club o mono-club, ni si el aislamiento por `club_id` se aplica desde la primera versión. La investigación proponía aislamiento multi-club como requisito transversal. |
| **5. Opciones consideradas** | No consta. `decisions/stack-evaluation.md` (pregunta 1) plantea la pregunta sin fijar opciones. |
| **6. Evidencia y fuentes** | `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §2(a) *Arquitectura y separación multi-club*; `decisions/stack-evaluation.md` § *Preguntas necesarias* 1; criterio de matriz *Seguridad y aislamiento multi-club* (15%). |
| **7. Decisión y justificación** | **Aprobada.** Texto asentado: «Multi-club desde MVP, aislamiento estricto, una afiliación activa, historial de transferencias». La aprobación consta como acto del propietario; **no hay justificación escrita en la fuente**. Implementada en F1 como RLS forzada por `club_id` e historial en `club_memberships`. |
| **8. Riesgos y mitigaciones** | No consta de forma específica en el corpus. Riesgo transversal: acceso cruzado entre clubes; mitigado en F1 con RLS `enable`+`force`, políticas por club y pruebas negativas de aislamiento. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. Aprobada 25/10/2026. Asentada en el registro 26/10/2026 (v1.1). Fecha de revisión: no definida. |
| **Referencias** | Relación temática con `stack-evaluation.md` pregunta 1. Sin mapeo explícito a una `Q-xx`. |
| **Fuente de la aprobación** | `workspace/reanudacion-sesion.md` §4 (25/10/2026) |

### DEC-03 — Aprobar matriz de permisos por rol

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-03 — Aprobar matriz de permisos por rol |
| **2. Estado** | **Aprobada** el 25/10/2026 por el propietario. |
| **3. Responsable que propone / Persona que aprueba** | Propuesto en `03-requisitos` §2(d). Aprobado por el usuario, propietario (N-00), el 25/10/2026. |
| **4. Contexto y problema** | *(Contexto previo a la aprobación.)* Existía una matriz de permisos por rol redactada, pero el propio documento la marcaba como **propuesta no aprobada**. El proyecto exige aplicar permisos en servidor y datos, no ocultando controles en la interfaz. |
| **5. Opciones consideradas** | No consta. La matriz de `03` §2(d) es la única propuesta registrada. |
| **6. Evidencia y fuentes** | `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §2(d) *Permisos por rol - matriz propuesta*; `governance/governance-charter.md` § *Decisiones que requieren aprobación humana* (cambios en roles, permisos, privacidad o retención). |
| **7. Decisión y justificación** | **Aprobada.** Texto asentado: «Matriz base de permisos por rol» — la de `03-requisitos` §2(d). La aprobación consta como acto del propietario; **no hay justificación escrita en la fuente**. En F1 se aplica con RLS por club, RPC con guardas y roles en `club_memberships`; los valores por defecto concretos de F1 (solo `platform_admin` crea clubes, designa administradores y edita el perfil del club) son **provisionales** y están en `docs/implementation/f1/00-autorizacion-y-alcance.md`. |
| **8. Riesgos y mitigaciones** | No consta de forma específica. Riesgo asociado: que el control se implemente solo en la interfaz; mitigado en F1 verificando con pruebas negativas en base de datos. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. Aprobada 25/10/2026. Asentada en el registro 26/10/2026 (v1.1). Fecha de revisión: no definida. |
| **Referencias** | Q-23 · `docs/implementation/f1/00-autorizacion-y-alcance.md` |
| **Fuente de la aprobación** | `workspace/reanudacion-sesion.md` §4 (25/10/2026) |

### DEC-04 — Flujo de autorización de representante

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-04 — Flujo de autorización de representante (E-2, E-7, E-8) |
| **2. Estado** | **Pendiente** (`05-bitacora-fuentes.md` §6). No aprobada. |
| **3. Responsable que propone / Persona que aprueba** | Sin asignar. Aprobador: usuario (propietario), sin asignar formalmente. |
| **4. Contexto y problema** | No está definido cómo se autoriza la representación de menores: si una sola autorización cubre fotos, vídeos, resultados y marketing, y cómo se acredita electrónicamente y cómo interviene el derecho a ser escuchado del menor. La investigación advierte explícitamente que **autorización del tutor ≠ identidad verificada del tutor**. |
| **5. Opciones consideradas** | No consta. |
| **6. Evidencia y fuentes** | `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §2(b) *Privacidad (Ley 1581)* y §4 E-2, E-7, E-8; `05-bitacora-fuentes.md` §2 (C-xx, protección de datos). |
| **7. Decisión y justificación** | **Pendiente. No se ha tomado ninguna decisión.** |
| **8. Riesgos y mitigaciones** | No consta. Riesgo asociado en la propia investigación: presentarse como representante legal sin verificación (**R-11**). |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Fecha de revisión: no definida. |
| **Referencias** | E-2, E-7, E-8 · Q-15, Q-16, Q-17 · R-11 |

### DEC-05 — Política de conservación/retención

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-05 — Política de conservación/retención (E-4) |
| **2. Estado** | **Pendiente** (`05-bitacora-fuentes.md` §6). No aprobada. |
| **3. Responsable que propone / Persona que aprueba** | Sin asignar. Aprobador: usuario (propietario), sin asignar formalmente. |
| **4. Contexto y problema** | No está definido cuánto tiempo se conservan los historiales de menores tras la baja, ni las reglas de conservación y eliminación en general. |
| **5. Opciones consideradas** | No consta. |
| **6. Evidencia y fuentes** | `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §2(b) y §4 E-4; `governance/governance-charter.md` § *Gobernanza de datos* (conservación, historial y eliminación). |
| **7. Decisión y justificación** | **Pendiente. No se ha tomado ninguna decisión.** |
| **8. Riesgos y mitigaciones** | No consta. Riesgo transversal: dar de baja sin fijar retención incumple la finalidad declarada. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Fecha de revisión: no definida. |
| **Referencias** | E-4 · Q-19 |

### DEC-06 — Nivel ASVS

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-06 — Nivel ASVS |
| **2. Estado** | **Aprobada** el 13/11/2026 por el propietario (v1.4). |
| **3. Responsable que propone / Persona que aprueba** | Propuesta por el agente, siguiendo la recomendación S-01 de la investigación. Aprueba el usuario (propietario, N-00). |
| **4. Contexto y problema** | No está fijado el nivel de la norma ASVS (OWASP ASVS) que el producto debe satisfacer como objetivo de seguridad verificable. La investigación señala que las referencias de seguridad (OWASP) no dependen de la jurisdicción. |
| **5. Opciones consideradas** | Niveles 1, 2 y 3 de **OWASP ASVS v5.0.0**. Se descarta el nivel 1 por insuficiente para datos personales (S-01) y el nivel 3 por coste de verificación desproporcionado para un MVP con techo de US$0 (DEC-08). |
| **6. Evidencia y fuentes** | `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §2(c) *Seguridad (OWASP - no depende de jurisdicción)* y §2 S-01; `05-bitacora-fuentes.md` §4 (fuentes heredadas F-xx); OWASP ASVS v5.0.0 (mayo 2025). |
| **7. Decisión y justificación** | **Aprobada: OWASP ASVS v5.0.0, nivel 2**, como objetivo verificable. Cada requisito aplicable se cita con su versión (`v5.0.0-x.y.z`) y se mantiene una matriz **requisito → estado** (`cumple` / `no cumple` / `no aplica`) con las excepciones documentadas. Justificación: es el punto de partida que S-01 recomienda para aplicaciones con datos personales y es verificable sin añadir gasto. |
| **8. Riesgos y mitigaciones** | Riesgo: que la matriz quede como documento muerto. Mitigación: revisarla en cada entrega con datos reales. Riesgo: que el nivel 2 no cubra exigencias derivadas de datos de menores; se reevalúa antes de tratar datos reales (`E-1`…`E-10` siguen abiertos). La matriz **no existe todavía**: su creación es trabajo pendiente, no parte de esta aprobación. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. Aprobada 13/11/2026 (v1.4). Fecha de revisión: **pendiente de fijar** (desviación declarada en §3). |
| **Referencias** | Q-24 · S-01 · `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §2(c) |

### DEC-07 — RPO/RTO y política de respaldo

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-07 — RPO/RTO y política de respaldo |
| **2. Estado** | **Aprobada** el 13/11/2026 por el propietario (v1.4). |
| **3. Responsable que propone / Persona que aprueba** | Propuesta por el agente a partir de O-03. Aprueba el usuario (propietario, N-00), que además queda como **responsable** de ejecutar el respaldo. |
| **4. Contexto y problema** | No están fijados los objetivos de punto de recuperación (RPO), de tiempo de recuperación (RTO) ni la política de respaldos, sin los cuales no puede evaluarse el hosting. |
| **5. Opciones consideradas** | (a) RPO 24 h / RTO 8 h con volcado diario cifrado y retención 30 días; (b) RPO 1 h / RTO 4 h, que exige *point-in-time recovery* de pago y choca con DEC-08 (US$0/mes); (c) volcado solo bajo demanda, sin periodicidad. Se elige (a). |
| **6. Evidencia y fuentes** | `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §2(f) *Operación* y §2 O-03; `decisions/stack-evaluation.md` § *Preguntas necesarias* 6 y criterio *Despliegue y operación* (10%); `docs/operations/o-03-respaldo-restauracion.md` §4.1/§4.2. |
| **7. Decisión y justificación** | **Aprobada:** RPO **24 h**, RTO **8 h** (horario laboral), volcado **diario** en formato custom y **cifrado**, almacenado **fuera del proveedor**, retención **30 días**, responsable **el propietario**. No autoriza gasto: el destino debe ser gratuito (almacenamiento local o servicio ya disponible); cualquier servicio de pago exige una decisión nueva (DEC-08). Justificación: cubre la pérdida de un día de trabajo con una ventana de recuperación de una jornada, sin PITR de pago. |
| **8. Riesgos y mitigaciones** | Riesgo: que el plan gratuito de Supabase no incluya la retención asumida → **verificar antes de usar datos reales** y, si no alcanza, cubrirlo con el volcado propio. Riesgo: que el volcado no se ejecute por olvido → calendario y revisión periódica (O-03 §6, O-05). Riesgo: restauración no probada en el proyecto nuevo → el ensayo de O-03 §4.3 sigue pendiente. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. Aprobada 13/11/2026 (v1.4). Fecha de revisión: **pendiente de fijar** (desviación declarada en §3). |
| **Referencias** | Q-27 · O-03 · DEC-08 · `docs/operations/pendientes-bloqueantes.md` §2 |

### DEC-08 — Presupuesto mensual máximo

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-08 — Presupuesto mensual máximo |
| **2. Estado** | **Aprobada** el 25/10/2026 por el propietario. |
| **3. Responsable que propone / Persona que aprueba** | Propuesto por la investigación (`stack-evaluation.md` § *Preguntas necesarias* 4). Aprobado por el usuario, propietario (N-00), el 25/10/2026. |
| **4. Contexto y problema** | *(Contexto previo a la aprobación.)* No existía un techo de gasto mensual. Sin él, la comparación de alternativas de stack y los criterios de costo total no eran evaluables, y la carta exige aprobación humana de presupuesto y de cualquier servicio con costo. |
| **5. Opciones consideradas** | No consta. |
| **6. Evidencia y fuentes** | `decisions/stack-evaluation.md` § *Preguntas necesarias* 4 y criterio *Costo total* (12%); `governance/governance-charter.md` § *Decisiones que requieren aprobación humana* (presupuesto o nuevo servicio con costo). |
| **7. Decisión y justificación** | **Aprobada.** Texto asentado: «Techo de infraestructura y servicios: **US$0/mes**. No autoriza gastos». Es un techo, no una autorización: cualquier servicio de pago exige una decisión nueva del propietario. |
| **8. Riesgos y mitigaciones** | Riesgo asociado: que el techo US$0 se interprete como permiso para contratar servicios gratuitos con condiciones contractuales no evaluadas (por ejemplo, planes gratuitos restringidos a uso no comercial). Mitigación: cada proveedor se evalúa antes de usarse. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. Aprobada 25/10/2026. Asentada en el registro 26/10/2026 (v1.1). Fecha de revisión: no definida. |
| **Referencias** | Q-13 |
| **Fuente de la aprobación** | `workspace/reanudacion-sesion.md` §4 (25/10/2026) |

### DEC-09 — Ámbito federado FVCV vs. no federado

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-09 — Ámbito federado FVCV vs. no federado |
| **2. Estado** | **Pendiente** (`05-bitacora-fuentes.md` §6). No aprobada. |
| **3. Responsable que propone / Persona que aprueba** | Sin asignar. Aprobador: usuario (propietario), sin asignar formalmente. |
| **4. Contexto y problema** | No está decidido si el producto se orienta a clubes federados (FVCV) o no federados. La investigación advierte explícitamente del riesgo de **asumir reglamentos FVCV no leídos**. |
| **5. Opciones consideradas** | No consta. |
| **6. Evidencia y fuentes** | `05-bitacora-fuentes.md` §3 (fuentes deportivas D-01…D-22); `03-requisitos-...md` § *Gobernanza deportiva* (origen y significado de métricas); `01-problemas-clubes-entrenadores.md` (cierre: riesgo de confundir ranking de club con ranking federativo). |
| **7. Decisión y justificación** | **Pendiente. No se ha tomado ninguna decisión.** |
| **8. Riesgos y mitigaciones** | No consta. Riesgo asociado: asumir reglamentos FVCV no leídos (cierre de `05-bitacora-fuentes.md`). |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Fecha de revisión: no definida. |
| **Referencias** | Q-10, Q-33 |

### DEC-10 — Imágenes/difusión de menores (fuera por defecto)

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-10 — Imágenes/difusión de menores (fuera por defecto) |
| **2. Estado** | **Pendiente** (`05-bitacora-fuentes.md` §6). No aprobada. |
| **3. Responsable que propone / Persona que aprueba** | Sin asignar. Aprobador: usuario (propietario), sin asignar formalmente. |
| **4. Contexto y problema** | Está **propuesto** que la difusión de imágenes de menores quede fuera por defecto, pero la propuesta no ha sido aprobada. La investigación registra un precedente sancionatorio directo por tratar imágenes de NNA sin autorización expresa. |
| **5. Opciones consideradas** | No consta. |
| **6. Evidencia y fuentes** | `05-bitacora-fuentes.md` § *Riesgos* (cierre) — precedente sancionatorio directo; `03-requisitos-...md` §2(b). |
| **7. Decisión y justificación** | **Pendiente. No se ha tomado ninguna decisión.** |
| **8. Riesgos y mitigaciones** | No consta. Riesgo asociado: tratar imágenes de NNA sin autorización expresa (cierre de `05-bitacora-fuentes.md`). |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Fecha de revisión: no definida. |
| **Referencias** | Q-09 · E-2 (autorización por finalidad) |

### DEC-11 — Aceptar/mitigar riesgos R-01…R-11

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-11 — Aceptar/mitigar riesgos R-01…R-11 (03) |
| **2. Estado** | **Pendiente** (`05-bitacora-fuentes.md` §6). No aprobada. |
| **3. Responsable que propone / Persona que aprueba** | Sin asignar. Aprobador: usuario (propietario), sin asignar formalmente. |
| **4. Contexto y problema** | Se han documentado 11 riesgos para Colombia, pero no se ha decidido cuáles se aceptan, cuáles se mitigan y con qué medida. Sin esta decisión no hay tratamiento formal del riesgo. |
| **5. Opciones consideradas** | No consta. La estructura del riesgo (descripción, evidencia, severidad, mitigación) está en `03-requisitos` §3. |
| **6. Evidencia y fuentes** | `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §3 *Riesgos (revisados para Colombia)* — R-01…R-11, incluida la verificación de identidad del tutor (**R-11**). |
| **7. Decisión y justificación** | **Pendiente. No se ha tomado ninguna decisión.** |
| **8. Riesgos y mitigaciones** | Por definir: esta decisión *es* el tratamiento de los 11 riesgos. Mitigaciones propuestas ya están descritas en `03-requisitos` §3. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Fecha de revisión: no definida. |
| **Referencias** | R-01…R-11 |

### DEC-12 — Selección de stack / ADR — FastAPI como BFF

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-12 — Selección de stack / ADR — **FastAPI como BFF** |
| **2. Estado** | **Aprobada** el 12/11/2026 por el propietario. Cierra el estado *sin decidir* del corpus. |
| **3. Responsable que propone / Persona que aprueba** | Propuesta documentada por los agentes `architect` / coordinador (matriz y ADR-012) y por la elección provisional de `docs/architecture/backend-choice.md` (31/10/2026). Aprobada por el usuario, propietario del proyecto (N-00), el 12/11/2026 en la sesión de OpenCode. |
| **4. Contexto y problema** | El stack de la capa de aplicación no estaba seleccionado. La matriz de 10 criterios estaba puntuada desde el 26/10/2026 con pesos y filtros confirmados, y el ADR-012 proponía la opción B (estático + PostgREST) sin aprobación. En paralelo existía un backend FastAPI provisional, con JWT de usuario y sin `service_role`, que no coincidía ni con B ni con la variante D puntuada. |
| **5. Opciones consideradas** | **Sí, registradas.** Puntuadas: A Next.js/Vercel (3,96), B estático + PostgREST (4,06), C backend TS aparte (3,65), D Python/FastAPI con conexión directa (2,58, eliminada por el filtro de seguridad). **Variante aprobada: D-BFF** (FastAPI delgado, JWT de usuario, PostgREST/RLS, sin `service_role`), **no puntuada**. El host del BFF no está elegido. |
| **6. Evidencia y fuentes** | `decisions/stack-evaluation.md` · `decisions/dec-12-matriz-puntuada.md` (puntuación 26/10/2026) · `decisions/dec-12-material-decision.md` · `decisions/adr/ADR-012-capa-de-aplicacion.md` (**rechazada**) · `decisions/adr/ADR-013-fastapi-bff.md` (**aprobada**) · `docs/architecture/backend-choice.md` (ratificado el 12/11/2026) · `volterra/apps/integrations/supabase/per_request.py` y `volterra/apps/auth/deps.py` (cliente por petición con JWT, sin `service_role`) · `supabase/README.md` (127 comprobaciones SQL documentadas). |
| **7. Decisión y justificación** | **Aprobada: FastAPI como BFF.** Texto asentado de la instrucción del propietario: «Ratificar FastAPI como BFF». Invariantes: JWT del usuario por petición, clave publicable, sin conexión directa como propietario, sin `service_role` en ningún camino de usuario, autorización efectiva en RLS + RPC, y el BFF sin reglas de dominio. **No consta justificación escrita en la fuente y no se rellena por inferencia.** La matriz **no avala** esta decisión: la variante puntuada de D era la conexión directa eliminada; D-BFF no fue puntuada. Se registra como desviación declarada respecto de la recomendación B y del empate técnico A/B. |
| **8. Riesgos y mitigaciones** | Riesgo principal: que el BFF aloje `service_role` o credenciales de propietario y anule la invariante de seguridad. Mitigación: prohibición explícita, eliminación de `SUPABASE_SERVICE_ROLE_KEY` de la configuración, pruebas negativas y revisión del artefacto. Riesgo de deriva entre guardas del BFF y RLS: prohibir reglas de dominio en Python y probar los caminos negativos en SQL. Riesgo de hosting: el host no está elegido y el despliegue no está autorizado; US$0/mes (DEC-08). Siguen abiertos DEC-19/E-6 y DEC-05 (DEC-06 y DEC-07 se aprobaron el 13/11/2026); el primer dato real los activa. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. **v1.1 (26/10/2026):** respuestas del propietario y matriz puntuada. **v1.2 (12/11/2026):** aprobación de FastAPI como BFF; ADR-012 rechazada y ADR-013 aprobada. Fecha de revisión propuesta: **12/02/2027**, o antes si se cumple un disparador de ADR-013. |
| **Referencias** | `decisions/stack-evaluation.md` · `decisions/dec-12-material-decision.md` · `decisions/dec-12-matriz-puntuada.md` · `decisions/adr/ADR-012-capa-de-aplicacion.md` · `decisions/adr/ADR-013-fastapi-bff.md` · `docs/architecture/backend-choice.md` · Relación con DEC-13 (modelo del proveedor OpenCode). |
| **Fuente de la aprobación** | Sesión de OpenCode del 12/11/2026: respuesta del propietario «Ratificar FastAPI como BFF». No hay documento firmado ni justificación escrita adicional. |

### DEC-13 — Proveedor/modelo OpenCode (divergencia v1/v2 permisos)

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-13 — Proveedor/modelo OpenCode (divergencia v1/v2 permisos) |
| **2. Estado** | **Pendiente** (`05-bitacora-fuentes.md` §6). No aprobada. |
| **3. Responsable que propone / Persona que aprueba** | Sin asignar. Aprobador: usuario (propietario), sin asignar formalmente. |
| **4. Contexto y problema** | No está decidido qué proveedor y modelo de OpenCode usará el proyecto. La investigación detectó una divergencia entre el esquema de permisos de v1 y el de v2. El modelo elegido tiene impacto directo en privacidad, porque el proyecto trata datos de menores. |
| **5. Opciones consideradas** | No consta como lista en el corpus. `decisions/stack-evaluation.md` pregunta 7 la plantea. |
| **6. Evidencia y fuentes** | `decisions/stack-evaluation.md` § *Preguntas necesarias* 7; `governance/governance-charter.md` § *Decisiones que requieren aprobación humana* (proveedor); `03-requisitos-...md` §2(b) (privacidad). |
| **7. Decisión y justificación** | **Pendiente. No se ha tomado ninguna decisión.** |
| **8. Riesgos y mitigaciones** | No consta. Riesgo transversal: enviar datos de menores a un proveedor no evaluado. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Fecha de revisión: no definida. |
| **Referencias** | Q-29 |

### DEC-14 — Responsable y periodicidad de revalidación normativa

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-14 — Responsable y periodicidad de revalidación normativa |
| **2. Estado** | **Pendiente** (`05-bitacora-fuentes.md` §6). No aprobada. |
| **3. Responsable que propone / Persona que aprueba** | Sin asignar. Aprobador: usuario (propietario), sin asignar formalmente. |
| **4. Contexto y problema** | No está definido quién revisa la normativa colombiana aplicable ni con qué periodicidad, de modo que los vacíos legal y las fuentes registradas no tienen un ciclo de revisión. |
| **5. Opciones consideradas** | No consta. |
| **6. Evidencia y fuentes** | `05-bitacora-fuentes.md` §2 (C-01…C-10) y §6 (vacíos E-1…E-10); `governance/governance-charter.md` § *Gobernanza operativa* (revisión periódica). |
| **7. Decisión y justificación** | **Pendiente. No se ha tomado ninguna decisión.** |
| **8. Riesgos y mitigaciones** | No consta. Riesgo transversal: confundir borradores con norma vigente (cierre de `05-bitacora-fuentes.md`). |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Fecha de revisión: no definida. |
| **Referencias** | Sin mapeo explícito a `Q-xx` en el corpus. |

### DEC-15 — Figura de cumplimiento interno (manual art. 17.k)

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-15 — Figura de cumplimiento interno (manual art. 17.k; no es DPD europeo) |
| **2. Estado** | **Pendiente** (`05-bitacora-fuentes.md` §6). No aprobada. |
| **3. Responsable que propone / Persona que aprueba** | Sin asignar. Aprobador: usuario (propietario), sin asignar formalmente. |
| **4. Contexto y problema** | No está decidido si VOLTERRA queda obligada a designar una figura de cumplimiento interno conforme al art. 17.k de la ley colombiana o a una oficina de cumplimiento según tamaño. El corpus advierte expresamente que **no es el DPD europeo**, para no arrastrar un marco normativo equivocado. |
| **5. Opciones consideradas** | No consta. El propio `03-requisitos` §4 E-9 acota la pregunta. |
| **6. Evidencia y fuentes** | `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §4 E-9; `05-bitacora-fuentes.md` §2 (C-xx). |
| **7. Decisión y justificación** | **Pendiente. No se ha tomado ninguna decisión.** |
| **8. Riesgos y mitigaciones** | No consta. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Fecha de revisión: no definida. |
| **Referencias** | E-9 |

### DEC-16 — Datos de salud (pruebas físicas) en fases futuras (E-3)

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-16 — Datos de salud (pruebas físicas) en fases futuras (E-3) |
| **2. Estado** | **Pendiente** (`05-bitacora-fuentes.md` §6). No aprobada. |
| **3. Responsable que propone / Persona que aprueba** | Sin asignar. Aprobador: usuario (propietario), sin asignar formalmente. |
| **4. Contexto y problema** | Los datos de salud (pruebas físicas) están fuera del MVP, pero se ha dejado planteada su entrada en fases futuras sin resolver si requieren autorización expresa adicional, manejo reforzado y articulación con federaciones o seguros. |
| **5. Opciones consideradas** | No consta. |
| **6. Evidencia y fuentes** | `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §4 E-3 y §2(b); `02-mvp-vs-futuro.md` (F21-F22 fuera del MVP). |
| **7. Decisión y justificación** | **Pendiente. No se ha tomado ninguna decisión.** |
| **8. Riesgos y mitigaciones** | No consta. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Fecha de revisión: no definida. |
| **Referencias** | E-3 |

### DEC-17 — Aprobar plan de validación con clubes y mercado

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-17 — Aprobar plan de validación con clubes y mercado |
| **2. Estado** | **Pendiente** (`05-bitacora-fuentes.md` §6). No aprobada. |
| **3. Responsable que propone / Persona que aprueba** | Sin asignar. Aprobador: usuario (propietario), sin asignar formalmente. |
| **4. Contexto y problema** | No hay un plan aprobado de validación con clubes objetivo y con el mercado, que es lo que permitiría confirmar o corregir los 12 problemas de investigación antes de construir. |
| **5. Opciones consideradas** | No consta. |
| **6. Evidencia y fuentes** | `01-problemas-clubes-entrenadores.md` (12 problemas reclasificados para Colombia); `05-bitacora-fuentes.md` §5 (vacíos de evidencia GC-01…GC-11). |
| **7. Decisión y justificación** | **Pendiente. No se ha tomado ninguna decisión.** |
| **8. Riesgos y mitigaciones** | No consta. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Fecha de revisión: no definida. |
| **Referencias** | Sin mapeo explícito a `Q-xx` en el corpus. |

### DEC-18 — Alcance y retención de bitácora de auditoría

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-18 — Alcance y retención de bitácora de auditoría |
| **2. Estado** | **Aprobada — Opción C (riesgo aceptado, sin cambio RLS)**. Resuelta el 16/11/2026. |
| **3. Responsable que propone / Persona que aprueba** | Propuesto por auditoría de seguridad (run-1, F-02). Aprobado por propietario (usuario). |
| **4. Contexto y problema** | Está propuesto un requisito de trazabilidad (bitácora de auditoría) pero no están fijados su alcance ni su periodo de retención, lo que incide directamente en el tratamiento de datos y en el coste operativo. `memberships_select` oculta a `club_admin` las pertenencias cerradas, pero `audit_select` le deja leer los `audit_events` de su club y `trg_audit_memberships` guarda `before_data/after_data` (UUID, rol, fechas). |
| **5. Opciones consideradas** | A) Restringir `audit_select` para `club_admin` (solo `platform_admin` ve membresías); B) Redactar snapshots en trigger para `club_admin`; C) Aceptar riesgo (sin cambio RLS). |
| **6. Evidencia y fuentes** | `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §2(e) *Trazabilidad*; `governance/governance-charter.md` § *Gobernanza de IA/agentes*; `docs/security/asvs-l2-f1.md` (F-02); auditoría run-1 (`findings.json`, `REPORT.md`). |
| **7. Decisión y justificación** | **Opción C — Riesgo aceptado, sin cambio de RLS.** `club_admin` mantiene visibilidad actual de `audit_events`. Riesgo medio: puede correlacionar UUIDs con personas, pero no hay nombres ni correos en claro. Sin migración SQL ni cambios de código. Revisar si se correlaciona UUID con persona. |
| **8. Riesgos y mitigaciones** | Riesgo medio: `club_admin` ve UUIDs, rol y fechas en `audit_events`. Mitigación: no hay PII en claro; si se requiere mayor protección, aplicar Opción A o B en revisión futura. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Resuelta 16/11/2026 (Opción C). Fecha de revisión: pendiente (revisar si se correlaciona UUID con persona). |
| **Referencias** | Q-26 |

### DEC-19 — Región de hosting / transferencia internacional (E-6)

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-19 — Región de hosting / transferencia internacional (E-6) |
| **2. Estado** | **Aprobada — Opción A (hosting en región LATAM)**. Resuelta el 16/11/2026. |
| **3. Responsable que propone / Persona que aprueba** | Propuesto por auditoría de seguridad (run-1, F-07/F-10/F-11). Aprobado por propietario (usuario). |
| **4. Contexto y problema** | No está decidida la región de hosting ni evaluada la transferencia internacional de datos. La investigación advierte de **transferencias internacionales sin evaluar el art. 26**. |
| **5. Opciones consideradas** | A) Hosting en región LATAM (Bogotá/São Paulo) — menor latencia, simplifica art. 26; B) Hosting US/EU con transferencia internacional evaluada; C) Híbrido (datos en LATAM, compute en US/EU). |
| **6. Evidencia y fuentes** | `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §4 E-6 y §2(b); `05-bitacora-fuentes.md` §2 (C-xx); `decisions/stack-evaluation.md` (alternativas de hosting). |
| **7. Decisión y justificación** | **Opción A — Hosting en región LATAM.** Desplegar en región cercana a usuarios (ej. AWS `sa-east-1` São Paulo o GCP `southamerica-east1`). Menor latencia para usuarios colombianos; simplifica cumplimiento art. 26 (no hay transferencia internacional si los datos se alojan en LATAM). |
| **8. Riesgos y mitigaciones** | Riesgo bajo: costo potencialmente mayor; menos opciones de servicios managed. Mitigación: evaluar costos en la región elegida antes de desplegar. E-5 (costo operativo) sigue pendiente de evaluación. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Resuelta 16/11/2026 (Opción A). Fecha de revisión: pendiente (evaluar costos en región LATAM). |
| **Referencias** | E-6 · Q-21, Q-30 |

### DEC-20 — Adopción formal del estándar de evidencia y de los requisitos de 03

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-20 — Adopción formal del estándar de evidencia y de los requisitos de 03 |
| **2. Estado** | **Pendiente** (`05-bitacora-fuentes.md` §6). No aprobada. |
| **3. Responsable que propone / Persona que aprueba** | Sin asignar. Aprobador: usuario (propietario), sin asignar formalmente. |
| **4. Contexto y problema** | Existe un estándar de evidencia redactado y un conjunto de requisitos propuestos, pero **no han sido adoptados formalmente**: siguen siendo propuestas y el documento que los contiene está marcado como estado base de discusión. |
| **5. Opciones consideradas** | No consta. |
| **6. Evidencia y fuentes** | `governance/research-evidence-standard.md`; `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` §2 (30+ requisitos con evidencia [J]/[H]/[R]/[I]/[A]); `product/volterra-scope.md` (*"Estado: base de discusión, no especificación aprobada"*). |
| **7. Decisión y justificación** | **Pendiente. No se ha tomado ninguna decisión.** |
| **8. Riesgos y mitigaciones** | No consta. Riesgo transversal: la carta exige distinguir hipótesis de hechos; sin adopción formal no hay norma exigible. |
| **9. Fecha, versión y fecha de revisión** | Registrada 21/10/2026. v1.0. Fecha de revisión: no definida. |
| **Referencias** | Sin mapeo explícito a `Q-xx` en el corpus. |

### DEC-21 — Frontend de F1: Jinja2 + HTMX, sesión por cookie y escrituras

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-21 — Frontend de F1: **Jinja2 + HTMX**, sesión por cookie `HttpOnly` + CSRF y alcance de **lectura y escritura** |
| **2. Estado** | **Aprobada** el 12/11/2026 por el propietario. **Ampliada el 13/11/2026** a las escrituras de F1 en local, con datos ficticios y sin despliegue (v1.5). |
| **3. Responsable que propone / Persona que aprueba** | Propuesta documentada por el coordinador en el plan de frontend del 12/11/2026. Aprobada por el usuario, propietario del proyecto (N-00), con la respuesta «Apruebo» a ese plan. |
| **4. Contexto y problema** | El BFF FastAPI ya expone lecturas de F1 (`/api/v1/me/`, `/clubs/me`, `/clubs/{id}`, `/clubs/{id}/members`, `/platform/overview`), pero no existe frontend ni stack de presentación aprobado. Sin interfaz, la demo exige llamadas manuales o un *smoke test*. La migración `20261102120000_f1_is_platform_admin.sql` sigue pendiente en el proyecto remoto: sin ella, toda pantalla autenticada recibirá `503`. **(Actualizado 12/11/2026: ya está aplicada y verificada; ver §8.)** |
| **5. Opciones consideradas** | **Frontend:** A) SPA React + TypeScript + Vite; **B) FastAPI + Jinja2 + HTMX (elegida)**; C) Next.js; D) SvelteKit/Astro. **Sesión:** 1) token en `localStorage`; 2) token en memoria; **3) cookie `HttpOnly` + CSRF en el BFF (elegida)**. La opción B evita un segundo servicio y un segundo host; la sesión 3 evita exponer tokens a JavaScript. |
| **6. Evidencia y fuentes** | `decisions/adr/ADR-014-frontend-jinja-htmx.md` (decisión y consecuencias) · `decisions/adr/ADR-013-fastapi-bff.md` (BFF, JWT de usuario, sin `service_role`) · `docs/implementation/f1/02-demo-local.md` (flujo local) · `volterra/apps/web/` (rutas, plantillas y estáticos) · `volterra/apps/auth/session.py` (cookies y CSRF) · `volterra/apps/services/f1_reads.py` (lecturas compartidas) · `volterra/tests/test_web_session.py` y `test_f1_reads.py` (pruebas ejecutadas). |
| **7. Decisión y justificación** | **Aprobada.** Texto asentado: «Apruebo» al plan que proponía **Jinja2 + HTMX**, **cookie `HttpOnly` + CSRF**, **F1 en solo lectura primero**, **UI funcional mínima**, **español `es-CO`** y **navegadores modernos**. Justificación registrada en el plan: un solo servicio y un solo host, sin token en el navegador, coste US$0/mes (DEC-08) y menor superficie que una SPA. El frontend **solo oculta** acciones según el rol; la autorización efectiva sigue en RLS + RPC y el BFF no reimplementa reglas de dominio (ADR-013). Las escrituras quedaron fuera porque los endpoints de escritura de F1 todavía no existían. **Enmienda del 13/11/2026:** el propietario aprobó ampliar el alcance a las **escrituras de F1** (crear y editar club, añadir miembro, cambiar rol y cerrar pertenencia) **en local, con datos ficticios y sin despliegue**. Se implementan como formularios HTML que llaman a las RPC `SECURITY DEFINER` ya existentes (`fn_create_club`, `fn_update_club`, `fn_add_member`, `fn_change_member_role`, `fn_end_membership`); no se añade ninguna regla de autorización en Python. |
| **8. Riesgos y mitigaciones** | XSS: cookies `HttpOnly` para tokens y CSP `default-src 'self'`; el token no aparece en HTML ni en JavaScript. CSRF: cookie double-submit, campo oculto en formularios y cabecera `X-CSRF-Token` para HTMX/refresh. Deriva entre UI y RLS: pruebas negativas de acceso a club ajeno y de `platform_admin`; la UI no autoriza. Filas invisibles por RLS (un entrenador no ve perfiles de compañeros): la página declara que solo muestra lo que los permisos permiten leer. **Actualización 12/11/2026:** la migración remota se aplicó y el frontend se verificó de extremo a extremo (37/37); el riesgo de `503` queda cerrado. **Escrituras (13/11/2026):** toda mutación pasa por una RPC con guardas; el BFF solo traduce errores SQLSTATE a HTTP y nunca decide permisos. Riesgo residual: el formulario de alta de miembro pide un UUID a mano (no hay buscador de usuarios en F1); se mitiga validando el formato y dejando que la RPC compruebe existencia y rol. Host y despliegue: siguen bloqueados por DEC-19/E-6 y autorización expresa. |
| **9. Fecha, versión y fecha de revisión** | Registrada 12/11/2026. **v1.1 (13/11/2026):** ampliación a escrituras. Fecha de revisión propuesta: **12/02/2027**, o antes si cambia el stack, la sesión, el alcance de escritura o el host. |
| **Referencias** | `decisions/adr/ADR-014-frontend-jinja-htmx.md` · `decisions/adr/ADR-013-fastapi-bff.md` · DEC-08 (US$0) · DEC-12 (BFF) · DEC-06 (ASVS) · DEC-19/E-6 (región) · `docs/implementation/f1/00-autorizacion-y-alcance.md` · `docs/implementation/f1/02-demo-local.md` · `supabase/migrations/20261026025413_f1_mutations_and_audit.sql` · `supabase/migrations/20261026035037_f1_update_club_profile.sql` · `supabase/migrations/20261026040817_f1_hardening.sql` · `volterra/apps/services/f1_writes.py` · `volterra/tests/test_f1_writes.py` · `volterra/tests/test_web_writes.py` · `supabase/migrations/20261102120000_f1_is_platform_admin.sql`. |
| **Fuente de la aprobación** | Sesión de OpenCode del 12/11/2026: respuesta del propietario «Apruebo» al plan de frontend presentado. No hay documento firmado adicional. |

### DEC-22 — Hardening de F1: límite de peticiones y logging estructurado

| Campo | Valor |
|---|---|
| **1. ID y título** | DEC-22 — Hardening de F1: límite de peticiones **en memoria por proceso** y logging estructurado |
| **2. Estado** | **Aprobada** el 13/11/2026 por el propietario. Implementada en local; sin despliegue. |
| **3. Responsable que propone / Persona que aprueba** | Propuesta presentada por el coordinador en la sesión del 13/11/2026, al acotar «terminar el back». Aprobada por el usuario, propietario del proyecto (N-00), al elegir las opciones «en memoria por proceso» y «perfil estricto». |
| **4. Contexto y problema** | El límite de peticiones figuraba como **condición de entrega no implementada** y no había registro de peticiones ni identificador para correlacionar errores. `/login` aceptaba intentos ilimitados contra GoTrue y cualquier ruta podía saturar el BFF o PostgREST. DEC-06 (ASVS v5 nivel 2) exige controles de anti-automatización y registro, pero su matriz `requisito → estado` sigue sin existir. |
| **5. Opciones consideradas** | **Mecanismo:** A) contador de ventana fija **en memoria por proceso (elegido)**; B) Redis o almacén compartido; C) delegar en el proxy/host. **Umbrales:** 1) permisivo; **2) estricto (elegido)**; 3) perfil recomendado intermedio. Se descartaron B por dependencia y posible coste (DEC-08) y C porque el host no está elegido. |
| **6. Evidencia y fuentes** | `decisions/adr/ADR-015-hardening-f1.md` · `apps/core/ratelimit.py` · `apps/core/logging.py` · `main.py` · `apps/auth/deps.py` · `tests/test_ratelimit.py` · `tests/test_logging.py` · `docs/operations/pendientes-bloqueantes.md` §1. |
| **7. Decisión y justificación** | **Aprobada.** Límite de ventana fija con cerrojo y reloj monótono, clave por IP en ámbitos anónimos y por `sub` en peticiones autenticadas. Perfil estricto: login **5/5 min**, refresh y logout **15/5 min**, escrituras **15/min**, lecturas **120/min**; escrituras sin sesión **15/min por IP**. Logging JSON en stdout con método, ruta sin consulta, estado, duración y `X-Request-ID`; sin correos, contraseñas, cookies, cuerpos ni IP en claro. Justificación: cierra la condición de entrega sin dependencias, servicios ni coste, y hace observable el BFF. **No autoriza**: la autorización sigue en RLS + RPC. |
| **8. Riesgos y mitigaciones** | Multi-worker: el cupo efectivo se multiplica por el número de procesos y se reinicia al reiniciar; se documenta y se revisa al elegir host. IP compartida (NAT, oficina): el perfil estricto puede dar falsos positivos; umbrales configurables y decisión nueva si aparece. Proxy: si se despliega detrás de uno sin `RATE_LIMIT_TRUST_FORWARDED_FOR`, todos comparten la IP del proxy. Logs: el destino y la retención deberán decidirse antes de usar datos reales. **No se declara conformidad ASVS.** |
| **9. Fecha, versión y fecha de revisión** | Registrada 13/11/2026. v1.0. Fecha de revisión propuesta: **13/02/2027**, o antes si se elige host, se despliega con más de un worker o se usan datos reales. |
| **Referencias** | ADR-015 · DEC-06 · DEC-08 · DEC-12 · DEC-21 · DEC-19/E-6 · `docs/operations/pendientes-bloqueantes.md` · `volterra/apps/core/ratelimit.py` · `volterra/apps/core/logging.py` · `volterra/tests/test_ratelimit.py` · `volterra/tests/test_logging.py` |
| **Fuente de la aprobación** | Sesión de OpenCode del 13/11/2026: respuesta del propietario a la consulta de alcance, eligiendo «Hardening mínimo: límite de peticiones + logging», «en memoria por proceso» y «perfil estricto». No hay documento firmado adicional. |

---

## 3. Ciclo de gobernanza aplicado a este registro

Según `governance/governance-charter.md`:

```
Proponer → documentar evidencia → evaluar impacto → revisar con las partes pertinentes
        → aprobar o rechazar → implementar → verificar → revisar periódicamente
```

Estado actual: **9 fichas aprobadas** (DEC-01, DEC-02, DEC-03, DEC-06, DEC-07, DEC-08, DEC-12,
DEC-21, DEC-22), **13 pendientes** y **0 sin decidir**. Además, 5 decisiones N-xx constan aprobadas en §1.1.

**Desviación declarada (DEC-12):** la aprobación del 12/11/2026 no sigue la recomendación de la
matriz (B, 4,06) ni puntúa la variante finalmente adoptada (D-BFF). Se registra como acto del
propietario, sin justificación escrita en la fuente. El ADR-013 fija invariantes y disparadores de
revisión; no cierra DEC-19/E-6 ni DEC-05.

**Desviación declarada (DEC-06 y DEC-07, 13/11/2026):** ambas se aprobaron sin responder sus
preguntas P1 asociadas (`Q-24` y `Q-27`) y sin fijar fecha de revisión; el propietario eligió la
opción recomendada en una consulta directa de la sesión. Además, la matriz `requisito → estado`
que DEC-06 exige **no existe todavía**. Se registran como acto del propietario; el cierre formal
de ambas fichas sigue pendiente.

**Alcance de DEC-21:** la aprobación cubre el frontend de F1 en **solo lectura**. No autoriza
escrituras, despliegue, host, datos reales ni un segundo servicio. La migración remota se aplicó y
se verificó el 12/11/2026 (**37/37** E2E y SMOKE OK); lo que sigue bloqueado es el **host** y
DEC-19/E-6. **La v1.5 amplía el alcance a las escrituras de F1 en local, con datos ficticios y sin
despliegue.**

**Alcance de DEC-22:** el límite de peticiones es **por proceso** y no se comparte entre workers;
los contadores se reinician al reiniciar. La decisión **no** cierra la matriz ASVS de DEC-06 ni
autoriza despliegue, host, datos reales o gasto. Se revisa si cambia la topología o aparecen
falsos positivos por IP compartida.

**Desviación declarada (aprobaciones del 25/10/2026):** las cuatro aprobaciones se asentaron el 26/10/2026 sin que sus fichas
cumplan los cuatro mínimos que esta misma sección exige. En concreto: no consta responsable
proponente formal, no hay justificación escrita, las `Q-xx` P1 asociadas no están todas respondidas
(Q-23 en DEC-03, Q-13 en DEC-08) ni los `E-x` cerrados (E-1 sigue abierto para F7), y no hay fecha
de revisión fijada. La aprobación es un acto del propietario y se registra como tal; el **cierre
formal del ciclo** de esas cuatro fichas sigue pendiente.

**Ninguna ficha de este registro autoriza por sí misma ninguna acción.** Aprobar una ficha exige,
como mínimo:

1. Responder las `Q-xx` P1 que la bloquean (o registrar por escrito que se decide sin ellas).
2. Cerrar los `E-x` que la bloquean, con asesoría jurídica colombiana.
3. Registrar responsable proponente y aprobador en la ficha.
4. Fijar fecha de revisión.

---

## 4. Registro de cambios

| Fecha | Versión | Cambio | Autor |
|---|---|---|---|
| 22/10/2026 | v1.0 | Creación del registro. Importadas DEC-01…DEC-20 con el estado literal del corpus. **Ninguna decisión aprobada.** | OpenCode (agente `volterra-coordinator`), por instrucción del usuario |
| 26/10/2026 | v1.1 | Sincronización con las aprobaciones del 25/10/2026 registradas en `workspace/reanudacion-sesion.md` §4: DEC-01, DEC-02, DEC-03 y DEC-08 pasan a **Aprobada**; se añade §1.1 con las cinco N-xx; se actualizan cabecera, índice de bloqueo y §3. **No** se rellenan opciones, evidencia ni justificación ausentes en la fuente. | OpenCode (agente `volterra-coordinator`), por instrucción explícita del propietario |
| 12/11/2026 | v1.2 | **DEC-12 pasa a Aprobada**: FastAPI como BFF, por instrucción del propietario en la sesión de OpenCode. Se crea `ADR-013-fastapi-bff.md`, se marca `ADR-012` como rechazada, se actualizan cabecera, índice de bloqueo, ficha, §3 y documentos dependientes. Se declara que la variante D-BFF no fue puntuada y que no consta justificación escrita. | OpenCode (coordinador), por instrucción explícita del propietario |
| 12/11/2026 | v1.3 | **DEC-21 pasa a Aprobada**: frontend Jinja2 + HTMX, sesión con cookie `HttpOnly` + CSRF, F1 en solo lectura, UI funcional mínima, español `es-CO` y navegadores modernos. Se crea `ADR-014-frontend-jinja-htmx.md`, se añade la ficha DEC-21 y se actualizan cabecera, resumen, §3 y conteos. La aprobación es la respuesta «Apruebo» al plan de frontend. | OpenCode (coordinador), por instrucción explícita del propietario |
| 13/11/2026 | v1.4 | **DEC-06 y DEC-07 pasan a Aprobada**, elegidas por el propietario en consulta directa de la sesión: OWASP ASVS v5.0.0 **nivel 2**; y **RPO 24 h / RTO 8 h**, volcado diario cifrado fuera del proveedor, retención 30 días, responsable el propietario. Se actualizan cabecera, resumen, fichas, §3 y conteos (8 aprobadas, 13 pendientes). Se declara que `Q-24` y `Q-27` siguen sin responder, que no hay fecha de revisión y que la matriz ASVS no existe todavía. | OpenCode (coordinador), por instrucción explícita del propietario |
| 13/11/2026 | v1.5 | **DEC-21 se amplía a escrituras de F1**: crear/editar club, añadir miembro, cambiar rol y cerrar pertenencia, en local, con datos ficticios y sin despliegue. No cambia el número de decisiones aprobadas (8). Se actualizan cabecera, ficha, §3 y documentos dependientes. La autorización sigue en RLS + RPC. | OpenCode (coordinador), por instrucción explícita del propietario |
| 13/11/2026 | v1.6 | **DEC-22 pasa a Aprobada**: hardening mínimo de F1 con límite de peticiones **en memoria por proceso** y **perfil estricto** (login 5/5 min, refresh/logout 15/5 min, escrituras 15/min, lecturas 120/min) y logging estructurado JSON sin datos personales. Se crea `ADR-015-hardening-f1.md`, se añade la ficha DEC-22 y se actualizan cabecera, resumen, §3 y conteos (**9 aprobadas, 13 pendientes**). No cierra la matriz ASVS ni autoriza despliegue. | OpenCode (coordinador), por instrucción explícita del propietario |
