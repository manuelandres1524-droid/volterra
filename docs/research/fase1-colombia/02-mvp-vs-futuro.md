# FASE 1 (Colombia) — 02: MVP vs. funcionalidades futuras

**Área:** A2 · **Estado:** propuesta — no aprobada · **Fecha:** 21/10/2026.
**Jurisdicción:** Colombia. Modo solo lectura. La protección de menores está **dentro del MVP** (decisión confirmada del usuario).

> Conserva la estructura F1–F24 de `docs/research/fase1/02-mvp-vs-futuro.md`. Cambios: protección de menores → MVP; licencias/registros → modelo colombiano (sin RFEVB); referencias RGPD → Ley 1581.

---

## 1. Principios

- MVP = lo mínimo para que 1-3 clubes piloto operen reales durante una temporada, con cumplimiento de Ley 1581 desde el día 1 (no después).
- **Protección de menores = MVP** (autorización de representante, prueba conservable, derechos ARCO-P, minimización).
- En el producto **no hay IA en el MVP** (F21, fuera). La gobernanza transversal aplica a los agentes de desarrollo y a cualquier IA futura: **asiste y explica, no decide**.
- Sin pagos, sin IA del producto, sin ranking "oficial" salvo acuerdo FVCV (todos fuera).

## 2. Tabla de funcionalidades

| ID | Funcionalidad | MVP / futuro | Prioridad MVP | Esfuerzo | Cumplimiento (Colombia) |
|---|---|---|---|---|---|
| F1 | Perfiles de club y usuarios | **MVP** | 1 | 3 | Ley 1581 art. 17 (informar finalidad) |
| F2 | Fichas de atleta (datos básicos) | **MVP** | 1 | 4 | Titular mayor: autorización propia (art. 9) e información (arts. 12, 17); NNA: autorización representante (art. 7 + 2.2.2.25.2.9) y carácter facultativo (art. 12.b) — ver P-13/P-01 en `03` |
| F3 | **Flujo de autorización de representante legal** (alta de menores, prueba conservable, derecho a ser escuchado registrado; verificación de identidad del representante — ver riesgo R-11 en `03`) | **MVP** | 1 | 5 | **Hecho verificado (Ley 1581):** art. 17.b · **Hecho verificado (D. 1074, texto leído vía C-03-3):** arts. 2.2.2.25.2.4/.9 |
| F4 | Gestión de duplas con periodos (historial inmutable) | **MVP** | 2 | 4 | Reglas FIVB (dupla unidad); gobernanza |
| F5 | Entrenamientos y asistencia | **MVP** | 2 | 4 | Finalidad declarada |
| F6 | Observaciones/evaluaciones del entrenador | **MVP** | 3 | 4 | Minimización; acceso por rol |
| F7 | Resultados de competiciones (entrada manual) | **MVP condicionado a E-1** | 3 | 3 | **Pendiente:** ¿dato público? — F7 solo se activa en el MVP si E-1 lo permite; hasta entonces, fuera o limitada a mayores de edad |
| F8 | Informes de evolución (no diagnóstico) | **MVP** | 4 | 4 | Sin promesas de predicción de lesión |
| F9 | Roles y permisos por club (entrenador/admin/atleta/tutor) | **MVP** | 1 | 5 | Art. 17.a/e Ley 1581; seguridad |
| F10 | Registro de consentimientos/autorizaciones (bitácora quién/cuándo/finalidad/prueba) | **MVP** | 1 | 4 | Art. 17.b; precedentes SIC C-07/C-08 |
| F11 | Exportación/retirada de datos del titular | **MVP** | 3 | 3 | Art. 8 (derechos ARCO-P) + art. 15 (vía de reclamo), Ley 1581 |
| F12 | Bitácora de auditoría (acciones sensibles sobre datos personales — con énfasis en NNA) | **MVP** | 2 | 4 | Art. 17; accountability; privacidad por defecto de todos los usuarios |
| F13 | Altas/afiliaciones federativas (liga→FVCV), licencias, certificados | **FUTURO** | — | — | Res. 1286/2024 existente; requiere acuerdo/verificación FVCV (sitio no extraíble) |
| F14 | Sincronización con FVCV/eventos oficiales | **FUTURO** | — | — | No se verificó API/disponibilidad |
| F15 | Pruebas físicas estandarizadas (CMJ, sprint, 5-10-5, 30-15 IFT) | **FUTURO** | — | — | Posible dato de salud → art. 5–6 Ley 1581 (sensibles); autorización expresa adicional |
| F16 | Control de carga/s-RPE/ACWR | **FUTURO** | — | — | Ídem (datos sensibles si implican salud) |
| F17 | Galería de fotos/video con consentimiento por finalidad | **FUTURO** | — | — | Res. SIC 57093/2020 y 21-349477/2022 (imágenes de menores sin autorización → orden de eliminar); autorización expresa separada |
| F18 | Notificaciones push/email | **FUTURO** | — | — | Finalidad y base por informar |
| F19 | Calendario de competiciones | **FUTURO** | — | — | — |
| F20 | Ranking del club (no oficial) | **FUTURO** | — | — | Debe etiquetarse "no oficial" (no hay RNVP colombiano verificado) |
| F21 | IA/ML del producto (asistencia, predicciones) | **FUERA** | — | — | Gobernanza transversal; aprobación explícita |
| F22 | Pagos | **FUERA** | — | — | Dominio suspendido hasta aprobación |
| F23 | Exportación del club (backup) | **MVP mínimo** (recomendación) | 4 | 3 | Recomendación; confirmar con usuario |
| F24 | Multi-club desde el MVP | **PENDIENTE** (Q-01) | — | — | Aislamiento por club_id si se aprueba |

## 3. Reglas transversales del MVP

1. Todo dato personal exige una base registrada: para NNA, autorización del **representante** con prueba (F3/F10); para **titulares mayores**, autorización **propia** del titular (art. 9) salvo excepciones de la ley — alcance de excepciones por confirmar (ver P-13 en `03`).
2. Autorización separada por finalidad (datos vs. imágenes/marketing) — **inferencia** apoyada en el art. 9 (finalidad de la autorización); el art. 12 es deber de informar. **Confirmar con asesoría** (E-2).
3. Silencio = sin autorización (D. 1074 art. 2.2.2.25.2.4).
4. Por defecto: perfiles/rankings no públicos; datos personales mínimos y privacidad por defecto **de todos los usuarios** (con énfasis en NNA).
5. Plazos de atención de titulares colombianos: consulta ≤10 días hábiles (art. 14); reclamo ≤15 días hábiles (art. 15) — **no copiar plazos RGPD**.

## 4. Recorrido vertical del MVP (6 pasos, con criterios)

| Paso | Descripción | Criterios de aceptación |
|---|---|---|
| 1 | Admin crea club, invita entrenadores | Usuario no puede verse a sí mismo como admin de otro club (prueba negativa) |
| 2 | Admin da de alta atleta menor + tutor | Alta requiere autorización del representante; sin ella, alta bloqueada; se registra si el menor fue escuchado |
| 2b | Admin/club da de alta atleta **mayor de edad** | Alta con autorización **propia** del titular (art. 9) y registro de la prueba; sin tutor (ver P-13 en `03`); si el titular es NNA, aplica el paso 2 |
| 3 | Entrenador crea dupla (periodo abierto) | Cambio de integrante cierra periodo y abre otro; el periodo anterior no se modifica |
| 4 | Entrenador registra sesión + asistencia | Solo su club; bitácora registra acción |
| 5 | Se cargan resultados de un torneo | Resultado ligado a dupla y periodo; corregible con trazabilidad |
| 6 | Tutor solicita exportación/rectificación | **Consulta** ≤10 días hábiles (art. 14); **rectificación/supresión vía reclamo** ≤15 días (art. 15) — no conflationar plazos; queda registro |

## 5. Ambigüedades abiertas (actualizadas a Colombia)

| ID | Ambigüedad | Relación |
|---|---|---|
| A1c | ¿Resultados de menores = datos públicos? | E-1 asesoría |
| A2c | ¿Autorización única o por finalidad? | E-2 asesoría |
| A3c | Ranking del club: ¿cuándo y con qué etiqueta "no oficial"? | Q-07 |
| A4c | Multi-club desde MVP | Q-01 |
| A5c | ¿Los atletas menores ven observaciones propias? | Q-23 (matriz de permisos) |
| A6c | ¿Certificado médico (Res. 1286) lo gestiona la plataforma o solo el club? | Q-34 |
| A7c | ¿Afiliación FVCV en alcance? | Q-10 |
| A8c | Retención de datos tras dar de baja un atleta | E-4 asesoría |

---

**Cierre:** F1–F12 + F23 (mínimo) en MVP — **F7 condicionado a E-1**; menores integrados desde F2/F3/F10 y **titulares mayores** vía alta propia (paso 2b, P-13); futuro explícito (F13–F20); fuera (F21–F22). **Archivos modificados:** ninguno hasta este documento. **Pruebas:** n/a (documento). **Riesgos:** subestimar el flujo F3; asumir "resultado público"; confundir "autorización del tutor" con "identidad verificada del tutor" (ver R-11 en `03`); no cubrir titulares de todas las edades (instrucción 21/10/2026, Q-37). **Pendiente:** aprobación del usuario; respuestas E-1…E-4. **Siguiente paso:** 03-requisitos.
