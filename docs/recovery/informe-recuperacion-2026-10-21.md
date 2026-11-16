# Informe de recuperación del entorno de trabajo — VOLTERRA

| | |
|---|---|
| **Fecha del informe** | 2026-10-21 (hora local `SA Pacific Standard Time`, UTC−05:00) |
| **Directorio canónico auditado** | `C:\Users\Miguel\Projects\VOLTERRA` |
| **Encargo** | `C:\Users\Miguel\Documents\nuevoproyecto.txt` — fases 1 a 6 |
| **OpenCode instalado** | `v2.1.2` |
| **OpenCode usado en la sesión perdida** | `v1.19.3` |
| **Modo de ejecución** | Inspección de solo lectura. Único archivo creado: este informe. |
| **Secreto expuesto en este informe** | Ninguno. Claves, tokens y contraseñas no se imprimieron ni se transcribieron. |

---

## 0. Cómo leer este informe

Todo lo que sigue está etiquetado. Las etiquetas no son decorativas: separan lo que está **probado** de lo que **se propone** o **se supone**.

| Etiqueta | Significado |
|---|---|
| **[V]** | **Verificado** en disco o en la base de datos de OpenCode durante esta auditoría. Con evidencia. |
| **[R]** | **Recuperado**: el contenido existía y se reconstruyó literalmente desde la sesión perdida. No es una propuesta. |
| **[P]** | **Propuesta** o recomendación de este informe. **No está aprobada y no se aplicó.** |
| **[H]** | **Hipótesis** razonada, sin confirmación directa. Se señala como tal. |
| **[A]** | **Pendiente de aprobación humana.** No se resolvió por inferencia. |

> Regla aplicada de forma estricta: **ningún elemento de este informe se ha marcado como "aprobado" por inferencia.** El proyecto no tiene stack aprobado, ni técnica seleccionada, ni decisiones registradas en un registro con aprobador.

---

## 1. Estado real del proyecto

### 1.1 Hallazgo principal

**La sesión anterior de OpenCode no se perdió: sigue almacenada y fue recuperada íntegramente.**

OpenCode guarda el historial en `C:\Users\Miguel\.local\share\opencode\opencode.db` (SQLite, 196 MB). La sesión que el usuario percibió como "desaparecida" es:

| Campo | Valor |
|---|---|
| ID de sesión | `ses_ea521a708ffeS45aSnI6YTjuXj` |
| Título | "Leer archivo .txt Nuevo Proyecto en Documentos" |
| Directorio de trabajo | `C:\Users\Miguel\Projects\VOLTERRA` |
| Agente de sesión | `build` (se cambió manualmente entre `plan` y `volterra-coordinator`) |
| Ventana temporal | 20/10/2026 14:51 → 21/10/2026 08:35 (local) |
| Mensajes recuperados | 97 (exportados con `/api/experimental/session/{id}/export`) |
| Subagentes lanzados | 6, con `parentID` = esa sesión |

El contenido de la sección 6 y del Anexo A de este informe se construye sobre esa transcripción literal. No es una reconstrucción de memoria ni una interpretación: es el texto que el modelo réellement escribió en la sesión perdida.

**[V]** Se conserva una copia de trabajo de la transcripción completa en:
`C:\Users\Miguel\AppData\Local\Temp\opencode\volterra_transcript.md` (68 KB, 97 mensajes).

### 1.2 Situación de partida verificada

| Elemento | Estado | Evidencia |
|---|---|---|
| Directorio canónico | **Existe** | `C:\Users\Miguel\Projects\VOLTERRA`, 38 archivos (sin `node_modules`) |
| Reglas de proyecto (`AGENTS.md`) | **Existe** | 721 B, 12 líneas de reglas vinculantes |
| Definiciones de agentes | **Existen (11)** | `.opencode/agents/*.md` |
| Corpus de investigación | **Existe** | `docs/research/fase1/` (6 .md + 1 .zip) y `docs/research/fase1-colombia/` (6 .md) |
| Gobernanza | **Existe** | `governance/` con 3 documentos |
| Registro de decisiones | **Ausente** | No hay registro de decisiones con ID/estado/aprobador |
| Configuración de proyecto (`opencode.json`) | **Ausente** | No existe en la raíz ni en `.opencode/` |
| `docs/recovery/` | **Ausente antes de este informe** | Creado por esta auditoría |
| Control de versiones (`.git`) | **Ausente** | No hay historial de cambios por versiones |
| Repositorio de código | **No existe** | Consistente con `README.md`: "no es un repositorio" |
| Stack tecnológico | **No aprobado** | `decisions/stack-evaluation.md`: "Estado: pendiente" |
| Despliegue / producción | **Nunca ocurrió** | Sin logs, sin configs de despliegue, sin costos generados |

### 1.3 Las cuatro copias de VOLTERRA

Se localizaron cuatro copias del material base. La comparación por hash MD5 confirma que **todos los archivos compartidos son byte-idénticos** entre las cuatro, y que `Projects\VOLTERRA` es un **superconjunto estricto**.

| Copia | Contenido compartido | Exclusivo | Veredicto |
|---|---|---|---|
| `C:\Users\Miguel\Projects\VOLTERRA` | AGENTS.md, README.md, 11 agentes, governance, workspace, decisions, product, integrations | `docs/research/**` (13 archivos) + `governance/governance-operating-model.md` | **CANÓNICA** |
| `C:\Users\Miguel\Documents\VOLTERRA_OpenCode_Architecture_Starter` | idem | — | Copia anterior (19/10 23:42) |
| `C:\Users\Miguel\Downloads\VOLTERRA_OpenCode_Architecture_Starter` | idem | — | Copia anterior |
| `C:\Users\Miguel\Downloads\VOLTERRA_OpenCode_Architecture_Starter_v2_Gobernanza\VOLTERRA_OpenCode_Architecture_Starter` | idem (sin `governance-operating-model.md`) | — | La más antigua; junto a ella hay un `.zip` de 10.740 B |

**[V]** Las tres copias no canónicas **no contienen `docs/research/`**: el trabajo de investigación de FASE 1 solo sobrevive en `Projects\VOLTERRA` y en la base de datos de OpenCode. Si esa carpeta se hubiera perdido, el trabajo de investigación se habría perdido con ella.

**[P]** Las tres copias obsoletas son un riesgo de confusionismo operativo (cualquiera de las cuatro parece "el proyecto"). **No se eliminó ninguna** — la misión prohíbe borrados. Se recomienda archivarlas manualmente cuando el usuario lo decida.

### 1.4 Producto: qué está realmente definido

**[V]** Extracto verificado de `product/volterra-scope.md` ("Estado: base de discusión, no especificación aprobada"):

- Plataforma para administrar clubes de **voleibol de playa**.
- Cada dato se registra una vez y se reutiliza; el historial de una dupla no se reescribe al cambiar sus integrantes.
- Ranking competitivo separado de indicadores de desarrollo.
- Los permisos se aplican **en servidor y datos**, no solo ocultando botones.
- La IA asiste al entrenador; no sustituye su criterio.
- ML, deep learning y visión por computador **quedan fuera del MVP** (decisión ya tomada en el documento de alcance).
- Roles candidatos: administrador de plataforma, administrador de club, entrenador, atleta. **Permisos concretos pendientes.**
- Mercado inicial: **Colombia** (ver §6, ronda 4).

**[V]** Conteo verificado del corpus vigente `docs/research/fase1-colombia/`:

| Elemento | Rango | Cantidad |
|---|---|---|
| Problemas detectados | — | 12 |
| Funcionalidades | `F1`–`F24` | 24 |
| Requisitos | `P-01`–`P-13` | 13 |
| Riesgos | `R-01`–`R-11` | 11 |
| Preguntas abiertas | `Q-01`–`Q-38` | 38 (P1=20, P2=14, P3=4) |
| Decisiones | `DEC-01`–`DEC-20` | 20 (19 pendientes + `DEC-12` "sin decidir") |
| Vacíos de evidencia legal | `E-1`–`E-10` | 10 |
| Fuentes de derecho colombiano | `C-01`–`C-10` | 10 |
| Fuentes deportivas/deportivas | `D-xx` | 22 |
| Vacíos de gobernanza | `GC-01`–`GC-11` | 11 |

**Nada de esto está aprobado.** **[V]** El propio corpus lo declara: 19 decisiones en estado pendiente y `DEC-12` explícitamente "sin decidir".

### 1.5 Causa raíz verificada de la desaparición de la sesión

**[V]** La sesión **no se perdió ni se borró: fue archivada fuera de vista.** El cambio de modelo de proyectos entre V1 y V2 lo explica por completo.

OpenCode **v1.19.3** archivaba todas las sesiones bajo un único proyecto `global` con ruta canónica `/`. OpenCode **v2.1.2** crea un proyecto **por directorio**. `GET /api/project` devuelve hoy exactamente **dos** proyectos:

| `projectID` | Ruta canónica | Creado | Activo por última vez |
|---|---|---|---|
| `global` | `/` | 11/09/2026 | 20/10/2026 14:29 |
| `e3613a6e536038d915182451a82eb9e53a5ca88c` | `C:\Users\Miguel` | **21/10/2026 20:33** | 21/10/2026 23:29 |

**[V]** Las **44 sesiones heredadas** —incluidas **las 8 de VOLTERRA** (la principal `ses_ea521a708ffeS45aSnI6YTjuXj`, sus 6 subagentes y la sesión previa de las 14:41)— siguen con `projectID = "global"`. **No existe ningún proyecto asociado a `C:\Users\Miguel\Projects\VOLTERRA`.**

Consecuencia directa y verificable: al abrir OpenCode dentro de la carpeta del proyecto, la interfaz lista las sesiones del proyecto asociado a ese directorio y **no encuentra ninguna**, porque las 8 están archivadas bajo `/`. Para el usuario, la sesión "desapareció". **Los datos siguen íntegros en `opencode.db`.**

**[V]** El proyecto `e3613a6e…` (ruta `C:\Users\Miguel`) se creó a las **20:33 del 21/10**, después de instalar OpenCode v2.1.2 (19:44) y de la migración de base de datos. Antes de ese momento, todo colgaba de `global`. El vídeo coincide: la sesión perdida se ejecutó el 20–21/10 bajo `projectID = "global"`; la sesión actual es la **primera** que cuelga de un proyecto por directorio.

**[P] Solución disponible y verificada en la API.** Existe `POST /api/session/{sessionID}/move` — *"Move a session to another project directory"*, con cuerpo obligatorio `{ "directory": "<ruta absoluta>" }` y `delivery` opcional. Reubicar las 8 sesiones de VOLTERRA en `C:\Users\Miguel\Projects\VOLTERRA` debería volver a asociarlas al proyecto de ese directorio y, con ello, a la vista en la interfaz.

> **No se ejecutó.** Es una mutación de datos y el encargo exige aprobación humana previa. Queda registrada como paso **0.0** en §8. Su efecto sobre la visibilidad es la consecuencia esperable según el esquema del endpoint, **no un hecho verificado**: la única forma de confirmarlo es ejecutarla.

**[V]** Contexto adicional del entorno, sin relación con la pérdida:

- La **app de escritorio de OpenCode** (Electron, `OpenCode.exe`, 231 MB) está instalada en `C:\Users\Miguel\AppData\Local\Programs\@opencode-aidesktop\`. Su último uso fue el **23/09/2026**, y sus archivos de workspace (`opencode.workspace.*.dat`) solo registran `-` (raíz) y `C--Users-Mig` (`C:\Users\Mig`) — **nunca** `Projects\VOLTERRA`. Es decir: la app de escritorio no se ha usado desde antes de la sesión de investigación.
- Existen **dos** lanzadores npm, `opencode` y `opencode2`, ambos con fecha 21/10 19:44 y ambos reportando **v2.1.2**. `opencode2` es un alias residual de la instalación de V2, **no** una segunda versión en paralelo. **[V]** No hayconflictos de versión activos.

---

## 2. Archivos encontrados y ausentes

### 2.1 Inventario completo (38 archivos, `node_modules` excluido)

Raíz `C:\Users\Miguel\Projects\VOLTERRA`:

```
AGENTS.md                                                  721 B
README.md                                                 1252 B
.opencode/.gitignore                                        63 B
.opencode/package.json                                       64 B
.opencode/package-lock.json                              14628 B
.opencode/agents/volterra-coordinator.md                   962 B
.opencode/agents/researcher.md                             373 B
.opencode/agents/product-analyst.md                        353 B
.opencode/agents/architect.md                              373 B
.opencode/agents/data-architect.md                         389 B
.opencode/agents/security-auditor.md                      359 B
.opencode/agents/governance-analyst.md                   1080 B
.opencode/agents/qa-engineer.md                            372 B
.opencode/agents/backend-developer.md                      347 B
.opencode/agents/frontend-developer.md                     383 B
.opencode/agents/technical-writer.md                       372 B
decisions/stack-evaluation.md                             2272 B
governance/governance-charter.md                          2664 B
governance/governance-operating-model.md                  2736 B
governance/research-evidence-standard.md                  1441 B
integrations/notebooklm-opencode-assessment.md            4477 B
product/volterra-scope.md                                 1388 B
workspace/agent-workflow.md                                722 B
workspace/security-and-permissions.md                      795 B
workspace/workspace-structure.md                          1099 B
docs/research/fase1/00-plan-investigacion.md              5551 B
docs/research/fase1/01-problemas-clubes-entrenadores.md  38193 B
docs/research/fase1/02-mvp-vs-futuro.md                  23313 B
docs/research/fase1/03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md  26460 B
docs/research/fase1/04-preguntas-antes-elegir-tecnologias.md  10988 B
docs/research/fase1/05-bitacora-fuentes.md               15942 B
docs/research/fase1/00-plan-investigacion.zip             45934 B
docs/research/fase1-colombia/00-plan-investigacion.md     4730 B
docs/research/fase1-colombia/01-problemas-clubes-entrenadores.md  10238 B
docs/research/fase1-colombia/02-mvp-vs-futuro.md           8047 B
docs/research/fase1-colombia/03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md  16053 B
docs/research/fase1-colombia/04-preguntas-antes-elegir-tecnologias.md  6914 B
docs/research/fase1-colombia/05-bitacora-fuentes.md      17490 B
```

### 2.2 Ausentes — y qué significa cada ausencia

| Ausente | Interpretación verificada |
|---|---|
| `opencode.json` / `opencode.jsonc` de proyecto | **[V]** Nunca existió en esta copia. No hay `model`, `default_agent`, `permissions`, `instructions` ni `plugins` fijados a nivel de proyecto. Consecuencia directa: el agente coordinador **no es el agente por defecto**. |
| `.git/` | **[V]** No hay control de versiones. El historial de cambios solo existe de forma reconstructible a partir de la transcripción de sesión y de las marcas de tiempo del log. |
| Registro de decisiones | **[V]** `governance/governance-charter.md` **exige** un registro con ID, estado y aprobador, y define los estados `borrador / propuesta / aprobada / rechazada`. Ese registro **no existe**. `decisions/` solo contiene la matriz de stack, que se declara "pendiente, no aprobado". |
| `docs/architecture/`, `docs/security/`, `docs/testing/`, `docs/operations/` | **[V]** No existen. Son **propuesta** de `workspace/workspace-structure.md`, no estructura construida. |
| Registro ADR | **[V]** No existe. `DEC-01…DEC-20` y `E-1…E-10` viven dispersos entre los documentos de investigación, sin aprobador ni fecha de aprobación. |
| Código fuente, migraciones, CI, tests | **[V]** No existen. El proyecto es, en esta fecha, **documentación y preparación**. |
| `.opencode/plugins/` | **[V]** No existe, pese a que `.opencode/package.json` declara la dependencia `@opencode-ai/plugin@1.19.3`. La dependencia está instalada pero **sin uso**. `.opencode/.gitignore` excluye `node_modules`, `package.json`, `package-lock.json` y `.gitignore` — es decir, esa dependencia fue deliberadamente dejada fuera del control de versiones. |

### 2.3 Hallazgo de integridad: un artefacto sin autor conocido

**[V]** `docs/research/fase1/00-plan-investigacion.zip` (45.934 B, mtime 21/10/2026 01:15:43) **no fue creado por la sesión recuperada**. El transcript de esa sesión no contiene ninguna escritura de ese archivo, y el log de OpenCode no registra ningún evento de escritura sobre esa ruta. **No se abrió ni se descomprimió.**

**[H]** Hipótesis plausible (no confirmada): la carpeta `fase1/` fue comprimida como entrega o respaldo alrededor de las 01:15, antes del cambio de jurisdicción a Colombia (01:38). Esto es consistente con la secuencia temporal, pero **no hay evidencia directa**.

**Riesgo:** si ese ZIP contiene una versión del plan anterior a las correcciones, y se hubiera sobrescrito `fase1/00-plan-investigacion.md`, el ZIP sería la única copia de esa variante. **Es una razón más para no borrar ni reorganizar `docs/research/fase1/` hasta que el usuario revise su contenido.**

### 2.4 Aclaración sobre una falsa alarma de marcas de tiempo

**[V]** Una revisión intermediaointerpretó que los archivos de `fase1/` habían sido modificados a las 12:21–12:29. **Es un artefacto de formato de 12/24 h en la tabla de PowerShell.** Los mtimes exactos son:

```
2026-10-21 00:21:21  fase1/00-plan-investigacion.md
2026-10-21 00:24:04  fase1/01-problemas-clubes-entrenadores.md
2026-10-21 00:25:37  fase1/02-mvp-vs-futuro.md
2026-10-21 00:27:28  fase1/03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md
2026-10-21 00:28:23  fase1/04-preguntas-antes-elegir-tecnologias.md
2026-10-21 00:29:40  fase1/05-bitacora-fuentes.md
```

Coinciden exactamente con las entradas del log de OpenCode (`2026-10-21T05:21:21Z` … `T05:29:40Z`, UTC). **No hay ninguna modificación fuera de las sesiones recuperadas.** Solo el ZIP (§2.3) queda sin explicar.

---

## 3. Agentes e instrucciones recuperados

### 3.1 Definiciones originales: recuperadas, no propuestas

**[R]** La fase 3 del encargo pedía "buscar las definiciones originales de los agentes y recuperarlas si existen; si faltan, proponerlas". **Existen todas.** No procede ninguna propuesta de arquitectura de agentes: proponer una aquí sería inventar sobre material sano, y además violaría la regla del proyecto de no tratar una propuesta como aprobada.

**Resultado: 11 definiciones recuperadas, byte-idénticas en las cuatro copias** (verificado por MD5).

### 3.2 Permisos exactos por agente (frontmatter literal en disco)

| Agente | `mode` | `edit` | `bash` | Rol funcional |
|---|---|---|---|---|
| `volterra-coordinator` | **primary** | ask | ask | Coordina tareas y pide aprobación antes de decisiones importantes |
| `researcher` | subagent | **deny** | **deny** | Investiga fuentes oficiales y alternativas sin modificar archivos |
| `product-analyst` | subagent | **deny** | **deny** | Convierte necesidades en flujos, reglas y criterios de aceptación |
| `architect` | subagent | **deny** | **deny** | Compara arquitecturas y sus consecuencias sin modificar archivos |
| `data-architect` | subagent | **deny** | **deny** | Diseña modelo conceptual de datos e historial |
| `security-auditor` | subagent | **deny** | ask | Audita permisos, seguridad y exposición de datos sin modificar archivos |
| `governance-analyst` | subagent | **deny** | **deny** | Analiza gobernanza del proyecto, datos, IA, seguridad y trazabilidad |
| `qa-engineer` | subagent | **deny** | ask | Define y ejecuta pruebas e informa defectos |
| `backend-developer` | subagent | ask | ask | Implementa tareas backend aprobadas con pruebas |
| `frontend-developer` | subagent | ask | ask | Implementa interfaz aprobada, accesible y adaptable |
| `technical-writer` | subagent | ask | **deny** | Redacta documentación técnica y registra decisiones |

### 3.3 Cobertura de los roles solicitados por la misión

**[V]** Los 9 roles tipo del encargo están cubiertos 1:1 por los 11 agentes existentes:

| Rol solicitado | Agente(s) que lo cubren |
|---|---|
| Coordinador principal | `volterra-coordinator` (`mode: primary`) |
| Investigador de mercado y fuentes | `researcher` |
| Analista funcional y de producto | `product-analyst` |
| Arquitecto de software | `architect` |
| Seguridad, privacidad y gobernanza | `security-auditor` + `governance-analyst` |
| Desarrollo | `backend-developer` + `frontend-developer` |
| Pruebas y QC | `qa-engineer` |
| Datos e integraciones | `data-architect` |
| Documentación y auditoría de cambios | `technical-writer` |

**Cobertura completa. Sin huecos que requerir propuesta.**

### 3.4 Permisos de delegación del coordinador (relevante para seguridad)

**[V]** El coordinador declara en su frontmatter:

```yaml
permission:
  edit: ask
  bash: ask
  task:
    "*": deny
    "researcher": allow
    "product-analyst": allow
    "architect": allow
    "data-architect": allow
    "qa-engineer": allow
    "security-auditor": allow
    "governance-analyst": allow
    "backend-developer": ask
    "frontend-developer": ask
    "technical-writer": ask
```

Traducción: **la regla por defecto es denegar**; 7 agentes de solo lectura se lanzan sin fricción; los 3 agentes que escriben requieren un "¿puedo?" explícito en cada invocación. Este diseño coincide con `workspace/security-and-permissions.md`.

**[V]** **Los permisos se aplicaron de verdad en la sesión perdida.** Los 6 subagentes lanzados fueron `researcher` (×4), `product-analyst` (×1) y `governance-analyst` (×1) — los tres con `edit: deny` y `bash: deny`. En la ronda 2 (§6.2) esos agentes produjeron 12 problemas, 39 fuentes, 24 funcionalidades, 30+ requisitos, 34 preguntas y 11 vacíos de evidencia **sin escribir un solo archivo**. El log de OpenCode registra las evaluaciones de permiso correspondientes.

### 3.5 Instrucciones de proyecto recuperadas

**[R]** `AGENTS.md` (721 B) — reproduced verbatim:

```
# Instrucciones del proyecto VOLTERRA
- No asumir que una propuesta está aprobada.
- Diferenciar hechos, hipótesis, recomendaciones y decisiones confirmadas.
- Consultar decisiones antes de seleccionar tecnologías.
- Priorizar soluciones simples, seguras, mantenibles y comprobables.
- Mantener historia de atletas, resultados y duplas; evitar duplicar fuentes de verdad.
- Aplicar permisos en servidor y datos.
- No desplegar, hacer push, borrar datos ni generar costos sin aprobación humana.
- No leer ni revelar secretos; nunca imprimir variables de entorno.
- Informar pruebas ejecutadas realmente.

Al terminar: resumen, archivos modificados, pruebas/resultados, riesgos, decisiones pendientes y siguiente paso.
```

**[R]** `README.md` (1.252 B) — estado declarado: *"borrador; no es un repositorio ni una selección de tecnologías definitiva"*. Declara como decisiones pendientes: frontend, backend, base de datos/auth, hosting, pruebas/CI, observabilidad/backups, **proveedor/modelo para OpenCode** y herramientas de organización. Fija 6 pasos de uso que empiezan por revisar `decisions/stack-evaluation.md` y terminan (paso 6) en "crear el repositorio solo después de aprobar las decisiones mínimas".

**[R]** `workspace/agent-workflow.md` — ciclo obligatorio por tarea:
**investigar → diseñar → aprobar → implementar → verificar → entregar.** Cada tarea debe declarar objetivo, incluye/no incluye, archivos permitidos, dependencias, criterios de aceptación, pruebas, riesgos y si requiere aprobación humana.

**[R]** `workspace/security-and-permissions.md` — investigación, arquitectura, producto, QA de revisión y auditoría: **solo lectura por defecto**. Escrituras, shell, instalación, red, `git push` y despliegue: **pedir aprobación**. Producción, credenciales y datos reales: **no accesibles por defecto**. Prohibido copiar tokens, claves API o contraseñas a prompts o logs. Usar datos ficticios en desarrollo.

**[R]** `governance/governance-charter.md` — define los estados de decisión (`borrador`, `propuesta`, `aprobada`, `rechazada`) y exige un **registro de decisiones con ID, estado y aprobador**. Define que la gobernanza es transversal a producto, datos, arquitectura, agentes y operación.

**[R]** `governance/governance-operating-model.md` — matriz de roles y responsabilidades + estados de decisión. **Este archivo solo existe en la copia canónica** (se añadió después de las otras tres; es una de las razones por las que `Projects\VOLTERRA` es la canónica).

**[R]** `governance/research-evidence-standard.md` — estándar de evidencia para la investigación.

### 3.6 Brechas detectadas en las instrucciones (constatadas, no corregidas)

**[V]** Brecha 1 — **El coordinador no es el agente por defecto.** No hay `default_agent` en ningún `opencode.json`. El campo `agent` de la sesión perdida era `build`, y el transcript muestra al usuario cambiando manualmente entre `plan` y `volterra-coordinator` a lo largo de la sesión. En la práctica, la gobernanza del coordinador era **opcional**: dependía de que el usuario se acordara de cambiar de agente. **Este es el punto de fricción más importante del sistema y no tiene arreglo automático.**

**[V]** Brecha 2 — **El frontmatter es de OpenCode V1** (`permission:` como mapa, `task:`). La máquina pasó de `v1.19.3` a `v2.1.2` después de la sesión perdida. **[V]** La guía oficial de migración de V2 documenta que las definiciones de agente en `.opencode/` **siguen funcionando sin cambios**, y que V2 traduce automáticamente el frontmatter heredado (`bash` → `shell`, `task` → `subagent`). Además, la propia sesión perdida demuestra que los agentes se cargaron y funcionaron. **No hay breakage conocido.** Aun así, la forma V1 explícita es más frágil frente a futuras versiones.

**[V]** Brecha 3 — **Ningún agente fija `model`.** Todos heredan el modelo de la sesión (en la sesión perdida: `opencode/big-pickle`). No es un error, pero significa que **el "equipo" multiagente no usa modelos distintos por especialidad** y que su comportamiento depende del modelo que el usuario tenga seleccionado en ese momento.

**[V]** Brecha 4 — **Los 4 agentes con `edit: ask` + `bash: ask` no tienen `model` ni guía de pruebas.** El `backend-developer` declara "Implementa solo tareas aprobadas" pero no exige un formato de salida de pruebas, mientras `AGENTS.md` sí exige "Informar pruebas ejecutadas realmente".

---

## 4. Configuraciones que requieren revisión

### 4.1 Configuración global de OpenCode

Ruta: `C:\Users\Miguel\.config\opencode\opencode.jsonc`

**[V]** Contenido verificado (claves MCP solamente):

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "canva":       { "type": "remote", "url": "https://mcp.canva.com/mcp" },
    "adobe-express":{ "type": "local", "command": ["npx","-y","@adobe/express-developer-mcp@latest"] }
  }
}
```

**[V]** Observaciones:

- No hay `model`, `default_agent`, `permissions`, `agents`, `instructions`, `plugins`, `provider` ni `formatter` definidos globalmente.
- **No existe** `~/.config/opencode/agents/`, `agent/`, `command/`, `skill/` ni `plugin/`. Es decir: **no hay agentes globales**; los 11 de VOLTERRA son exclusivamente de proyecto.
- **[V]** El directorio heredado `C:\Users\Miguel\.opencode` **no existe en absoluto**. No hay configuración global de agentes ni de plugins en ninguna de las dos rutas posibles.
- **[V]** La app de escritorio de OpenCode (Electron) está instalada pero **sin uso desde el 23/09/2026**, y sus workspaces registrados no incluyen el proyecto VOLTERRA (ver §1.5).
- `opencode.backup.jsonc` (5/10/2026) es una versión anterior con solo `canva`.
- `cli.json` (21/10 19:46) contiene **preferencias de terminal** (`diffs.wrap: word`, `session.sidebar: auto`, `session.scrollbar: false`, `session.thinking: hide`, `animations: true`). No afecta al comportamiento de los agentes.
- `service.json` contiene la **contraseña del servicio local de OpenCode**. **[V] Su valor no fue leído ni impreso en esta auditoría.**
- `~/.local/share/opencode/auth.json` contiene una entrada `google` de tipo `api` con clave. **[V] El valor no fue leído ni impreso.**

### 4.2 Estado de proveedores y herramientas — verificado vs. solo mencionado

Este es el punto donde la fase 5 exige más rigor: **no afirmar que algo está conectado solo porque aparece mencionada en un documento.**

| Elemento | Estado real | Cómo se verificó |
|---|---|---|
| **Gemini (proveedor `google`)** | **Conectado de verdad** | `models` reporta `google/gemini-4-argon`, `gemini-3.8-flash`, `gemini-flash-lite-latest`, `gemini-3-pro-image`, `gemma-4-31b-it`, `lyria-3-pro-preview` como `active`; `auth.json` tiene entrada `google` tipo `api`; una sesión pasada (`ses_f5dd2eb90ffeYhJMbJ3LMaBiEc`, proyecto Barena) corrió efectivamente con `google/gemini-3.8-flash`. |
| **OpenCode Zen (proveedor `opencode`)** | **Conectado** | 9 modelos `active` de costo 0, incluido `opencode/big-pickle` (el modelo de esta sesión). |
| **NotebookLM** | **NO existe integración** | Nada en `opencode.jsonc`, ni en `auth.json`, ni en `mcp-auth.json` lo referencia. Solo se menciona en `integrations/notebooklm-opencode-assessment.md`. |
| **MCP `adobe-express`** | **Conectado** | `opencode mcp list` → `✓ adobe-express connected`. |
| **MCP `canva`** | **NO conectado — requiere autenticación** | `opencode mcp list` → `⚠ canva needs authentication`. Existe una entrada `canva` en `mcp-auth.json` sin sesión activa. |
| **MCP en el proyecto VOLTERRA** | **Ninguno** | No hay `mcp` en ninguna configuración del proyecto. Los MCP son globales. |

**[V]** La afirmación de `integrations/notebooklm-opencode-assessment.md` — *"OpenCode está conectado a Gemini mediante una clave de API"* — **queda verificada como cierta** a fecha de hoy. La conclusión del mismo documento (que **no** existe API pública para cuadernos personales de NotebookLM, solo NotebookLM Enterprise, y que un MCP es solo una vía técnica, no una API) **sigue vigente y no se contradice** con lo verificado: Gemini sí está conectado; NotebookLM no tiene ninguna integración.

**[V]** Ningún proveedor, modelo o clave fue modificado durante esta auditoría.

### 4.3 Configuraciones que requieren revisión humana

| # | Configuración | Problema | Riesgo | Acción propuesta |
|---|---|---|---|---|
| C-1 | `default_agent` ausente | El coordinador no es el agente por defecto; en la sesión perdida el agente activo era `build` | **Alto** — la gobernanza depende de un gesto manual | Crear `opencode.json` de proyecto con `default_agent: volterra-coordinator` **[P][A]** |
| C-2 | Frontmatter V1 en los 11 agentes | Depende de la capa de compatibilidad de V2 | **Bajo** hoy, **medio** a futuro | Migrar a `permissions:` como lista ordenada `{action, resource, effect}` **[P][A]** |
| C-3 | Sin `model` por agente | Comportamiento variable según la sesión | **Medio** — cobertura y coste impredecibles | Fijar modelo por familia de agente tras elegir proveedor **[P][A]** |
| C-4 | `canva` MCP sin autenticar | Herramienta declarada pero inutilizable | **Bajo** — no es necesaria para VOLTERRA | Autenticar o retirar del config global **[P][A]** |
| C-5 | `@opencode-ai/plugin@1.19.3` declarado y sin usar | Dependencia huérfana en `.opencode/package.json` | **Bajo** | Eliminar del `package.json` o empezar a usar plugins **[P][A]** |
| C-6 | `decisions/stack-evaluation.md` con pesos "iniciales" sin confirmar | El propio documento pide confirmar los pesos antes de comparar | **Medio** — comparaciones construidas sobre supuestos no validados | Confirmar pesos con el usuario antes de puntuar **[P][A]** |
| C-7 | Tres copias obsoletas del proyecto | Riesgo de editar la copia equivocada | **Medio** | Archivar/eliminar las tres, conservando la canónica **[P][A]** |
| C-8 | `docs/research/fase1/` (versión España/UE) sin marcar como superada | Dos corpus vigentes a la vez; riesgo de citar la fuente equivocada | **Medio** | Marcar `fase1/` como histórico/superseded en su cabecera **[P][A]** |

### 4.4 Configuración no encontrada (relevante para lo que se perdió)

**[V]** No existe ninguna configuración de:

- Proveedor/modelo por defecto del proyecto.
- Permisos de herramientas a nivel de proyecto.
- Instrucciones (`instructions`) propias del proyecto.
- Formateador, linter o plugins.
- Servidor MCP de proyecto.
- Cualquier CI/CD, observabilidad o backups.

**[H]** Hipótesis: el material base se distribuía como "starter kit" (`VOLTERRA_OpenCode_Architecture_Starter`) con la configuración deliberadamente **vacía** para forzar la decisión explícita de proveedor y stack. Esto es coherente con `README.md` ("No se incluye proveedor/modelo en la configuración: debe decidirse según opciones disponibles, calidad, privacidad y costo") y con el `.gitignore` que excluye `package.json`. **No hay confirmación directa.**

---

## 5. Arquitectura multiagente

### 5.1 Arquitectura reconstruida (recuperada, no diseñada)

**[R]** Esta arquitectura **existía y funcionó**. No es una propuesta de este informe.

```
                    ┌──────────────────────────────────────┐
                    │        volterra-coordinator          │
                    │        mode: primary                 │
                    │        edit: ask   bash: ask         │
                    └───────────────┬──────────────────────┘
                                    │ task: "*" → deny
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
   ┌────▼─────────────────────┐ ┌───▼──────────────────┐ ┌──────▼──────────────────────┐
   │  SOLO LECTURA (allow)    │ │  SOLO LECTURA        │ │  ESCRITURA (ask)           │
   ├──────────────────────────┤ ├──────────────────────┤ ├────────────────────────────┤
   │ researcher         ✎✎ deny │ │ security-auditor ✎ deny │ │ backend-developer   ✎ ask ✎ ask │
   │ product-analyst    ✎✎ deny │ │ qa-engineer     ✎ deny │ │ frontend-developer  ✎ ask ✎ ask │
   │ architect          ✎✎ deny │ │ governance-analyst ✎✎ deny │ │ technical-writer   ✎ ask ✎ deny │
   │ data-architect     ✎✎ deny │ │                    │ │                            │
   └──────────────────────────┘ └──────────────────────┘ └────────────────────────────┘
        ✎ = edit    ✎✎ = bash
```

**[V]** Modelo de permisos en tres niveles, coherente con `workspace/security-and-permissions.md`:

| Nivel | Agentes | `edit` | `bash` | Regla |
|---|---|---|---|---|
| **I — Solo lectura total** | researcher, product-analyst, architect, data-architect, governance-analyst | deny | deny | No pueden tocar el disco ni ejecutar nada. Investigar y diseñar. |
| **II — Lectura + ejecución controlada** | security-auditor, qa-engineer | deny | ask | No escriben; pueden ejecutar comandos **preguntando**. Auditar y probar. |
| **III — Escritura controlada** | backend-developer, frontend-developer, technical-writer | ask | ask | Escriben y ejecutan **preguntando cada vez**. Implementar y documentar. |

**[V]** El coordinador queda por encima con `edit: ask` / `bash: ask`, y la delegación por defecto es `deny`: cada subagente hay que habilitarlo explícitamente. Esto es una defensa en profundidad razonable para un proyecto con datos personales de atletas menores de edad.

### 5.2 Ejecutividad demostrada

**[V]** Los 6 subagentes que corrieron, con su ventana temporal y su resultado:

| # | Sesión | Agente | Ventana (local) | Resultado |
|---|---|---|---|---|
| 1 | `ses_ea33ed689ffeDvGhoL4WMnG4rz` | `researcher` | 20/10 23:38–23:45 | Problemas de voleibol playa: 12 problemas |
| 2 | `ses_ea33e9d4fffeJd2ddIYEjd33TF` | `governance-analyst` | 20/10 23:39–23:43 | Requisitos de gobernanza: 11 vacíos GC-01…GC-11 |
| 3 | `ses_ea33809f2ffeB5pJ76OfbVs5EX` | `product-analyst` | 20/10 23:46–23:49 | Delimitación MVP: 24 funcionalidades F1…F24 |
| 4 | `ses_ea3346aaaffeIPqUIPlvuDSG3G` | `researcher` | 20/10 23:50–23:57 | Preguntas y bitácora: 34 preguntas + fuentes |
| 5 | `ses_ea3053dc5ffekMTEUAm5sxa5Z0` | `researcher` | 21/10 00:41–00:47 | Contexto deportivo Colombia: 22 fuentes D-xx |
| 6 | `ses_ea30585a5ffePBOSjlbaUzhxeL` | `researcher` | 21/10 00:41–00:55 | Fuentes jurídicas Colombia: 10 fuentes C-01…C-10 |

**[V]** Las 6 corrieron con `parentID = ses_ea521a708ffeS45aSnI6YTjuXj`. **Ninguna escribió un archivo.** La primera ronda fue íntegramente de lectura, y el permission engine evaluó cada invocación de `bash` (entradas `evaluated permission=bash` en el log) — los agentes con `bash: deny` quedaron bloqueados sin que seorsionara el trabajo.

**[V]** En las rondas 2 y 3 (auditorías) se usaron subagentes adicionales con el mismo patrón de solo lectura, lo que confirma que la restricción no fue decorativa sino efectiva.

### 5.3 Cobertura de la arquitectura: qué falta y qué sobra

**[V]** La arquitectura cubre **todos los roles de investigación, diseño, auditoría, construcción y documentación** que el encargo enumera. **[V]** No hay sobre-dotación: no existen agentes redundantes.

**[P]** Dos capacidades **no** están cubiertas por ningún agente, y sí son necesarias para la fase siguiente:

| Capacidad no cubierta | Por qué importa | Agente candidato |
|---|---|---|
| **Ingesta / normalización de datos** | El corpus define 24 funcionalidades, 13 requisitos y un modelo de datos con historial de duplas; nadie está "&aacute;responsible" de llevar datos externos (canchas, torneos, pruebas) al modelo | `data-architect` (ampliar) o agente nuevo de ingesta |
| **Operaciones / despliegue / observabilidad** | `README.md` y `workspace/workspace-structure.md` contemplan `docs/operations/`, y el encargo Fase 6 pide un plan de operación; ningún agente cubre backups, rollback ni despliegue | `backend-developer` (ampliar) o agente nuevo de operaciones |

**Estas dos filas son recomendaciones, no decisiones. No se creó ningún agente.**

---

## 6. Flujo de trabajo reconstruido

**[R]** Este es el método que **realmente se ejecutó**, recuperado del transcript. Se documenta porque es un activo operativo: cualquiera que retome VOLTERRA debe saber que este ciclo ya funcionó una vez, completa, con dos auditorías y dos rondas de corrección.

### 6.1 Ciclo canónico declarado (norma)

**[R]** De `workspace/agent-workflow.md`:

```
investigar → diseñar → aprobar → implementar → verificar → entregar
```

Cada tarea declara: objetivo · incluye/no incluye · archivos permitidos · dependencias · criterios de aceptación · pruebas · riesgos · si requiere aprobación humana.

### 6.2 Ejecución real de la sesión perdida — 9 rondas

**[R]** Reconstrucción literal, con marcas de tiempo locales y el papel de cada agente.

| # | Momento | Qué pasó | Agente(s) | Resultado en disco |
|---|---|---|---|---|
| **1** | 20/10 14:51–14:57 | Lectura de `nuevoproyecto.txt`, inventario del proyecto y **plan de FASE 1** con 3 puntos de aprobación (A1–A5) | `plan` | Ninguno |
| **2** | 20/10 14:5x | El usuario **aprobó** vía herramienta `question`: jurisdicción inicial **España/UE**, foco en **menores**, entregables en `docs/research/fase1/` | — | — |
| **3** | 20/10 23:37–23:57 | **Ronda 1 — investigación paralela (solo lectura)**: A1 `researcher`, A3 `governance-analyst`, A2 `product-analyst`, A4+A5 `researcher` | 4 subagentes | 12 problemas, 39 fuentes, 24 funcionalidades, 30+ requisitos, 34 preguntas, 11 vacíos. **Sin archivos escritos.** |
| **4** | 21/10 00:20–00:29 | **Escritura del corpus España/UE** — 6 archivos en `docs/research/fase1/` | `volterra-coordinator` | `fase1/` (6 .md) |
| **5** | 21/10 00:38 | **Cambio de jurisdicción**: el usuario relee `nuevoproyecto.txt` y pide pasar a **Colombia**. Se presenta el plan y el usuario responde **"sí"** | — | — |
| **6** | 21/10 00:40–01:10 | **Ronda 2 — investigación Colombia en paralelo**: contexto deportivo + fuentes jurídicas | 2 subagentes `researcher` | `fase1-colombia/` (6 .md). **`fase1/` intacto** |
| **7** | 21/10 01:23 | **Auditoría ronda 1**: 5 altas (A-01…A-05), 8 medias (M-01…M-08), 8 bajas (B-01…B-08). Dictamen: **REQUIERE CORRECCIONES** | `volterra-coordinator` | — |
| **8** | 21/10 01:37–01:49 | El usuario da **permiso explícito y general** ("te doy permiso en todo lo que decidas") y se aplican todas las correcciones | `volterra-coordinator` | `05-bitacora-fuentes.md` reescrita + ediciones en los otros 5 |
| **9** | 21/10 08:21 | **Auditoría ronda 2** con un criterio nuevo: *"cubrir **todas** las edades, no solo menores"*. Resultado: 3 altas (H-01…H-03), 7 medias (M-01…M-07), 4 bajas (L-01…L-04). Dictamen: **REQUIERE CORRECCIONES** | `volterra-coordinator` | — |
| **10** | 21/10 08:25–08:35 | El usuario responde **"procigue"**. Se aplican las correcciones y **se verifican con búsquedas directed** sobre el texto resultante. M-07 se cierra leyendo **D. 1377** (URL 3 de C-03), que contiene el mapa oficial de compilación hacia D. 1074. Se deja declarada la salvedad sobre el "art. 3.1.1" (consolidado final no leído) | `volterra-coordinator` | 6 archivos corregidos (mtimes 08:27–08:35) |

**[V]** La ronda 10 confirma que las correcciones **quedaron persistidas**: se verificó en disco la presencia de `Q-37`, `Q-38`, `P-13`, `E-10` y `DEC-01`…`DEC-20`.

**[V]** La sesión perdida **terminó sin cerrar el trabajo**: quedó pendiente responder las 20 preguntas P1, obtener asesoría jurídica para los 10 vacíos E-1…E-10 y tomar 19 decisiones. El informe de auditoría final (08:21) y las correcciones (08:35) son el último estado.

### 6.3 Patrón de gobernanza que se revela (reconstruido)

**[R]** Tres comportamientos que se repetieron y que conviene preservar:

1. **Investigación siempre antes que escritura, y siempre en solo lectura.** Las rondas 1 y 2 produjeron cero escrituras. Los agentes de investigación no podían escribir por diseño.
2. **El plan se aprueba antes de ejecutar.** El agente `plan` presentó A1–A5 con 3 puntos de aprobación y el usuario los resolvió con la herramienta `question` antes de que se lanzara ningún subagente.
3. **Autocorrección por auditoría con dictamen formal.** El mismo rol produjo hallazgos (A/M/B y H/M/L), y el trabajo no se dio por bueno hasta que los hallazgos se corrigieron y se verificaron.

**[P]** Un cuarto patrón que conviene adoptar explícitamente: **registrar el dictamen de auditoría y el estado de cierre de cada hallazgo dentro del propio documento de investigación** (no solo en la conversación), para que el estado sobreviva a la sesión. La auditoría de las 08:21 y sus correcciones de las 08:25–08:35 **solo constan en la transcripción de sesión**: quien abra `docs/research/fase1-colombia/` hoy no ve que hubo dos auditorías ni cuáles quedaron cerradas.

---

## 7. Decisiones pendientes y riesgos

### 7.1 Decisiones que requieren aprobación humana

**Ninguna se resuelve por inferencia en este informe.**

| # | Decisión | Estado actual | Depende de |
|---|---|---|---|
| D-1 | **Modelo de datos y framework de persistencia** | Sin stack aprobado. Matriz de 11 criterios con pesos "iniciales" sin confirmar (`decisions/stack-evaluation.md`) | Respuesta a Q-01…Q-38 (20 P1) |
| D-2 | **Proveedor y modelo de OpenCode para el proyecto** | Sin definir a nivel de proyecto. Hoy hay `opencode` (gratuitos) y `google` (Gemini) disponibles y autenticados | Criterio de privacidad: datos de menores |
| D-3 | **`DEC-01`…`DEC-20`** | 19 en estado pendiente; `DEC-12` "sin decidir" | Asesoría jurídica (E-1…E-10) |
| D-4 | **Vacíos legales E-1…E-10** | Los 10 requieren lawyer; el propio corpus lo dice | Abogado en derecho deportivo colombiano |
| D-5 | **`default_agent` del proyecto** | No definido. El coordinador existe pero no es el agente por defecto | Decisión del usuario (C-1) |
| D-6 | **Forma del frontmatter de agentes** | V1 heredado, funcional por compatibilidad | Decisión del usuario (C-2) |
| D-7 | **Registro de decisiones con aprobador** | Exigido por `governance-charter.md`, inexistente | Decisión del usuario |
| D-8 | **Alcance por edades** | **`Q-37` fue la corrección de mayor peso de la auditoría ronda 2** y fijó "todas las edades". **Ya respondida por el usuario en la sesión perdida** | — |
| D-9 | **Pagos** | `product/volterra-scope.md` los lista "si se aprueban". No están en el MVP | Decisión del usuario |
| D-10 | **Creación del repositorio** | Pendiente. `README.md` paso 6: "solo después de aprobar las decisiones mínimas" | D-1, D-3, D-4 |

### 7.2 Riesgos

| # | Riesgo | Severidad | Evidencia | Mitigación propuesta |
|---|---|---|---|---|
| R-1 | **Que el proyecto se corte de nuevo y se pierda el trabajo de investigación** | **Alta** | `docs/research/` no existe en 3 de las 4 copias; no hay `.git` | **[P]** Crear repositorio + primera confirmación de versiones — **solo tras aprobar D-10** |
| R-2 | **Cumplimiento legal con datos de menores de edad** | **Alta** | E-1…E-10 abiertos; `Q-37` extiende el alcance a todas las edades | **[P]** No usar datos reales hasta cerrar E-1…E-10 con asesoría jurídica |
| R-3 | **Límite de confianza con OpenCode: el permission engine es la única barrera** | **Alta** | `AGENTS.md` prohíbe revelar secretos; `service.json` y `auth.json` guardan credenciales | **[P]** Regla operativa: ninguna credencial en prompts ni logs (ya está en `AGENTS.md`; solo falta aplicarla en la práctica) |
| R-4 | **La gobernanza depende de un gesto manual** (el agente por defecto era `build`) | **Media-Alta** | §3.6 Brecha 1; campo `agent` = `build` en la sesión | **[P]** Fijar `default_agent` (C-1) |
| R-5 | **Editando la copia equivocada** | Media | 4 copias byte-idénticas | **[P]** Archivar las 3 obsoletas (C-7) |
| R-6 | **Citar el corpus España/UE como si fuera el vigente** | Media | `fase1/` y `fase1-colombia/` conviven sin marca de estado | **[P]** Marcar `fase1/` como superseded (C-8) |
| R-7 | **El estado de auditoría no sobrevive a la sesión** | Media | Las 2 auditorías y sus cierres solo constan en el transcript | **[P]** Incorporar el dictamen al propio documento |
| R-8 | **Artefacto ZIP sin autor conocido** | Baja-Media | §2.3 | **[P]** Revisar su contenido antes de reorganizar `fase1/` |
| R-9 | **Modelo sin fijar por agente → cobertura y coste impredecibles** | Media | Brecha 3 | **[P]** Fijar modelo tras D-2 |
| R-10 | **Ruptura futura por frontmatter heredado V1** | Baja | Guía oficial: V2 mantiene compatibilidad; no hay breakage conocido | **[P]** Migrar a forma V2 nativa (C-2) |
| R-11 | **El trabajo de investigación sigue invisible en la interfaz** — el usuario no ve sus 8 sesiones recuperadas y puede concluir que se perdieron otra vez, y repetir el trabajo | **Media-Alta** | §1.5: las 8 sesiones siguen bajo `projectID = "global"`; no hay proyecto para `Projects\VOLTERRA` | **[P]** Ejecutar el paso **0.0** (§8): reubicar las 8 sesiones con `POST /api/session/{id}/move` |
| R-12 | **Cualquier trabajo nuevo que no se ejecute dentro de `Projects\VOLTERRA`** se archivará en `global` y volverá a quedar invisible | Media | Mismo mecanismo que R-11; el proyecto por directorio solo se crea al abrir OpenCode **en** la carpeta | **[P]** Abrir siempre OpenCode con cwd = `C:\Users\Miguel\Projects\VOLTERRA` (esto también habilita los 11 agentes) |

### 7.3 Lo que **no** se hizo (y por qué)

Registro explícito, conforme a `AGENTS.md` ("No desplegar, hacer push, borrar datos ni generar costos sin aprobación humana"):

- **No** se borró ni movió ningún archivo, incluida ninguna de las 3 copias obsoletas.
- **No** se sobrescribió ningún archivo existente. El único archivo creado es este informe.
- **No** se modificó ninguna configuración: ni `opencode.jsonc`, ni `auth.json`, ni `service.json`, ni los 11 agentes, ni `AGENTS.md`.
- **No** se cambió proveedor, modelo, clave ni conexión.
- **No** se instalaron dependencias ni se ejecutaron instalaciones.
- **No** se desplegó, no se hizo push, no se generaron costos.
- **No** se leyeron ni imprimieron valores de secretos.
- **No** se abrió el ZIP de §2.3 (se documentó como no abierto).
- **No** se escribió código de producto, ni migraciones, ni tests.
- **No** se resolvió ninguna de las 20 preguntas P1, ni ninguna de las 19 decisiones DEC.

---

## 8. Plan ordenado de recuperación

Ordenado por dependencia. Cada paso indica si es una **acción** o una **decisión**. Ningún paso de acción se ejecuta sin la aprobación que lo precede.

### Fase 0 — Preservación inmediata (riesgos R-1, R-11, R-12)

| # | Paso | Tipo | Depende de |
|---|---|---|---|
| **0.0** | **Reubicar las 8 sesiones de VOLTERRA** (la principal `ses_ea521a708ffeS45aSnI6YTjuXj`, la previa `ses_ea52a4609ffeD1NmmQuRz7rkKJ` y los 6 subagentes) en `C:\Users\Miguel\Projects\VOLTERRA` mediante `POST /api/session/{sessionID}/move` con `{ "directory": "C:\\Users\\Miguel\\Projects\\VOLTERRA" }`. **Muta datos: requiere aprobación expresa.** Efecto esperado: las sesiones vuelven a aparecer en la interfaz y quedan asociadas al proyecto del directorio (§1.5) | **Decisión (A)** → luego acción | — |
| 0.1 | Revisar el contenido de `docs/research/fase1/00-plan-investigacion.zip` (45.934 B) y registrar qué contiene | Acción | — |
| 0.2 | Verificar espacio disponible y decidir si `Projects\VOLTERRA` se respalda a una ubicación externa antes de cualquier reorganization | Acción | — |
| 0.3 | **Decidir** si se crea el repositorio git ahora o después de cerrar D-1/D-3/D-4 | **Decisión (A)** | — |

### Fase 1 — Consolidar la gobernanza (sin stack, sin código)

| # | Paso | Tipo | Depende de |
|---|---|---|---|
| 1.1 | **Decidir** `default_agent: volterra-coordinator` en un `opencode.json` de proyecto | **Decisión (A)** → luego acción | §5.1 |
| 1.2 | **Decidir** si se migra el frontmatter de los 11 agentes a `permissions:` nativo V2 | **Decisión (A)** → luego acción | §3.6 |
| 1.3 | **Decidir** si se fija `model` por familia de agente | **Decisión (A)** → luego acción | D-2 |
| 1.4 | Crear el **registro de decisiones** que exige `governance-charter.md` (ID, estado `borrador/propuesta/aprobada/rechazada`, aprobador, fecha) e **importar** los 20 `DEC-xx` con estado "pendiente" — **sin aprobar ninguno** | Acción | 1.1 |
| 1.5 | Crear el registro de los 10 vacíos `E-1…E-10` y de las 38 preguntas con su prioridad P1/P2/P3 | Acción | 1.4 |
| 1.6 | Marcar `docs/research/fase1/` como **versión superada (España/UE)** en su cabecera, y `fase1-colombia/` como **vigente** | Acción | 0.1 |
| 1.7 | Incorporar al documento de investigación el **dictamen de las 2 auditorías** y el estado de cierre de cada hallazgo (A/M/B, H/M/L) | Acción | — |
| 1.8 | Archivar las 3 copias obsoletas (tras confirmar que el ZIP de 0.1 no depende de ellas) | **Decisión (A)** → luego acción | 0.1, 0.3 |

### Fase 2 — Cerrar el bloque legal (R-2)

| # | Paso | Tipo | Depende de |
|---|---|---|---|
| 2.1 | **Decidir** si se contrata asesoría jurídica en derecho deportivo colombiano y con qué alcance | **Decisión (A)** | — |
| 2.2 | Responder las **20 preguntas P1** (bloqueantes para stack) y dejar constancia de quién respondió | Acción | 2.1 |
| 2.3 | Cerrar `E-1`…`E-10` con el abogado, o dejar constancia de que quedan abiertos | Acción | 2.1, 2.2 |
| 2.4 | **Decidir** el alcance de datos por edad (respuesta ya registrada a `Q-37`: todas las edades) y su reflejo en requisitos | Acción | — |
| 2.5 | Revisar `P-07`/`S-11` y `P-01`/`P-02`/`T-1`, que la auditoría marcó como `[H]` + `[A]` | Acción | 2.3 |

### Fase 3 — Decidir el stack (D-1, D-2)

| # | Paso | Tipo | Depende de |
|---|---|---|---|
| 3.1 | **Confirmar los 11 pesos** de `decisions/stack-evaluation.md` (el propio documento lo exige antes de comparar) | **Decisión (A)** | 2.2 |
| 3.2 | Puntuar cada alternativa con **evidencia adjunta**, marcando qué criterios son verificables hoy y cuáles dependen de un proveedor concreto | Acción | 3.1 |
| 3.3 | **Decidir** proveedor/modelo de OpenCode del proyecto (privacidad: datos de menores) | **Decisión (A)** | 3.2 |
| 3.4 | Emitir `DEC-01`…`DEC-20` con estado y aprobador en el registro de 1.4 | Acción | 3.2, 3.3 |

### Fase 4 — Construir (solo tras aprobar el stack)

| # | Paso | Tipo | Depende de |
|---|---|---|---|
| 4.1 | **Decidir** si se crea el repositorio (README paso 6) | **Decisión (A)** | Fase 3 completa |
| 4.2 | Crear el repo, versionar `docs/`, `governance/`, `decisions/`, `product/`, `workspace/`, `.opencode/agents/`, `AGENTS.md` | Acción | 4.1 |
| 4.3 | Definir el modelo de datos con `data-architect` (duplas con periodos de asociación, historial inmutable, aislamiento multi-club) | Acción | 4.1 |
| 4.4 | Definir arquitectura, permisos en servidor y estrategia de pruebas con `architect`, `security-auditor` y `qa-engineer` | Acción | 4.3 |
| 4.5 | Implementar el vertical slice con `backend-developer` / `frontend-developer` **solo con tareas aprobadas** | Acción | 4.4 |
| 4.6 | Documentar con `technical-writer` y actualizar el registro de decisiones | Acción | 4.5 |

### Fase 5 — Operación

| # | Paso | Tipo | Depende de |
|---|---|---|---|
| 5.1 | **Decidir** observabilidad, backups, rollback y entorno de hosting | **Decisión (A)** | 4.4 |
| 5.2 | **Decidir** si `canva` MCP se autentica o se retira del config global | **Decisión (A)** | — |
| 5.3 | **Decidir** si la dependencia `@opencode-ai/plugin` se elimina o se empieza a usar | **Decisión (A)** | — |
| 5.4 | Operar con datos ficticios; ningún dato real hasta cerrar la Fase 2 | Regla | 2.3 |

---

## Anexo A — Línea de tiempo de la sesión recuperada

### A.1 Sesiones envolvidas

| Sesión | ID | Padre | Agente | Ventana (local) | Mensajes |
|---|---|---|---|---|---|
| Principal | `ses_ea521a708ffeS45aSnI6YTjuXj` | — | `build` (cambia a `plan` y `volterra-coordinator`) | 20/10 14:51 → 21/10 08:35 | 97 |
| Previa | `ses_ea52a4609ffeD1NmmQuRz7rkKJ` | — | `build` | 20/10 14:41 → 14:44 | 10 |
| Sub 1 | `ses_ea33ed689ffeDvGhoL4WMnG4rz` | principal | `researcher` | 20/10 23:38 → 23:45 | — |
| Sub 2 | `ses_ea33e9d4fffeJd2ddIYEjd33TF` | principal | `governance-analyst` | 20/10 23:39 → 23:43 | — |
| Sub 3 | `ses_ea33809f2ffeB5pJ76OfbVs5EX` | principal | `product-analyst` | 20/10 23:46 → 23:49 | — |
| Sub 4 | `ses_ea3346aaaffeIPqUIPlvuDSG3G` | principal | `researcher` | 20/10 23:50 → 23:57 | — |
| Sub 5 | `ses_ea3053dc5ffekMTEUAm5sxa5Z0` | principal | `researcher` | 21/10 00:41 → 00:47 | — |
| Sub 6 | `ses_ea30585a5ffePBOSjlbaUzhxeL` | principal | `researcher` | 21/10 00:41 → 00:55 | — |

### A.2 Mensajes del usuario en la sesión principal (índice literal)

| # | Momento | Texto del usuario |
|---|---|---|
| 1 | 20/10 14:51 | "entra en documentos y lee el aarchivo .txt nuevo proyecto" |
| 2 | 20/10 ~14:5x | (aprobación vía herramienta `question`: España/UE + menores, entregables en `docs/research/fase1/`) |
| 3 | 21/10 00:38 | "lee otra ves el archivo .txt nuevoproyecto en documentos" *(→ cambio a Colombia)* |
| 4 | 21/10 00:3x | "si" *(aprobación del plan de Colombia)* |
| 5 | 21/10 01:37–01:49 | "apliquemos las correcciones, te doy permiso en todo lo que decidas" |
| 6 | 21/10 08:2x | "procigue" |
| 7 | 21/10 08:3x | "lee otra ves el archivo .txt nuevoproyecto en documentos" *(→ este encargo de recuperación)* |

### A.3 Momentos clave del proceso, con su efecto en disco

| Momento | Evento | Efecto en disco |
|---|---|---|
| 20/10 23:37–23:57 | Ronda 1 de investigación, 4 subagentes en solo lectura | **Ninguno** (12 problemas, 39 fuentes, 24 funcionalidades, 30+ requisitos, 34 preguntas, 11 vacíos Без escritura) |
| 21/10 00:21–00:29 | Escritura del corpus España/UE | `fase1/` — 6 .md (5.551–38.193 B) |
| 21/10 00:41–00:55 | Ronda 2 de investigación, 2 subagentes en paralelo | **Ninguno** |
| 21/10 ~01:10 | Escritura del corpus Colombia | `fase1-colombia/` — 6 .md |
| 21/10 01:23 | Auditoría ronda 1 → **REQUIERE CORRECCIONES** (5 altas, 8 medias, 8 bajas) | — |
| 21/10 01:37–01:49 | Correcciones con permiso general del usuario | `05` reescrita + ediciones en los otros 5 |
| 21/10 08:21 | Auditoría ronda 2 (criterio nuevo: todas las edades) → **REQUIERE CORRECCIONES** (3 altas, 7 medias, 4 bajas) | — |
| 21/10 08:25–08:35 | Correcciones + verificación con búsquedas; M-07 cerrado con D. 1377 | 6 archivos con mtime 08:27–08:35 |
| — | **Evento sin autor conocido** | `fase1/00-plan-investigacion.zip` (45.934 B, 01:15:43) |

### A.4 Elementos corregidos en la ronda final (08:25–08:35)

**[R]** Registro literal del cierre de la sesión:

- `05-bitacora-fuentes.md` — **reescrita**: identificadores `D-xx` → `DEC-xx` (colisión con A-01); URLs completas de C-03/C-05/C-07…C-10 y D-04/D-07/D-09/D-10/D-14/D-16; faltantes D-15/D-17/D-20/D-22 añadidos; **GC-02 corregido**; cierre con recuentos correctos.
- `00-plan-investigacion.md` — **DEC-12** (A-01); referencia E-1…E-10 rota arreglada (B-01).
- `01-problemas-clubes-entrenadores.md` — D. 1074 rebajado a `[H]` en 3 sitios (A-05); vacíos Q-28/Q-29 → Q-31/Q-32 y vinculados a GC-xx (A-03, B-07).
- `02-mvp-vs-futuro.md` — F7 condicionado a E-1 (M-06); plazos de 10/15 días deslindados (M-04); art. 12 → inferencia del art. 9 (B-05); A5c → Q-23, A6c → Q-34 (B-02, B-03); F11 corregido (B-04); tensión IA resuelta (M-08).
- `03-requisitos-…` — P-07/S-11 rebajados a `[H]`+`[A]` y añadida **E-10** (A-04); R-11 (verificación de identidad del tutor, M-05); clasificaciones `[J]`/`[H]` separadas en P-01/P-02/T-1 (A-05).
- `04-preguntas-…` — contadores 19/13/4 con Q-34 en P2 (M-01); "E-12" → P-12 (M-02); mapa Q → DEC corregido (M-…).

**[V]** El estado final en disco confirma la persistencia: `Q-37`, `Q-38`, `P-13`, `E-10` y `DEC-01`…`DEC-20` presentes; 38 preguntas (P1=20, P2=14, P3=4); 19 decisiones pendientes + `DEC-12` "sin decidir"; 10 fuentes de derecho `C-01`…`C-10`; 22 fuentes `D-xx`; 11 vacíos `GC-01`…`GC-11`.

### A.5 Salvedad declarada y no resuelta por la propia sesión

**[R]** La sesión cerrada en 08:35 dejó una salvedad explícita: el **"art. 3.1.1" no se pudo verificar** porque el **consolidado final** de la norma no fue leído. Se resolvió M-07 leyendo **D. 1377** (URL 3 de C-03), que contiene el **mapa oficial de compilación hacia D. 1074**. La salvedad quedó declarada, no resuelta. **[V]** Sigue abierta hoy.

---

## Anexo B — Evidencia, método y trazabilidad

### B.1 Fuentes consultadas

| Fuente | Ruta / endpoint | Uso |
|---|---|---|
| Encargo | `C:\Users\Miguel\Documents\nuevoproyecto.txt` (107 líneas, 6 fases) | Definición del encargo |
| Base de datos de OpenCode | `C:\Users\Miguel\.local\share\opencode\opencode.db` (196 MB) | Origen de las sesiones |
| Export de sesión | `GET /api/experimental/session/{id}/export` | Transcripción literal (97 + 10 mensajes) |
| Transcripción extraída | `C:\Users\Miguel\AppData\Local\Temp\opencode\volterra_transcript.md` (68 KB) | Fuente del Anexo A |
| Export de sesión previa | `C:\Users\Miguel\AppData\Local\Temp\opencode\prev_ses.json` | Sesión de las 14:41 |
| Log de OpenCode | `C:\Users\Miguel\.local\share\opencode\log\opencode.log` (5.994.305 B) | Cronología de escrituras (UTC), evaluaciones de permiso, versiones |
| Config global | `C:\Users\Miguel\.config\opencode\opencode.jsonc` | MCP declarados |
| Config global (respaldo) | `C:\Users\Miguel\.config\opencode\opencode.backup.jsonc` | Estado anterior (5/10) |
| Preferencias CLI | `C:\Users\Miguel\.config\opencode\cli.json` | Preferencias de terminal |
| Credenciales (solo claves, sin valores) | `~/.local/share/opencode/auth.json`, `mcp-auth.json` | Verificación de proveedor y MCP |
| **Índice de proyectos** | `GET /api/project` | Causa raíz de §1.5: solo 2 proyectos; ninguno para `Projects\VOLTERRA` |
| **Esquema OpenAPI** | `GET /openapi.json` (562.918 B) | Contrato de `POST /api/session/{id}/move` y parámetros de `/api/session` |
| **App de escritorio** | `C:\Users\Miguel\AppData\Local\Programs\@opencode-aidesktop\` + `AppData\Roaming\ai.opencode.desktop\` | Estado de uso y workspaces registrados (§1.5) |
| Documentación oficial V2 | `https://opencode.ai/v2/docs/agents`, `/v2/docs/migrate-v1` | Ruta `.opencode/agents/`, compatibilidad V1→V2 |

### B.2 Comandos ejecutados (todos de solo lectura)

```
opencode --version                                  → v2.1.2
opencode2 --version                                 → v2.1.2 (alias residual, misma versión)
opencode service status                             → http://127.0.0.1:45278
opencode mcp list                                   → adobe-express connected; canva needs authentication
opencode api get /api/project                       → 2 proyectos: "global" (/) y e3613a6e… (C:\Users\Miguel)
opencode api get /api/session --param "limit=…"     → 44 sesiones heredadas con projectID=global
opencode api get /api/session --param "directory=C:\Users\Miguel\Projects\VOLTERRA"
opencode api get /api/experimental/session/{id}/export
opencode api get /api/agent                         → solo builtins (cwd = C:\Users\Miguel)
Get-FileHash -Algorithm MD5                         → comparación de las 4 copias
Select-String / Get-ChildItem                       → inventario y conteos del corpus
Test-Path C:\Users\Miguel\.opencode                 → False (no hay dir home heredado)
python 3.11                                        → parseo de los exports JSON (decodificación UTF-16)
```

### B.3 Limitaciones de esta auditoría

1. **[V]** `opencode api get /api/agent` **ignora** el parámetro `directory` (el servidor resuelve al directorio de trabajo actual). Por eso **no se pudo probar por API** que los 11 agentes cargan desde `Projects\VOLTERRA`. **La prueba es indirecta pero sólida**: la sesión perdida se ejecutó en ese directorio y lanzó subagentes llamados `researcher`, `product-analyst` y `governance-analyst` — nombres que solo existen en `.opencode/agents/`.
2. **[V]** El mismo parámetro `directory` **también se ignora** en `GET /api/session`: la consulta con `directory=Projects\VOLTERRA` devolvió las 44 sesiones de todos los proyectos. El filtrado por proyecto se hizo leyendo el campo `projectID` de cada sesión.
3. **[V]** No se pudo leer el transcript *anterior a la creación* de la sesión: OpenCode no conserva versiones de los mensajes.
4. **[V]** Las versiones anteriores de `nuevoproyecto.txt` **no son recuperables**: el archivo se sobrescribió en cada iteración. Solo existe el texto actual.
5. **[V]** El contenido del ZIP de `fase1/` no se abrió.
6. **[H]** La causa del ZIP sin autor (§2.3) es una hipótesis, no un hecho.
7. **[V]** El log de OpenCode usa **UTC**; la hora local es `SA Pacific Standard Time` (UTC−05:00). Todos los tiempos de este informe están expresados en hora local, convertida desde UTC.
8. **[V]** El efecto de `POST /api/session/{id}/move` sobre la visibilidad en la interfaz **no se verificó**, porque ejecutarlo muta datos. El mecanismo de §1.5 (archivado bajo `projectID = global`) está verificado por datos; el efecto de la corrección está inferido del contrato del endpoint.

---

## Cierre

### Resumen

La sesión anterior de OpenCode **no se perdió**: estaba en `opencode.db` y se recuperó íntegra (97 mensajes, 6 subagentes, 9 rondas). Y se identificó **la causa raíz de que "desapareciera"**: al migrar de OpenCode v1.19.3 a v2.1.2, las sesiones dejaron de archivarse en un proyecto global y pasaron a archivarse en un proyecto **por directorio**. Las 8 sesiones de VOLTERRA siguen bajo `global`, y **no existe ningún proyecto asociado a `Projects\VOLTERRA`**, así que la interfaz no tiene nada que mostrar al abrir el proyecto. Los datos están íntegros (§1.5).

El entorno de trabajo de VOLTERRA se recuperó en su mayor parte: **las 11 definiciones de agentes originales existen y funcionaron**, las reglas de proyecto, el flujo multiagente, la gobernanza y el corpus de investigación están íntegros en disco. No hizo falta proponer arquitectura de agentes: había que recuperarla, y se recuperó.

Lo que falta no es contexto, sino **decisiones**: no hay stack aprobado, no hay registro de decisiones con aprobador, no hay `opencode.json` (y por tanto el coordinador no es el agente por defecto), no hay control de versiones, y siguen abiertos 19 decisiones, 38 preguntas (20 bloqueantes) y 10 vacíos legales.

### Archivos modificados

**Ninguno modificado.**

| Acción | Archivo |
|---|---|
| **Creado** | `C:\Users\Miguel\Projects\VOLTERRA\docs\recovery\informe-recuperacion-2026-10-21.md` (este informe) |
| **Creado (carpeta)** | `C:\Users\Miguel\Projects\VOLTERRA\docs\recovery\` |
| Modificado | — |
| Borrado | — |
| Desplegado | — |

Artefactos de trabajo fuera del proyecto (en `C:\Users\Miguel\AppData\Local\Temp\opencode\`): `volterra_transcript.md`, `volterra_export.json`, `prev_ses.json`, `ses_volt.txt`, `ses12.txt`, `openapi.json`, `extract.py`, `prev.py`, `sesv.py`, `sesv2.py`, `ses12.py`. Ninguno contiene secretos; los exports contienen el historial de sesión, que es material del propio proyecto.

### Pruebas y verificaciones realmente ejecutadas

Todas las siguientes se ejecutaron de verdad durante esta auditoría:

1. `opencode --version` → **v2.1.2** (y el log confirma **v1.19.3** en las sesiones del 20–21/10).
2. `opencode2 --version` → **v2.1.2** (alias residual de la misma instalación; no hay versiones en paralelo).
3. `opencode mcp list` → `✓ adobe-express connected`, `⚠ canva needs authentication`.
4. `opencode api get /api/session --param "directory=…"` → **47 sesiones** devueltas; 8 en `Projects/VOLTERRA` (1 actual, 1 principal perdida, 1 previa, 6 subagentes) — la pérdida de la que se trata.
5. `opencode api get /api/project` → **2 proyectos**: `global` (ruta `/`) y `e3613a6e…` (ruta `C:\Users\Miguel`, creado 21/10 20:33) → **base verificada de la causa raíz de §1.5**.
6. `opencode api get /api/session --param "limit=12"` → las **44 sesiones heredadas** con `projectID = "global"`, incluida la principal de VOLTERRA; solo la sesión actual pertenece a un proyecto por directorio.
7. `GET /openapi.json` → contrato de `POST /api/session/{sessionID}/move` (body `{directory}` obligatorio) y de los filtros `directory` / `project` de `GET /api/session`.
8. `opencode api get /api/experimental/session/{id}/export` → export completo de las 2 sesiones (3.308.404 B y 68.040 B).
9. Parseo de la transcripción con Python → **97 mensajes**, 6 subagentes con `parentID` correcto, 4 mensajes de usuario identificados literalmente.
10. `Get-FileHash -Algorithm MD5` sobre las 4 copias → **archivos compartidos byte-idénticos**; `Projects\VOLTERRA` = superconjunto estricto.
11. Conteo por `Select-String` sobre `fase1-colombia/` → DEC=20, E=10, R=11, P=13, F=24, Q=38, C=10, D=22, GC=11 (todos verificados, no copiados del transcript).
12. Mtimes exactos en ISO de los 12 `.md` de `docs/research/` → coherentes con el log (UTC ↔ local −5).
13. `Select-String` sobre `opencode.log` → confirmadas las escrituras de `fase1/` (05:21Z–05:29Z) y de `fase1-colombia/` (13:33Z–13:35Z), las evaluaciones de permiso y la ausencia de escrituras fuera de las sesiones.
14. Verificación de `auth.json` (solo claves) → proveedor `google` tipo `api` presente → **Gemini autenticado**.
15. `models` → 2 proveedores (`opencode` con 9 modelos, `google` con 6) todos `active`.
16. Lectura del frontmatter literal de los **11** agentes → tabla de permisos de §3.2.
17. Verificación en disco de `Q-37`, `Q-38`, `P-13`, `E-10`, `DEC-01` → **las correcciones de la sesión perdida quedaron persistidas**.
18. `Test-Path C:\Users\Miguel\.opencode` → **False**; inspección de `AppData\Local\Programs\@opencode-aidesktop` y `AppData\Roaming\ai.opencode.desktop` → app de escritorio instalada, último uso 23/09/2026, sin workspace VOLTERRA.

**No se ejecutó ninguna prueba de código**: no hay código en el proyecto.
**No se ejecutó ninguna mutación**: `POST /api/session/{id}/move` quedó documentado pero sin ejecutar (requiere aprobación).

### Riesgos

Los riesgos R-1 a R-12 están detallados en §7.2. Los tres de severidad alta: pérdida de datos por ausencia de control de versiones (R-1), cumplimiento legal con datos de menores (R-2) y dependencia de credenciales que solo separa el permission engine (R-3). Añadidos tras el hallazgo de §1.5: **R-11** (el trabajo sigue invisible en la interfaz) y **R-12** (cualquier sesión nueva abierta fuera de `Projects\VOLTERRA` volverá a quedar archivada en `global`).

### Decisiones pendientes

D-1 a D-10 en §7.1, más el paso **0.0** (§8) — reubicar las 8 sesiones recuperadas. Ninguna se resolvió por inferencia.

### Siguiente paso

**[A]** Dos decisiones Framing para desbloquear el resto:

1. **Paso 0.0** — autorizar la reubicación de las 8 sesiones en `C:\Users\Miguel\Projects\VOLTERRA`. Con esto el trabajo recuperado **vuelve a ser visible** en la interfaz, que es el objetivo declarado del encargo.
2. **Abrir siempre OpenCode con el directorio de trabajo en `C:\Users\Miguel\Projects\VOLTERRA`.** Eso activa los 11 agentes, crea el proyecto por directorio y evita que el trabajo nuevo vuelva a archivarse en `global` (R-12).

Después: D-5 (`default_agent`), D-10 (creación del repositorio) y Fase 2 (asesoría jurídica). Todo lo demás depende de esas tres.

Sin esas decisiones, la posición correcta es **no avanzar a la Fase 4**: con 19 decisiones abiertas, 20 preguntas P1 sin responder y 10 vacíos legales sin cerrar sobre datos de menores de edad, elegir stack o escribir código sería exactamente el error que `AGENTS.md` prohíbe.

---

*Informe generado el 2026-10-21. Auditoría de solo lectura. Ningún secreto quedó expuesto. Ninguna decisión fue tomada por inferencia.*
