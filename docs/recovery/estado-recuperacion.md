# VOLTERRA — Estado de recuperación del entorno (Fase 1)

| | |
|---|---|
| **Fecha** | Informe: 2026-10-21 · Ejecución posterior: **2026-10-22** (hora local `SA Pacific Standard Time`, UTC−05:00) |
| **Proyecto** | `C:\Users\Miguel\Projects\VOLTERRA` |
| **Encargo** | `C:\Users\Miguel\Documents\nuevoproyecto.txt` — *"VOLTERRA — FASE 1: RECUPERACIÓN DEL ENTORNO"* (38 líneas, reescrito el 21/10 23:37) |
| **OpenCode instalado** | `v2.1.2` (la sesión desaparecida corrió sobre `v1.19.3`) |
| **Modo** | Fase de inspección: solo lectura. Fase posterior (22/10): **reconstrucción aprobada por el usuario** (E-1, E-2, E-5) — ver §11 |
| **Secreto expuesto** | Ninguno. No se imprimieron claves, tokens ni contraseñas. |
| **Stack tecnológico** | **No seleccionado.** Fuera del alcance de esta fase (§9). |
| **Anexo técnico** | `docs/recovery/informe-recuperacion-2026-10-21.md` — línea de tiempo, evidencia y detalle de permisos |

---

## 0. Resumen ejecutivo

**La sesión no se perdió, y la configuración tampoco.** Ambas cosas se recuperaron y, en el caso de la sesión, se identificó la **causa raíz** de por qué dejó de verse.

| Pregunta del encargo | Respuesta | Estado tras la aprobación (22/10) |
|---|---|
| ¿Se perdió la sesión? | **No.** Sigue en `opencode.db`: 97 mensajes, 6 subagentes, 9 rondas de trabajo, íntegros y exportados. **Causa raíz verificada:** la migración de OpenCode v1.19.3 → v2.1.2 cambió el modelo de archivado de sesiones (de un proyecto global a un proyecto **por directorio**). Las 8 sesiones de VOLTERRA siguen bajo `projectID = "global"` y **no existe ningún proyecto asociado a `Projects\VOLTERRA`**, así que la interfaz no tiene nada que mostrar al abrir la carpeta. Los datos están intactos. | **RESUELTO (E-1).** Las 8 sesiones se reubicaron en `Projects\VOLTERRA`. El proyecto `3b56f64fc953aaebd3ed659e3d44852891fe3a4a` se creó y las 8 sesiones constan ya bajo ese `projectID`. |
| ¿Se perdió configuración? | **No.** Existen `AGENTS.md`, los **11 agentes originales**, `governance/` (3 documentos), `workspace/` (3), `product/`, `decisions/` e `integrations/`. Lo que falta es `opencode.json` — y por tanto que el agente coordinador sea el predeterminado. | **RESUELTO (E-2).** `opencode.json` creado y verificado: `opencode debug config` lo lista como documento de configuración del proyecto y `opencode debug agents` devuelve los 11 agentes VOLTERRA. |
| ¿Se inventó algún agente? | **No.** Los 11 se encontraron en disco, se leyeron literalmente y se compararon por hash entre las 4 copias del proyecto. | Sin cambio. |
| ¿Qué falta de verdad? | **Decisiones**, no contexto: 19 decisiones `DEC` abiertas, 38 preguntas (20 bloqueantes), 10 vacíos legales `E-1…E-10` sobre datos de menores, sin stack aprobado, sin registro de decisiones con aprobador y sin control de versiones. | **PARCIAL.** El registro de decisiones ya existe (E-5) con las 20 fichas y los 9 campos de la carta, **ninguna aprobada**. Siguen faltando las 38 respuestas, los 10 vacíos legales, el stack y el control de versiones. |

**Lo que sí estaba en riesgo:** que el trabajo de investigación volviera a ser invisible (R-11) y que se perdiera sin versionado (R-1).
**R-11 queda mitigado** por E-1: las sesiones ya están bajo el proyecto del directorio y aparecen en la interfaz. **R-1 sigue abierto**: no hay repositorio.

**Segundo lote ejecutado el 22/10 (E-3, E-6, E-7):** los 11 agentes usan ya el frontmatter nativo V2 **sin ningún cambio efectivo de permisos**; el corpus `fase1/` (España/UE) está marcado como superado con un índice propio; y la bitácora vigente registra el dictamen de las dos auditorías y el **cierre real de sus 35 hallazgos**, incluidos los dos que nunca se aplicaron (§11.4–§11.6).

---

## 1. Criterio de clasificación

Este informe usa **exactamente las cinco categorías del encargo** (§ Tarea 5). Cada afirmación material del informe está clasificada, y en ningún caso un hallazgo no verificado aparece como verificado.

| Categoría | Significado |
|---|---|
| **A — Recuperado y verificado** | Comprobado directamente en disco o en la base de datos, con evidencia reproducible. |
| **B — Encontrado pero no verificado** | Existe en disco, pero su contenido o su efecto **no pudo comprobarse** sin dejar la inspección de solo lectura. |
| **C — Ausente** | Se buscó en todas las ubicaciones relevantes y **no existe**. |
| **D — Posiblemente perdido** | Debería existir según el funcionamiento esperado y **no se puede recuperar**. |
| **E — Propuesta de reconstrucción pendiente de aprobación** | Recomendación de este informe. **No aplicada, no aprobada.** |

---

## 2. Contexto funcional conservado

Se conserva sin reinterpretar, tal como lo establece el encargo (§ Tarea 6):

- **VOLTERRA es un SaaS para clubes de voleibol playa.**
- **Mercado inicial: Colombia.**
- Contempla **deportistas de distintas edades, incluidos menores**.
- **Seguridad, privacidad y gobernanza son transversales** (producto, datos, arquitectura, agentes y operación).

Verificado en el corpus y en las reglas del proyecto:

- Principio de **fuente única de verdad**: cada dato se registra una vez y se reutiliza.
- **El historial de una dupla no se reescribe** al cambiar sus integrantes.
- **Ranking competitivo separado** de indicadores de desarrollo.
- Los permisos se aplican **en servidor y datos**, no solo ocultando botones.
- La IA asiste al entrenador; **no sustituye su criterio**.
- **ML, deep learning y visión por computador quedan fuera del MVP.**

Ruta: `C:\Users\Miguel\Projects\VOLTERRA\product\volterra-scope.md` (1.388 B) — *"Estado: base de discusión, no especificación aprobada."*

---

## 3. Clasificación del estado

### 3.1 A — Recuperado y verificado

**Agentes (11, originales, sin inventar)**

| # | Ruta exacta | `mode` | `edit` | `bash` |
|---|---|---|---|---|
| 1 | `C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\volterra-coordinator.md` | **primary** | ask | ask |
| 2 | `…\.opencode\agents\researcher.md` | subagent | **deny** | **deny** |
| 3 | `…\.opencode\agents\product-analyst.md` | subagent | **deny** | **deny** |
| 4 | `…\.opencode\agents\architect.md` | subagent | **deny** | **deny** |
| 5 | `…\.opencode\agents\data-architect.md` | subagent | **deny** | **deny** |
| 6 | `…\.opencode\agents\security-auditor.md` | subagent | **deny** | ask |
| 7 | `…\.opencode\agents\governance-analyst.md` | subagent | **deny** | **deny** |
| 8 | `…\.opencode\agents\qa-engineer.md` | subagent | **deny** | ask |
| 9 | `…\.opencode\agents\backend-developer.md` | subagent | ask | ask |
| 10 | `…\.opencode\agents\frontend-developer.md` | subagent | ask | ask |
| 11 | `…\.opencode\agents\technical-writer.md` | subagent | ask | **deny** |

Verificado por lectura literal del frontmatter y por `MD5` sobre las 4 copias del proyecto (archivos compartidos **byte-idénticos**).

**Documentación e instrucciones**

| Ruta exacta | Bytes | Qué aporta |
|---|---|---|
| `…\AGENTS.md` | 721 | 10 reglas vinculantes del proyecto + formato de cierre |
| `…\README.md` | 1.252 | Estado (borrador, no es repo), decisiones pendientes, 6 pasos de uso |
| `…\governance\governance-charter.md` | 2.664 | Estados de decisión (`borrador/propuesta/aprobada/rechazada`) + **registro de decisiones con ID, estado y aprobador** |
| `…\governance\governance-operating-model.md` | 2.736 | Matriz de roles y responsabilidades |
| `…\governance\research-evidence-standard.md` | 1.441 | Estándar de evidencia |
| `…\workspace\agent-workflow.md` | 722 | Ciclo `investigar → diseñar → aprobar → implementar → verificar → entregar` |
| `…\workspace\security-and-permissions.md` | 795 | Política de permisos: solo lectura por defecto, pedir aprobación para escribir |
| `…\workspace\workspace-structure.md` | 1.099 | Estructura propuesta de `docs/` (no construida) |
| `…\product\volterra-scope.md` | 1.388 | Alcance preliminar (§2) |
| `…\decisions\stack-evaluation.md` | 2.272 | Matriz de 11 criterios; **"Estado: pendiente. No hay stack aprobado"** |
| `…\integrations\notebooklm-opencode-assessment.md` | 4.477 | Evaluación NotebookLM (su conclusión sigue vigente: **no hay API pública para cuadernos personales**) |

**Investigación — corpus vigente (`docs/research/fase1-colombia/`)**

Conteos verificados por `Select-String` sobre los archivos, no copiados del historial:

| Elemento | Rango | Cantidad |
|---|---|---|
| Problemas | — | 12 |
| Funcionalidades | `F1`–`F24` | 24 |
| Requisitos | `P-01`–`P-13` | 13 |
| Riesgos | `R-01`–`R-11` | 11 |
| Preguntas abiertas | `Q-01`–`Q-38` | 38 (P1=20, P2=14, P3=4) |
| Decisiones | `DEC-01`–`DEC-20` | 20 (19 pendientes + `DEC-12` "sin decidir") |
| Vacíos legales | `E-1`–`E-10` | 10 |
| Fuentes de derecho colombiano | `C-01`–`C-10` | 10 |
| Fuentes deportivas | `D-xx` | 22 |
| Vacíos de gobernanza | `GC-01`–`GC-11` | 11 |

**Confirmado además:** las correcciones finales de la sesión desaparecida **quedaron persistidas** en disco (`Q-37`, `Q-38`, `P-13`, `E-10`, `DEC-01`…`DEC-20` presentes).

**Sesión desaparecida — recuperada**

| Campo | Valor |
|---|---|
| ID | `ses_ea521a708ffeS45aSnI6YTjuXj` |
| Título | "Leer archivo .txt Nuevo Proyecto en Documentos" |
| Directorio | `C:\Users\Miguel\Projects\VOLTERRA` |
| Ventana | 20/10/2026 14:51 → 21/10/2026 08:35 (local) |
| Mensajes | 97 — exportados de `opencode.db` |
| Subagentes | 6 (`researcher` ×4, `product-analyst`, `governance-analyst`), todos con `parentID` = esa sesión |

Los 6 subagentes corrieron con `edit: deny` / `bash: deny` y **no escribieron un solo archivo**: sus resultados (12 problemas, 39 fuentes, 24 funcionalidades, 30+ requisitos, 34 preguntas, 11 vacíos) salieron íntegros por el canal de solo lectura.

### 3.2 B — Encontrado pero no verificado

| Elemento | Ruta exacta | Por qué no se verificó |
|---|---|---|
| Artefacto comprimido | `…\docs\research\fase1\00-plan-investigacion.zip` (45.934 B, mtime 21/10 01:15:43) | **No se abrió ni descomprimió.** No hay ningún registro de escritura de ese archivo ni en la sesión recuperada ni en `opencode.log`. Su contenido es desconocido y su origen, desconocido. |
| Efecto de `POST /api/session/{id}/move` | Endpoint en la API de OpenCode | El endpoint existe y su contrato está leído (body `{directory}` obligatorio), pero **ejecutarlo muta datos**. El mecanismo de archivado está verificado; el efecto de la corrección está inferido. |
| Versión consolidada de una norma colombiana | Referenciada en `fase1-colombia/03-…` como "art. 3.1.1" | La sesión cerrada en 08:35 la **declaró explícitamente como no leída** (consolidado final). Sigue abierta. Se cerró parcialmente M-07 leyendo D. 1377, que contiene el mapa oficial de compilación hacia D. 1074. |
| Contenido del `00-plan-investigacion.md` de `fase1/` (España/UE) | `…\docs\research\fase1\00-plan-investigacion.md` (5.551 B) | Se verificó su existencia y tamaño, y que **no** fue escrito por la sesión recuperada (mtime 21/10 00:21:21 = log 05:21Z). Su contenido es la versión España/UE, superada por la de Colombia. |
| Estado de la app de escritorio | `C:\Users\Miguel\AppData\Local\Programs\@opencode-aidesktop\OpenCode.exe` (231 MB) | Instalada, último uso **23/09/2026**, workspaces registrados: `-` (raíz) y `C--Users-Mig`. Nunca registró `Projects\VOLTERRA`. No es la vía usada en la sesión de investigación. |

### 3.3 C — Ausente

| Elemento | Dónde se buscó | Por qué importa |
|---|---|---|
| Control de versiones (`.git/`) | `Projects\VOLTERRA` y las otras 3 copias | Sin historial por versiones. El historial solo es reconstruible desde la transcripción de sesión y el log. |
| Agentes globales | `C:\Users\Miguel\.config\opencode\agents|agent|command|skill|plugin\` **y** `C:\Users\Miguel\.opencode` (confirmado: `Test-Path` → `False`) | Los 11 agentes son exclusivamente de proyecto. Sin agentes globales que puedan pisar el rol del coordinador. |
| `docs/architecture/`, `docs/security/`, `docs/testing/`, `docs/operations/` | `…\docs\` | Son **propuesta** de `workspace/workspace-structure.md`, no estructura construida. |
| Código, migraciones, CI, tests, despliegue | `…\` completo | El proyecto es, hoy, documentación y preparación. `README.md`: *"no es un repositorio ni una selección de tecnologías definitiva"*. |
| Configuración de proyecto (modelo, permisos, plugins, MCP) | `…\.opencode\` | Sin `model` por agente (todos heredan el de la sesión) ni MCP de proyecto. |
| `notebooklm-opencode-assessment.md` como integración real | `opencode.jsonc`, `auth.json`, `mcp-auth.json` | **Nada** lo referencia. Solo se menciona en un documento. No hay integración de NotebookLM. |
> **Actualización 22/10 (tras la aprobación):** `opencode.json` y el **registro de decisiones** ya **no están ausentes** — fueron creados por E-2 y E-5 y verificados (§11). Los elementos que siguen en esta tabla **continúan ausentes**.

### 3.4 D — Posiblemente perdido

| Elemento | Evidencia | ¿Recuperable? |
|---|---|---|
| **Versiones anteriores de `nuevoproyecto.txt`** | El archivo se sobrescribió en cada iteración (la versión de 6 fases de 107 líneas fue reemplazada por la actual de 38 líneas el 21/10 23:37) | **No.** Solo existe el texto actual. |
| Historial de cambios por versiones del proyecto | Sin `.git/` en ninguna copia | **No.** Reconstruible solo de forma aproximada desde `opencode.db` + `opencode.log`. |
| Estado de auditoría y cierre de hallazgos | Las 2 auditorías (01:23 y 08:21) y sus correcciones (01:37–01:49 y 08:25–08:35) constan **solo** en la transcripción de sesión | **Sí, y ya se recuperó** → está en el anexo técnico. **No** está en los documentos de investigación. |
| Versión previa de `fase1/00-plan-investigacion.md` | Solo existe la actual (5.551 B) | **Probablemente**, si el ZIP de §3.2 la contiene. **No abierto**, no verificable sin salir de solo lectura. |

### 3.5 E — Propuesta de reconstrucción pendiente de aprobación

**Estado 22/10:** el usuario aprobó la reconstrucción en dos lotes. **E-1, E-2, E-3, E-5, E-6 y E-7 están EJECUTADAS y verificadas** (§11). **E-4, E-8 y E-10** siguen sin aplicar: cada una requiere su propia decisión; E-9 es una recomendación operativa, no una modificación.

| # | Propuesta | Justificación | Estado |
|---|---|---|---|
| E-1 | Reubicar las 8 sesiones de VOLTERRA en `C:\Users\Miguel\Projects\VOLTERRA` con `POST /api/session/{sessionID}/move` | Devuelve el trabajo recuperado a la vista en la interfaz (§4) | **EJECUTADA 22/10** — 8 sesiones movidas; proyecto `3b56f64f…` creado (§11) |
| E-2 | Crear `opencode.json` de proyecto con `default_agent: volterra-coordinator` | La gobernanza no puede depender de que el usuario recuerde cambiar de agente | **EJECUTADA 22/10** — `opencode.json` creado y verificado con `opencode debug config` / `debug agents` (§11) |
| E-3 | Migrar el frontmatter de los 11 agentes a la forma nativa V2 (`permissions:` como lista ordenada `{action, resource, effect}`) | El frontmatter es V1; hoy funciona por la capa de compatibilidad de V2, pero es más frágil a futuro | **EJECUTADA 22/10** — 11 agentes migrados; `opencode debug agents` confirma permisos efectivos idénticos y cuerpo intacto (§11.4) |
| E-4 | Fijar `model` por familia de agentes | Hoy el equipo multiagente hereda el modelo de la sesión → cobertura y coste impredecibles | **Pendiente de aprobación** |
| E-5 | Crear el **registro de decisiones** que exige `governance-charter.md` e importar los 20 `DEC-xx` con estado "pendiente" — **sin aprobar ninguno** | Cierra el vacío de gobernanza más visible sin tocar ninguna decisión | **EJECUTADA 22/10** — `decisions/decision-register.md` creado con las 20 fichas y los 9 campos de la carta; **0 aprobadas** (§11) |
| E-6 | Marcar `docs/research/fase1/` como **versión superada (España/UE)** y `fase1-colombia/` como **vigente** | Hoy conviven dos corpus sin marca de estado; riesgo de citar la fuente equivocada | **EJECUTADA 22/10** — aviso en los 6 documentos + `fase1/README.md`; contenido original intacto (§11.5) |
| E-7 | Incorporar al documento de investigación el dictamen de las 2 auditorías y el estado de cierre de cada hallazgo | Hoy ese estado solo vive en la transcripción de sesión | **EJECUTADA 22/10** — §7 nueva en `fase1-colombia/05-bitacora-fuentes.md` con los 35 hallazgos y sus cierres (§11.6) |
| E-8 | Archivar las 3 copias obsoletas del proyecto | Evitan editar la copia equivocada. **No se borró ninguna** | **Pendiente de aprobación** |
| E-9 | Abrir siempre OpenCode con el directorio de trabajo en `Projects\VOLTERRA` | Activa los 11 agentes, crea el proyecto por directorio y evita que el trabajo nuevo vuelva a archivarse en `global` | **Recomendación operativa** |
| E-10 | Decidir si `canva` MCP se autentica o se retira del config global; decidir si la dependencia huérfana `@opencode-ai/plugin@1.19.3` se elimina o se usa | Higiene de configuración global | **Pendiente de aprobación** |

---

## 4. La sesión desaparecida: causa raíz verificada

**[A]** OpenCode v1.19.3 archivaba todas las sesiones bajo un único proyecto `global` con ruta canónica `/`. OpenCode v2.1.2 crea un proyecto **por directorio**. `GET /api/project` devuelve hoy exactamente **dos** proyectos:

| `projectID` | Ruta canónica | Creado | Activo por última vez |
|---|---|---|---|
| `global` | `/` | 11/09/2026 | 20/10/2026 14:29 |
| `e3613a6e536038d915182451a82eb9e53a5ca88c` | `C:\Users\Miguel` | **21/10/2026 20:33** | 21/10/2026 23:31 |

**[A]** Las **44 sesiones heredadas** —incluidas las **8 de VOLTERRA** (la principal, la previa de las 14:41 y los 6 subagentes)— siguen con `projectID = "global"`. **No existe ningún proyecto asociado a `C:\Users\Miguel\Projects\VOLTERRA`.**

**Consecuencia:** al abrir OpenCode dentro de la carpeta del proyecto, la interfaz lista las sesiones del proyecto asociado a ese directorio y no encuentra ninguna. Para el usuario, la sesión "desapareció". Los datos están íntegros en `opencode.db`.

**Por qué importa que el proyecto `C:\Users\Miguel` se creara el 21/10 20:33:** fue después de instalar v2.1.2 (19:44) y de la migración de base de datos. Antes de ese momento todo colgaba de `global`. La sesión desaparecida corrió el 20–21/10, ya bajo `global`.

---

## 5. Rutas exactas de los archivos encontrados

Raíz canónica: `C:\Users\Miguel\Projects\VOLTERRA` — **42 archivos** (38 originales + 2 informes de recuperación + `opencode.json` + `decisions/decision-register.md`), excluyendo `node_modules`.

### 5.1 Raíz y configuración de agentes

```
C:\Users\Miguel\Projects\VOLTERRA\AGENTS.md                                                        721 B
C:\Users\Miguel\Projects\VOLTERRA\README.md                                                       1252 B
C:\Users\Miguel\Projects\VOLTERRA\opencode.json                                              94 B   CREADO 22/10 (E-2)
C:\Users\Miguel\Projects\VOLTERRA\.opencode\.gitignore                                              63 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\package.json                                             64 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\package-lock.json                                    14628 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\volterra-coordinator.md                        962 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\researcher.md                                  373 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\product-analyst.md                             353 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\architect.md                                   373 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\data-architect.md                              389 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\security-auditor.md                           359 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\governance-analyst.md                        1080 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\qa-engineer.md                                 372 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\backend-developer.md                           347 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\frontend-developer.md                          383 B
C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\technical-writer.md                            372 B
```

`.opencode/node_modules/` existe (dependencias instaladas: `yaml`, `zod`, `@opencode-ai/plugin@1.19.3`) pero **no hay ningún plugin escrito**: la dependencia está declarada y sin uso. `.opencode/.gitignore` excluye `node_modules`, `package.json`, `package-lock.json` y `.gitignore`.

### 5.2 Gobernanza, producto, decisiones, flujo de trabajo

```
C:\Users\Miguel\Projects\VOLTERRA\governance\governance-charter.md                               2664 B
C:\Users\Miguel\Projects\VOLTERRA\governance\governance-operating-model.md                       2736 B
C:\Users\Miguel\Projects\VOLTERRA\governance\research-evidence-standard.md                       1441 B
C:\Users\Miguel\Projects\VOLTERRA\product\volterra-scope.md                                      1388 B
C:\Users\Miguel\Projects\VOLTERRA\decisions\stack-evaluation.md                                   2272 B
C:\Users\Miguel\Projects\VOLTERRA\decisions\decision-register.md                            33802 B   CREADO 22/10 (E-5)
C:\Users\Miguel\Projects\VOLTERRA\integrations\notebooklm-opencode-assessment.md                 4477 B
C:\Users\Miguel\Projects\VOLTERRA\workspace\agent-workflow.md                                     722 B
C:\Users\Miguel\Projects\VOLTERRA\workspace\security-and-permissions.md                           795 B
C:\Users\Miguel\Projects\VOLTERRA\workspace\workspace-structure.md                              1099 B
```

### 5.3 Investigación

```
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1-colombia\00-plan-investigacion.md                  4730 B   VIGENTE
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1-colombia\01-problemas-clubes-entrenadores.md     10238 B   VIGENTE
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1-colombia\02-mvp-vs-futuro.md                      8047 B   VIGENTE
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1-colombia\03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md  16053 B   VIGENTE
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1-colombia\04-preguntas-antes-elegir-tecnologias.md 6914 B   VIGENTE
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1-colombia\05-bitacora-fuentes.md                  27635 B   VIGENTE (§7 auditorías)
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1\00-plan-investigacion.md                         6013 B   SUPERADA (ESPAÑA/UE)
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1\01-problemas-clubes-entrenadores.md            38655 B   SUPERADA (ESPAÑA/UE)
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1\02-mvp-vs-futuro.md                             23775 B   SUPERADA (ESPAÑA/UE)
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1\03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md  26922 B   SUPERADA (ESPAÑA/UE)
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1\04-preguntas-antes-elegir-tecnologias.md          11450 B   SUPERADA (ESPAÑA/UE)
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1\05-bitacora-fuentes.md                           16404 B   SUPERADA (ESPAÑA/UE)
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1\README.md                                         2544 B   ÍNDICE / AVISO DE SUPERACIÓN
C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1\00-plan-investigacion.zip                        45934 B   SIN AUTOR CONOCIDO (§3.2), NO ABIERTO
```

Tamaños medidos el 22/10/2026 con `os.path.getsize` (bytes reales, no caracteres), después de ejecutar E-6 y E-7.

### 5.4 Copias del proyecto (3 obsoletas, byte-idénticas en lo compartido)

| Ruta | Exclusivo |
|---|---|
| `C:\Users\Miguel\Documents\VOLTERRA_OpenCode_Architecture_Starter` | — (19/10 23:42) |
| `C:\Users\Miguel\Downloads\VOLTERRA_OpenCode_Architecture_Starter` | — |
| `C:\Users\Miguel\Downloads\VOLTERRA_OpenCode_Architecture_Starter_v2_Gobernanza\VOLTERRA_OpenCode_Architecture_Starter` | sin `governance-operating-model.md` |

**Ninguna tiene `docs/research/`**: el trabajo de investigación solo sobrevive en `Projects\VOLTERRA` y en `opencode.db`. Junto a la tercera hay un `.zip` de 10.740 B.

### 5.5 Configuración de OpenCode (fuera del proyecto)

```
C:\Users\Miguel\.config\opencode\opencode.jsonc           MCP: canva (remote) + adobe-express (local)
C:\Users\Miguel\.config\opencode\opencode.backup.jsonc    estado anterior (5/10): solo canva
C:\Users\Miguel\.config\opencode\cli.json                 preferencias de terminal
C:\Users\Miguel\.config\opencode\service.json             contraseña del servicio local (NO LEÍDA)
C:\Users\Miguel\.local\share\opencode\auth.json           proveedor google tipo api (CLAVE NO LEÍDA)
C:\Users\Miguel\.local\share\opencode\mcp-auth.json       entrada de canva sin sesión activa
C:\Users\Miguel\.local\share\opencode\opencode.db         196 MB — sesiones, mensajes y partes
C:\Users\Miguel\.local\share\opencode\log\opencode.log    5.994.305 B — cronología en UTC
```

`opencode.jsonc` **no** define `model`, `default_agent`, `permissions`, `agents`, `instructions` ni `plugins`. Solo MCP.

---

## 6. Conexiones verificables

### 6.1 Proveedores y modelos

| Elemento | Estado | Cómo se comprobó |
|---|---|---|
| **`google` (Gemini)** | **Conectado de verdad** | `auth.json` tiene entrada `google` tipo `api` (clave no leída); la API de modelos reporta 6 modelos `active`: `gemini-4-argon`, `gemini-3.8-flash`, `gemini-flash-lite-latest`, `gemini-3-pro-image`, `gemma-4-31b-it`, `lyria-3-pro-preview`; una sesión pasada corrió con `google/gemini-3.8-flash` |
| **`opencode`** (modelos gratuitos) | **Conectado** | 9 modelos `active`, incluido `opencode/big-pickle` (el de esta sesión) |
| **NotebookLM** | **Sin integración** | Ninguna referencia en `opencode.jsonc`, `auth.json` ni `mcp-auth.json`. Solo mencionado en `integrations/notebooklm-opencode-assessment.md`, cuya conclusión (no hay API pública para cuadernos personales; solo NotebookLM Enterprise) **sigue vigente** |

> La afirmación de `notebooklm-opencode-assessment.md` — *"OpenCode está conectado a Gemini mediante una clave de API"* — **queda verificada como cierta** a fecha de hoy. Conectado ≠ con integración de NotebookLM.

### 6.2 Herramientas MCP

| Servidor | Tipo | Estado | Origen |
|---|---|---|---|
| `adobe-express` | local (`npx @adobe/express-developer-mcp@latest`) | **✓ connected** | Global |
| `canva` | remote (`https://mcp.canva.com/mcp`) | **⚠ needs authentication** | Global |

**No hay MCP de proyecto.** La app de escritorio de OpenCode está instalada pero **sin uso desde el 23/09/2026** y sin workspace VOLTERRA registrado.

### 6.3 Entorno

| Elemento | Valor |
|---|---|
| OpenCode | `v2.1.2` (instalado); `opencode2` es un alias residual de la **misma** versión — no hay versiones en paralelo |
| Sesión desaparecida | corrió sobre `v1.19.3` (verificado en el log) |
| Servicio local | `http://127.0.0.1:45278` |
| Zona horaria | `SA Pacific Standard Time` (UTC−05:00); el log usa UTC |

---

## 7. Bloqueos

**B-1 · ~~La gobernanza depende de un gesto manual.~~ → RESUELTO 22/10 (E-2).** `opencode.json` de proyecto creado con `default_agent: volterra-coordinator`; verificado con `opencode debug config`. El coordinador deja de depender de que el usuario recuerde cambiar de agente a mano.

**B-2 · 19 decisiones abiertas y 20 preguntas bloqueantes.** `DEC-01…DEC-20` (19 pendientes, `DEC-12` "sin decidir") y `Q-01…Q-38` (P1=20) sin resolver. Sin el stack aprobado no se puede avanzar.

**B-3 · 10 vacíos legales sin cerrar.** `E-1…E-10` requieren asesoría jurídica en derecho deportivo colombiano. Tratan datos de menores: es el bloqueo de mayor severidad.

**B-4 · Sin control de versiones.** No hay `.git`. Y el trabajo de investigación no existe en 3 de las 4 copias.

**B-5 · ~~El trabajo recuperado sigue invisible en la interfaz.~~ → RESUELTO 22/10 (E-1).** Las 8 sesiones se reubicaron en `Projects\VOLTERRA` bajo el proyecto `3b56f64fc953aaebd3ed659e3d44852891fe3a4a`; el proyecto `global` pasó de 41 a 33 sesiones. El trabajo recuperado **ya aparece en la interfaz**.

**B-6 · El estado de auditoría no sobrevive a la sesión.** Las 2 auditorías y el cierre de cada hallazgo solo constan en la transcripción de sesión, no en los documentos de investigación.

**B-7 · Dos corpus conviven sin marca de estado.** `fase1/` (España/UE) y `fase1-colombia/` (Colombia) son ambos "vigentes" a ojos del lector.

---

## 8. Próximos pasos recomendados

Ordenados por dependencia. **Estado 22/10: los pasos 0.1, 1.1 y 1.4 están EJECUTADOS y verificados (§11).** El resto sigue pendiente. Los marcados **[A]** requieren decisión explícita del usuario.

### Fase 0 — Preservación y visibilidad (inmediato)

| # | Paso | Tipo |
|---|---|---|
| 0.1 | **Reubicar las 8 sesiones** de VOLTERRA en `C:\Users\Miguel\Projects\VOLTERRA` vía `POST /api/session/{sessionID}/move` con `{ "directory": "C:\\Users\\Miguel\\Projects\\VOLTERRA" }` — la principal, la previa y los 6 subagentes. Es la única acción que devuelve a la vista el trabajo recuperado | **EJECUTADO 22/10** — las 8 sesiones ya están bajo `Projects\VOLTERRA` (§11) |
| 0.2 | Revisar el contenido de `docs/research/fase1/00-plan-investigacion.zip` y registrar qué contiene | Acción (abre el ZIP, fuera de solo lectura) |
| 0.3 | **Decidir** si se crea el repositorio git ahora o después de cerrar el bloque legal | **[A]** |
| 0.4 | Operar siempre con el directorio de trabajo en `Projects\VOLTERRA` | Recomendación operativa (E-9) |

### Fase 1 — Consolidar la gobernanza (sin stack, sin código)

| # | Paso | Tipo |
|---|---|---|
| 1.1 | **Decidir** `default_agent: volterra-coordinator` en un `opencode.json` de proyecto (E-2) | **EJECUTADO 22/10** — `opencode.json` creado con `default_agent: volterra-coordinator` (§11) |
| 1.2 | **Decidir** la migración del frontmatter de los 11 agentes a la forma V2 nativa (E-3) | **[A]** |
| 1.3 | **Decidir** el modelo por familia de agentes (E-4) | **[A]** |
| 1.4 | Crear el **registro de decisiones** exigido por `governance-charter.md` e importar los 20 `DEC-xx` con estado "pendiente" — **sin aprobar ninguno** (E-5) | **EJECUTADO 22/10** — `decisions/decision-register.md` creado con las 20 fichas, **0 aprobadas** (§11) |
| 1.5 | Registrar los 10 vacíos `E-1…E-10` y las 38 preguntas con su prioridad P1/P2/P3 | Acción |
| 1.6 | Marcar `fase1/` como superada y `fase1-colombia/` como vigente (E-6) | Acción |
| 1.7 | Incorporar el dictamen de las 2 auditorías y el cierre de hallazgos al documento de investigación (E-7) | Acción |
| 1.8 | Archivar las 3 copias obsoletas, tras confirmar el contenido del ZIP (E-8) | **[A]** |

### Fase 2 — Cerrar el bloque legal

| # | Paso | Tipo |
|---|---|---|
| 2.1 | **Decidir** si se contrata asesoría jurídica en derecho deportivo colombiano y con qué alcance | **[A]** |
| 2.2 | Responder las **20 preguntas P1** y dejar constancia de quién respondió | Acción |
| 2.3 | Cerrar `E-1`…`E-10`, o dejar constancia de que quedan abiertos | Acción |
| 2.4 | Confirmar en los requisitos el alcance por edades (ya registrado en `Q-37`: **todas las edades**) | Acción |
| 2.5 | Revisar `P-07`/`S-11` y `P-01`/`P-02`/`T-1`, que la auditoría marcó como `[H]`+`[A]` | Acción |

### Fase 3 — Decidir el stack (fase de arquitectura, **fuera de este encargo**)

| # | Paso | Tipo |
|---|---|---|
| 3.1 | **Confirmar los 11 pesos** de `decisions/stack-evaluation.md` — el propio documento lo exige antes de comparar | **[A]** |
| 3.2 | Puntuar cada alternativa con evidencia, distinguiendo qué criterios son verificables hoy | Acción |
| 3.3 | **Decidir** proveedor y modelo de OpenCode para el proyecto (privacidad: datos de menores) | **[A]** |
| 3.4 | Emitir `DEC-01…DEC-20` con estado y aprobador en el registro de 1.4 | Acción |

### Fase 4 — Construir (solo tras aprobar el stack)

Repositorio → modelo de datos con `data-architect` → arquitectura, permisos de servidor y pruebas con `architect` / `security-auditor` / `qa-engineer` → vertical slice con `backend-developer` / `frontend-developer` **solo con tareas aprobadas** → documentación con `technical-writer`. Cada paso **[A]**.

---

## 9. Límites respetados

Registro explícito conforme a las restricciones obligatorias del encargo:

- **No** se borró, movió, renombró ni sobrescribió ningún archivo.
- **No** se reinstaló ni actualizó nada.
- **No** se modificó ninguna configuración **global** ni conexión (`opencode.jsonc`, `auth.json`, `mcp-auth.json`, `service.json`, `cli.json` intactos). La única configuración creada es **de proyecto** (`Projects\VOLTERRA\opencode.json`), autorizada por el usuario (E-2).
- **No** se instalaron dependencias.
- **No** se modificó código de producto.
- **No** se desplegó nada.
- **No** se seleccionó stack tecnológico (§8 Fase 3, fuera de alcance).
- **No** se afirmó haber recuperado sesiones, agentes o APIs sin comprobarlo: la sesión se recuperó de la fuente real (`opencode.db`), los agentes se leyeron literalmente de disco, y las conexiones se comprobaron con `opencode mcp list`, la API de modelos y la API de proyectos.
- **No** se leyeron ni imprimieron valores de claves, tokens ni contraseñas.
- **No** se abrió el ZIP de `fase1/`.
- **Mutaciones ejecutadas 22/10, con aprobación:** `POST /api/session/{id}/move` sobre las 8 sesiones de VOLTERRA (§11). Fue la única mutación de datos realizada.
- **No** se resolvió ninguna de las 20 preguntas P1 ni ninguna de las 19 decisiones `DEC`. El registro creado (E-5) las **documenta**, no las aprueba.

### Archivos modificados

| Acción | Ruta |
|---|---|
| **Creado (carpeta)** | `C:\Users\Miguel\Projects\VOLTERRA\docs\recovery\` |
| **Creado** | `C:\Users\Miguel\Projects\VOLTERRA\docs\recovery\estado-recuperacion.md` (este informe) |
| **Corregido** | `C:\Users\Miguel\Projects\VOLTERRA\docs\recovery\informe-recuperacion-2026-10-21.md` — se eliminó un bloque duplicado (§1.1, 8 líneas) introducido al escribirlo; el resto del documento se verificó íntegro |
| **Creado (22/10)** | `C:\Users\Miguel\Projects\VOLTERRA\opencode.json` (E-2) |
| **Creado (22/10)** | `C:\Users\Miguel\Projects\VOLTERRA\decisions\decision-register.md` (E-5) |
| **Modificado (22/10)** | Los **11** archivos de `C:\Users\Miguel\Projects\VOLTERRA\.opencode\agents\` — frontmatter V1 → V2 (E-3) |
| **Modificado (22/10)** | Los **6** documentos de `C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1\` — aviso `SUPERADO` al inicio, contenido original intacto (E-6) |
| **Creado (22/10)** | `C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1\README.md` — índice y aviso de superación (E-6) |
| **Modificado (22/10)** | `C:\Users\Miguel\Projects\VOLTERRA\docs\research\fase1-colombia\05-bitacora-fuentes.md` — nueva §7 con los dictámenes de auditoría (E-7) |
| **Modificado (22/10)** | `C:\Users\Miguel\Projects\VOLTERRA\docs\recovery\estado-recuperacion.md` (este informe: secciones §0, §3.3, §3.5, §5, §7, §8, §9 y nueva §11) |
| Borrado | — |
| **Respaldo externo (22/10)** | `C:\Users\Miguel\AppData\Local\Temp\opencode\agents-v1-backup\` — los 11 frontmatter V1 previos a E-3. Fuera del proyecto y en almacenamiento temporal |

### Verificaciones realmente ejecutadas

1. `opencode --version` → **v2.1.2**; `opencode2 --version` → **v2.1.2** (alias, misma versión).
2. `opencode mcp list` → `✓ adobe-express connected`, `⚠ canva needs authentication`.
3. `opencode api get /api/project` → **2 proyectos**: `global` (`/`) y `e3613a6e…` (`C:\Users\Miguel`, creado 21/10 20:33) → base verificada de §4.
4. `opencode api get /api/session` → **43 sesiones**: **41 heredadas con `projectID = "global"`** + 2 en el proyecto `e3613a6e…` (`C:\Users\Miguel`); 8 de ellas son de VOLTERRA (1 actual, 1 principal, 1 previa, 6 subagentes). *(Recuento corregido el 22/10: la cifra "47" de la primera redacción era un artefacto de paginación con cursor repetido.)*
5. `opencode api get /api/experimental/session/{id}/export` → export completo de la sesión principal (3.308.404 B) y de la previa (68.040 B).
6. Parseo con Python → **97 mensajes**, 6 subagentes con `parentID` correcto, 4 mensajes de usuario localizados literalmente.
7. `Get-FileHash -Algorithm MD5` sobre las 4 copias → archivos compartidos **byte-idénticos**; `Projects\VOLTERRA` = superconjunto estricto.
8. `Select-String` sobre `fase1-colombia/` → DEC=20, E=10, R=11, P=13, F=24, Q=38, C=10, D=22, GC=11 (contados, no copiados).
9. Mtimes en ISO de los 12 `.md` de `docs/research/` → coherentes con el log (UTC ↔ local −5).
10. `Select-String` sobre `opencode.log` → escrituras de `fase1/` (05:21Z–05:29Z) y `fase1-colombia/` (13:33Z–13:35Z), evaluaciones de permiso y ausencia de escrituras fuera de las sesiones.
11. `auth.json` (solo claves) → proveedor `google` tipo `api` presente → **Gemini autenticado**.
12. API de modelos → 2 proveedores, 15 modelos, todos `active`.
13. Lectura literal del frontmatter de los **11** agentes → tabla de permisos de §3.1.
14. `Test-Path C:\Users\Miguel\.opencode` → **False**.
15. En disco: `Q-37`, `Q-38`, `P-13`, `E-10`, `DEC-01` presentes → **las correcciones de la sesión desaparecida persistieron**.
16. `GET /openapi.json` → contrato de `POST /api/session/{id}/move` y de los filtros `directory`/`project`.
17. `opencode api get /api/project` (22/10) → **3 proyectos**: `global` (/), `e3613a6e…` (`C:\Users\Miguel`) y **`3b56f64fc953aaebd3ed659e3d44852891fe3a4a`** (`Projects\VOLTERRA`, creado por E-1).
18. `POST /api/session/{id}/move` × 8 (22/10) → las 8 sesiones de VOLTERRA reasignadas; `global` bajó de 41 a 33 y el proyecto nuevo acumula 8.
19. `opencode api get '/api/experimental/session/ses_ea521a708ffeS45aSnI6YTjuXj/export'` **después** del movimiento → export OK, **99 mensajes**: el contenido de las sesiones sobrevivió intacto al traslado.
20. `opencode debug agents` desde `Projects\VOLTERRA` (22/10) → **18 agentes**: los 7 internos (`build`, `plan`, `general`, `explore`, `compaction`, `title`, `summary`) + los **11 VOLTERRA**. Verifica también la traducción de permisos v1→v2: `bash`→`shell`, `task`→`subagent`.
21. `opencode debug config` desde `Projects\VOLTERRA` (22/10) → lista `Projects\VOLTERRA\opencode.json` con `default_agent: volterra-coordinator`.
22. `opencode debug paths` (22/10) → rutas globales confirmadas (`config` = `C:\Users\Miguel\.config\opencode`, `db` = `…\opencode.db`).
23. Conteo automático sobre `decisions/decision-register.md` (22/10) → **20 fichas**, 19 `Pendiente` + 1 `Sin decidir`, **0 aprobadas**, 21 menciones de "No aprobada", los 9 campos de la carta presentes en las 20.
24. `GET /openapi.json` → revisión del esquema de configuración en el binario de OpenCode: `default_agent` = *"Default primary agent to use when no session agent is selected"*.

**No se ejecutó ninguna prueba de código**: el proyecto no tiene código.

---

## 10. Dónde está la evidencia técnica

El anexo `docs/recovery/informe-recuperacion-2026-10-21.md` contiene el detalle de respaldo de este informe:

- Línea de tiempo completa de la sesión recuperada (9 rondas, con herramientas y efecto en disco)
- Diagrama de la arquitectura multiagente y matriz de permisos en 3 niveles
- Inventario con bytes y mtimes, y la cronología de escrituras contrastada con el log
- Registro de las correcciones aplicadas en la ronda final
- Bitácora completa de verificaciones y sus limitaciones

---

## 11. Ejecución posterior a la aprobación (22/10/2026)

El usuario aprobó la reconstrucción de este informe en dos lotes. Se ejecutaron **seis** propuestas —`E-1`, `E-2` y `E-5` en el primer lote; `E-3`, `E-6` y `E-7` en el segundo— y **solo** esas seis.
Ninguna decisión de negocio fue tomada y ningún stack fue seleccionado.

### 11.1 E-1 · Reubicar las 8 sesiones — EJECUTADA

**Qué se hizo:** `POST /api/session/{sessionID}/move` con `{"directory": "C:\\Users\\Miguel\\Projects\\VOLTERRA"}`
sobre las 8 sesiones de VOLTERRA. El endpoint crea el proyecto de destino si no existe.

| Sesión | Agente | `projectID` tras el movimiento |
|---|---|---|
| `ses_ea521a708ffeS45aSnI6YTjuXj` | `build` (principal) | `3b56f64f…` |
| `ses_ea52a4609ffeD1NmmQuRz7rkKJ` | `build` (previa) | `3b56f64f…` |
| `ses_ea33ed689ffeDvGhoL4WMnG4rz` | `researcher` | `3b56f64f…` |
| `ses_ea33e9d4fffeJd2ddIYEjd33TF` | `governance-analyst` | `3b56f64f…` |
| `ses_ea33809f2ffeB5pJ76OfbVs5EX` | `product-analyst` | `3b56f64f…` |
| `ses_ea3346aaaffeIPqUIPlvuDSG3G` | `researcher` | `3b56f64f…` |
| `ses_ea30585a5ffePBOSjlbaUzhxeL` | `researcher` | `3b56f64f…` |
| `ses_ea3053dc5ffekMTEUAm5sxa5Z0` | `researcher` | `3b56f64f…` |

**Resultado verificado:** el proyecto `3b56f64fc953aaebd3ed659e3d44852891fe3a4a` (`canonical` = `C:\Users\Miguel\Projects\VOLTERRA`)
se creó; las 8 sesiones constan bajo ese `projectID`; `global` pasó de 41 a 33 sesiones; y el export de la sesión principal
sigue devolviendo **99 mensajes** — el contenido sobrevivió intacto al traslado.

**Detalle técnico:** el cuerpo JSON debe escaparse para la capa nativa de PowerShell 5.1
(`{\"directory\":\"…\"}`); sin ese escapado el servidor responde `400 InvalidRequestError — Expected a valid JSON body`.
El endpoint devuelve **204 No Content** y no imprime nada en caso de éxito.

### 11.2 E-2 · `opencode.json` de proyecto — EJECUTADA

**Archivo creado** (`Projects\VOLTERRA\opencode.json`, 94 B):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "volterra-coordinator"
}
```

**Verificación:**
- `opencode debug config` desde `Projects\VOLTERRA` lista el archivo como *document* de configuración del proyecto,
  con `default_agent: volterra-coordinator`.
- `opencode debug agents` desde el mismo directorio devuelve **18 agentes**: los 7 internos de OpenCode
  (`build`, `plan`, `general`, `explore`, `compaction`, `title`, `summary`) **más los 11 agentes VOLTERRA**.
- El binario de OpenCode define la clave como
  *"Default primary agent to use when no session agent is selected"* — el coordinador pasa a ser el agente por defecto
  cuando no se elige otro.

**Hallazgo adicional (verifica la tabla de §3.1):** la traducción v1→v2 del frontmatter **funciona** y queda confirmada
en runtime. `bash:` se traduce a la acción `shell` y `task:` a la acción `subagent`, conservando la matriz de
delegación del coordinador (`subagent: deny` + allow/ask por subagente). Los 6 subagentes con `edit: deny` y
`shell: deny` quedan efectivamente sin escritura.

### 11.3 E-5 · Registro de decisiones — EJECUTADA

**Archivo creado:** `decisions/decision-register.md` (33802 B).

- Los **9 campos mínimos** de `governance/governance-charter.md` están presentes en las **20 fichas**.
- Se importa el estado **literal** del corpus: **19 `Pendiente`** + **1 `Sin decidir`** (DEC-12). **Ninguna aprobada.**
- El mapeo al vocabulario de la carta (`borrador`/`propuesta`/…) queda explícitamente marcado como **propuesta pendiente
  de confirmación**, no como decisión tomada.
- Los campos que el corpus no documenta (responsable nominal, opciones, decisión, fecha de revisión) se dejan
  **vacíos y señalados**; no se rellenan por inferencia.
- Incluye un índice de bloqueo (`E-1`…`E-10`, `Q-01`…`Q-38`, DEC-12) y el ciclo de gobernanza con el estado actual
  de cada ficha: **todas en el paso 1 (*Proponer*)**.

**Observación estructural (no modificada):** `workspace/workspace-structure.md` propone `docs/decisions/` para el
futuro repositorio, pero el proyecto actual usa `decisions/` en la raíz (donde ya vive `stack-evaluation.md`).
El registro se creó en `decisions/` por coherencia con la estructura **real**; la divergencia queda anotada aquí
y no se ha corregido por decisión propia.

### 11.4 E-3 · Frontmatter nativo V2 en los 11 agentes — EJECUTADA

**Qué se hizo:** los 11 archivos de `.opencode/agents/` pasaron del formato V1 (`permission:` como mapa con claves `edit`/`bash`/`task`) al formato nativo de V2 (`permissions:` como lista ordenada de `{action, resource, effect}`).

Mapeo aplicado, uno a uno: `bash` → `shell`; `task` → `subagent`; `resource: "*"` entrecomillado (en YAML, `*` sin comillas es un alias y rompe el parseo). El coordinador conserva la matriz de delegación completa: `subagent * deny` más 10 reglas por agente en `allow`/`ask`.

**Verificación previa (antes de tocar ningún archivo original):** se crearon tres agentes de prueba (`zz-probe-v1`, `-v2`, `-v3`) dentro del proyecto y se compararon sus permisos efectivos con `opencode debug agents`. Resultado: **el formato V2 produce exactamente el mismo conjunto que el V1**, incluida la matriz de subagentes. Los tres archivos de prueba se borraron y se comprobó que solo quedaban los 11 originales.
- Nota operativa: `opencode debug agents` solo lista agentes en proyectos **ya registrados**; desde un directorio temporal devuelve 0 agentes, ni siquiera los 7 internos. Por eso la prueba se hizo dentro del proyecto.

**Verificación posterior:** `opencode debug agents` (18 agentes antes y 18 después) comparado agente por agente contra la instantánea previa: **11/11 idénticos** en `mode`, `description`, cuerpo (`system`) y **permisos efectivos** (7 entradas por subagente; 18 en el coordinador). Ningún agente nuevo ni desaparecido. Los 11 archivos siguen en UTF-8 sin BOM, finales LF y 0 caracteres de reemplazo.

**Respaldo:** los 11 originales V1 están en `C:\Users\Miguel\AppData\Local\Temp\opencode\agents-v1-backup\`. Está **fuera** del proyecto y es almacenamiento temporal: puede no sobrevivir a una limpieza del sistema.

### 11.5 E-6 · Marcar `fase1/` como superada — EJECUTADA

- Se antepuso un aviso a cada uno de los **6 documentos** de `docs/research/fase1/`: "SUPERADO — este no es el corpus vigente", con fecha y jurisdicción del corpus (20/10/2026, España/UE), enlace a `../fase1-colombia/` y advertencia explícita de no reutilizar sus requisitos, plazos ni base jurídica.
- Se creó `docs/research/fase1/README.md` (2544 B): estado, motivo de la superación, qué se conserva y qué no, inventario de los 7 archivos y enlace al registro de auditorías del corpus vigente.
- **No se alteró el contenido original:** el único cambio en los 6 documentos es el bloque de aviso, **+462 B idénticos** en cada uno (de 5551→6013, 38193→38655, 23313→23775, 26460→26922, 10988→11450 y 15942→16404 B).
- El ZIP `00-plan-investigacion.zip` **sigue sin abrirse ni verificarse**; el README lo declara explícitamente en lugar de dar por bueno su contenido.

### 11.6 E-7 · Dictámenes de auditoría y cierre de hallazgos — EJECUTADA

- Se añadió **§7 «Auditorías del corpus y estado de cierre de cada hallazgo»** a `docs/research/fase1-colombia/05-bitacora-fuentes.md` (documento transversal A5), que pasa de 122 a 206 líneas y de 17490 a 27635 B.
- Contenido: dictamen literal de las dos auditorías del 21/10/2026 con sus recuentos (0/5/8/8 la primera; 0/3/7/4 la segunda), una tabla por auditoría con el **estado de cierre real de cada uno de sus 35 hallazgos** y un apartado §7.3 con lo que **sigue abierto** (incluidas las fuentes pendientes de verificación).
- **Colisión de identificadores resuelta:** las dos auditorías reutilizaron `M-01…`. Se conservan los identificadores originales con prefijo `AU1-`/`AU2-`, precisamente para no repetir la colisión que la propia auditoría 1 señaló como `A-01`.
- **Dos correcciones nunca se aplicaron y se registran como abiertas, no como cerradas:** `AU1-B-08`/`AU2-L-03` —C-01 y C-02 siguen en `http://`, verificado el 22/10— y el art. 3.1.1 del consolidado del Decreto 1074.
- También se actualizó el bloque «Cierre (formato AGENTS.md)» de esa bitácora para registrar la adición.

### 11.7 Lo que NO se hizo en esta ejecución

- No se seleccionó stack tecnológico. **DEC-12 sigue "sin decidir"**.
- No se resolvió ninguna `Q-xx` ni ningún `E-x`.
- No se aprobaron, rechazaron ni sustituyeron decisiones.
- No se fijó `model` por familia de agentes (**E-4** sigue pendiente; depende de DEC-13).
- No se archivaron ni borraron las 3 copias obsoletas (**E-8** pendiente).
- No se corrigieron las URLs `http://` de C-01/C-02: el hallazgo queda **registrado como abierto** en §7 de la bitácora, no cerrado.
- No se tocó la configuración global ni las conexiones (**E-10** pendiente).
- No se abrió el ZIP de `fase1/`.
- No se reescribió ningún hallazgo de auditoría: en E-7 los cierres se copiaron de lo que consta como aplicado, y lo que no se aplicó se declara como abierto.


## Cierre

**Siguiente paso:** el trabajo recuperado **ya es visible** en la interfaz, la gobernanza básica está documentada y los dos corpus de investigación están identificados sin ambigüedad. Las decisiones que quedan, por orden de valor: **E-4** (modelo por familia de agentes, bloqueada por DEC-13), **E-9** (operar siempre en `Projects\VOLTERRA`), **E-10** (higiene de configuración global) y **E-8** (archivar las 3 copias obsoletas). Requiere además tus respuestas a las **20 preguntas P1** y la consulta a asesoría jurídica colombiana para **E-1…E-10**.

---

*Informe generado el 2026-10-21 (inspección de solo lectura). Ejecución posterior el 2026-10-22: E-1, E-2 y E-5 (primer lote) y E-3, E-6 y E-7 (segundo lote), con aprobación explícita del usuario y registradas en §11. Ningún secreto expuesto. Ninguna decisión tomada por inferencia. Ningún stack seleccionado.*
