# Diagnóstico de solo lectura — VOLTERRA (23/10/2026)

**Modo:** solo lectura. No se creó, modificó, renombró ni borró ningún archivo durante la inspección.
**Alcance:** estructura, documentos de investigación, configuración de agentes y estado actual.
**Exclusiones:** no se abrieron los ZIP, no se probaron conexiones MCP/proveedores, no se instalaron dependencias y no se imprimieron secretos.
**Inventario:** 44 archivos y 16 carpetas, ≈481 KB, excluyendo `.opencode/node_modules` (antes de crear este documento; 45 archivos con él).

---

## 1. Estructura de carpetas

```text
VOLTERRA/
├── AGENTS.md
├── README.md
├── opencode.json
├── .opencode/
│   ├── agents/                 # 11 agentes .md
│   ├── package.json            # @opencode-ai/plugin 1.19.3
│   ├── package-lock.json
│   ├── .gitignore
│   └── node_modules/
├── decisions/                  # 2 documentos
├── docs/
│   ├── architecture/           # vacío
│   ├── decisions/              # vacío
│   ├── product/                # vacío
│   ├── recovery/               # 3 archivos (más este diagnóstico)
│   └── research/
│       ├── fase1/              # 8 archivos (España/UE, superado)
│       └── fase1-colombia/     # 6 archivos (vigente)
├── governance/                 # 3 documentos
├── integrations/               # 1 documento
├── product/                    # 1 documento
└── workspace/                  # 3 documentos
```

**Ausencias confirmadas:**

- No hay `.git/`: **no es un repositorio**.
- No hay `.gitignore` en la raíz.
- No hay código de aplicación, tests, CI, migraciones ni despliegue.
- No existen `docs/security/`, `docs/testing/` ni `docs/operations/`.
- `docs/architecture/`, `docs/decisions/` y `docs/product/` existen pero están vacías.
- No hay `apps/`, `packages/` ni `tests/`.

---

## 2. Documentos de investigación existentes

### 2.1 Corpus vigente: `docs/research/fase1-colombia/`

| Archivo | Tamaño | Estado declarado |
|---|---:|---|
| `00-plan-investigacion.md` | 4.730 B | Propuesta — no aprobada |
| `01-problemas-clubes-entrenadores.md` | 10.238 B | Propuesta — no aprobada |
| `02-mvp-vs-futuro.md` | 8.047 B | Propuesta — no aprobada |
| `03-requisitos-arq-seguridad-privacidad-permisos-trazabilidad.md` | 16.053 B | Propuesta — no aprobada |
| `04-preguntas-antes-elegir-tecnologias.md` | 6.914 B | Propuesta — no aprobada |
| `05-bitacora-fuentes.md` | 27.635 B | Propuesta — no aprobada |

**Contenido verificado por identificadores:**

- 12 problemas.
- 24 funcionalidades `F1`–`F24`.
- 13 requisitos `P-01`–`P-13`.
- 11 riesgos `R-01`–`R-11`.
- 38 preguntas `Q-01`–`Q-38` (P1=20, P2=14, P3=4).
- 10 fuentes jurídicas `C-01`–`C-10`.
- 22 fuentes deportivas `D-01`–`D-22`.
- 11 vacíos de gobernanza `GC-01`–`GC-11`.
- 10 vacíos legales `E-1`–`E-10`.
- 20 decisiones `DEC-01`–`DEC-20`.

La bitácora `05` incluye una §7 nueva con el dictamen de dos auditorías y el cierre de 35 hallazgos. Quedan abiertos, entre otros: `C-01`/`C-02` en `http://`, el art. 3.1.1 del consolidado del Decreto 1074, la guía SIC sobre NNA, reglamentos FVCV, D. 090/2018 y D-10.

**Observación:** este corpus no tiene `README.md` ni índice propio. El único índice existente es el de `fase1/`, que apunta a este directorio.

### 2.2 Corpus superado: `docs/research/fase1/`

Contiene 6 documentos, un `README.md` y un ZIP:

- `00-plan-investigacion.md` (6.013 B)
- `01-problemas-clubes-entrenadores.md` (38.655 B)
- `02-mvp-vs-futuro.md` (23.775 B)
- `03-requisitos...md` (26.922 B)
- `04-preguntas...md` (11.450 B)
- `05-bitacora-fuentes.md` (16.404 B)
- `README.md` (2.544 B)
- `00-plan-investigacion.zip` (45.934 B)

Los 6 documentos llevan el aviso **SUPERADO** y remiten a `fase1-colombia/`. El README indica que el ZIP **no se abrió ni verificó**.

### 2.3 Recuperación

- `docs/recovery/estado-recuperacion.md` (50.206 B): informe de recuperación y ejecución posterior.
- `docs/recovery/informe-recuperacion-2026-10-21.md` (69.905 B): anexo técnico, línea de tiempo y evidencia.
- `docs/recovery/estado-recuperacion.zip` (40.668 B, creado el 23/10 a las 07:57): **contenido no verificado**.

### 2.4 Otros documentos

- `decisions/decision-register.md` (33.802 B): 20 fichas `DEC-01`…`DEC-20`; **0 aprobadas**, 19 pendientes, 1 sin decidir.
- `decisions/stack-evaluation.md` (2.272 B): matriz de 11 criterios; **sin puntuar y sin pesos confirmados**.
- `governance/governance-charter.md` (2.664 B), `governance-operating-model.md` (2.736 B) y `research-evidence-standard.md` (1.441 B): los tres en estado de **propuesta**.
- `product/volterra-scope.md` (1.388 B): base de discusión, no especificación aprobada.
- `integrations/notebooklm-opencode-assessment.md` (4.477 B): evaluación preliminar; **no hay integración implementada**.
- `workspace/agent-workflow.md`, `workspace/security-and-permissions.md` y `workspace/workspace-structure.md`: flujo y políticas propuestas.

---

## 3. Configuración de agentes

### 3.1 Archivos

- `AGENTS.md`: 10 reglas vinculantes y formato de cierre.
- `opencode.json`: solo `$schema` y `default_agent: "volterra-coordinator"`.
- `.opencode/agents/`: 11 agentes.
- `.opencode/package.json`: dependencia `@opencode-ai/plugin@1.19.3`.
- `workspace/security-and-permissions.md` y `workspace/agent-workflow.md`: políticas operativas.

### 3.2 Permisos declarados en el frontmatter V2

| Agente | Modo | `edit` | `shell` |
|---|---|---|---|
| `volterra-coordinator` | primary | ask | ask |
| `researcher` | subagent | deny | deny |
| `product-analyst` | subagent | deny | deny |
| `architect` | subagent | deny | deny |
| `data-architect` | subagent | deny | deny |
| `governance-analyst` | subagent | deny | deny |
| `security-auditor` | subagent | deny | ask |
| `qa-engineer` | subagent | deny | ask |
| `backend-developer` | subagent | ask | ask |
| `frontend-developer` | subagent | ask | ask |
| `technical-writer` | subagent | ask | deny |

El coordinador además declara `subagent * deny` con reglas específicas `allow`/`ask` para los 10 subagentes.

**Verificado:** `opencode debug config` resuelve `default_agent: volterra-coordinator`; `opencode agent list` reconoce los 11 agentes.

### 3.3 Hallazgo importante sobre permisos

La CLI consultada **no traduce** el bloque V2 `permissions` a la lista efectiva `permission`:

- `opencode debug agent researcher` muestra las reglas `edit: deny` y `shell: deny` dentro de `options.permissions`.
- Sin embargo, la lista efectiva `permission` contiene solo los permisos globales por defecto (`*: allow`, reglas de lectura, etc.).
- Lo mismo ocurre con `volterra-coordinator`: sus reglas de `subagent` aparecen en `options.permissions`, pero no en `permission`.

**Conclusión provisional:** no se puede confirmar que los límites de solo lectura declarados se apliquen en el runtime de esta CLI. No se afirma que los agentes puedan escribir; se afirma que la evidencia disponible **no demuestra que estén restringidos**.

---

## 4. Estado actual del proyecto

### Hechos confirmados

- Proyecto en fase de **documentación y preparación**, sin código de producto.
- **Sin repositorio Git**, sin historial de versiones.
- **Sin stack aprobado**: `DEC-12` sigue “sin decidir”.
- **20 decisiones registradas, 0 aprobadas**: 19 pendientes + 1 sin decidir.
- **38 preguntas abiertas**, 20 de prioridad P1.
- **10 vacíos legales** `E-1`…`E-10`, relacionados con datos de menores y protección de datos.
- Corpus vigente: Colombia. Corpus anterior: España/UE, marcado como superado.
- Gobernanza, alcance y estándar de evidencia: **propuestas no aprobadas**.
- No hay validación con clubes ni entrenadores reales; no hay datos de mercado.
- No hay tests, CI ni entorno de ejecución.

### Recuperación

Según `docs/recovery/estado-recuperacion.md`, se ejecutaron 6 propuestas: `E-1`, `E-2`, `E-3`, `E-5`, `E-6` y `E-7`.

Verificado en disco:

- `E-2`: `opencode.json` existe y resuelve `default_agent`.
- `E-3`: los 11 agentes usan frontmatter V2.
- `E-5`: existe el registro de decisiones.
- `E-6`: los 6 documentos de `fase1/` llevan aviso de superado y existe su README.
- `E-7`: la §7 de auditorías está en `05-bitacora-fuentes.md`.

No verificado de forma independiente:

- `E-1`: la reubicación de las 8 sesiones requiere consultar la base/API de OpenCode; no se hizo en esta pasada.

Pendientes según el informe:

- `E-4`: fijar `model` por familia de agentes.
- `E-8`: archivar las 3 copias obsoletas.
- `E-10`: higiene de configuración global.
- `E-9`: recomendación operativa, no cambio pendiente.

---

## 5. Discrepancias y datos no verificados

1. **Versión de OpenCode inconsistente.**
   - `opencode --version` responde **1.19.3**.
   - El paquete global instalado es **`@opencode/cli@2.1.4`**.
   - El binario tiene `FileVersion 1.3.14`.
   - El informe de recuperación afirma que se instaló **v2.1.2**.
   - El paquete se instaló el 23/10 a las 07:42, pero el binario tiene fecha 19/10. **No se pudo determinar la causa ni qué versión gobierna realmente las sesiones.**

2. **Permisos efectivos no reproducibles.**
   - El informe §11.2/§11.4 afirma que `opencode debug agents` confirmó 18 agentes y permisos efectivos idénticos.
   - En la CLI actual no existe `debug agents`; existe `debug agent <nombre>`.
   - El resultado actual muestra las reglas V2 solo en `options.permissions`, no en `permission`. **La afirmación del informe no se reproduce con esta instalación.**

3. **Contenido de los ZIP.**
   - `docs/research/fase1/00-plan-investigacion.zip`.
   - `docs/recovery/estado-recuperacion.zip`.
   - Ambos permanecen **sin abrir y sin verificar**.

4. **Sesiones recuperadas.**
   - No se verificó en `opencode.db` ni en la API que las 8 sesiones estén realmente bajo el proyecto de `Projects\VOLTERRA`.

5. **Conexiones.**
   - La configuración global resuelta incluye servidores MCP (entre ellos `canva`, `adobe-express` y `github`); no se probó ninguna conexión.
   - No hay MCP definido a nivel de proyecto.

6. **Fuentes jurídicas.**
   - No se verificó la exactitud ni vigencia de las normas citadas; el propio corpus declara lecturas parciales y vacíos (art. 3.1.1, FVCV, guía SIC, D. 090/2018, D-10).
   - No hay asesoría jurídica colombiana contratada.

7. **Copias obsoletas.**
   - El informe menciona 3 copias del proyecto fuera de la ruta actual; no se inspeccionaron.

8. **Historial.**
   - Sin `.git`, no hay historial verificable de cambios.

9. **Aplicación del `default_agent` a esta sesión.**
   - La configuración lo resuelve, pero no se puede demostrar que esta sesión concreta se haya iniciado con ese agente.

10. **Codificación.**
    - Los `.md` y `.json` son UTF-8 válidos y no contienen caracteres de reemplazo. La consola de PowerShell muestra algunos caracteres mal interpretados; **no es corrupción de archivos**.

---

## 6. Riesgos principales

| Riesgo | Nivel | Comentario |
|---|---|---|
| Permisos de agentes no confirmados | Alto | La CLI muestra las reglas V2 como opciones, no como permisos efectivos. |
| Deriva de versión/configuración de OpenCode | Alto | 1.19.3 / 2.1.4 / 2.1.2 / 1.3.14 no coinciden. |
| Sin control de versiones | Alto | Todo el trabajo depende del disco y de la transcripción de sesiones. |
| Vacíos legales sobre datos de menores | Crítico | `E-1`…`E-10` sin cerrar; sin asesoría jurídica. |
| Investigación no aprobada usada como base | Alto | Todos los documentos son propuestas. |
| Dos corpus con estados distintos | Medio | `fase1/` está marcado como superado, pero el corpus vigente no tiene índice propio. |
| ZIP sin verificar | Medio | Podrían contener versiones antiguas o información no revisada. |
| Sin validación con clubes | Medio | No hay entrevistas ni datos de mercado. |
| Estructura documental incompleta | Bajo/Medio | Directorios vacíos y divergencia `decisions/` vs. `docs/decisions/`. |
| Dependencia huérfana y configuración global | Bajo/Medio | `E-10` pendiente; `.opencode/package.json` está ignorado por `.opencode/.gitignore`. |

---

## 7. Decisiones

### Confirmadas según los documentos (no revalidadas con el usuario en esta sesión)

- Mercado inicial: **Colombia**.
- Se gestionarán datos de atletas menores desde el MVP.
- El stack tecnológico **sigue sin decidirse**.
- La gobernanza es transversal.
- La investigación cubre atletas de todas las edades, con protección reforzada de menores.

### Provisional / no aprobado

- Los 6 documentos de `fase1-colombia/` son propuestas.
- La carta de gobernanza, el modelo operativo y el estándar de evidencia son propuestas.
- El alcance del producto es una base de discusión.
- El registro de decisiones documenta, pero no aprueba.

### Pendientes

- `DEC-01`…`DEC-20`: 19 pendientes y `DEC-12` sin decidir.
- Preguntas P1: 20 de 38.
- Vacíos legales `E-1`…`E-10`.
- `E-4`, `E-8`, `E-10`.
- Decidir si se crea el repositorio Git.
- Confirmar los pesos de la matriz de stack antes de puntuarla.
- Definir proveedor/modelo de OpenCode y su impacto en privacidad.

---

## 8. Pruebas y resultados reales

| Comprobación | Resultado |
|---|---|
| Inventario de archivos | 44 archivos, 16 carpetas, ≈481 KB sin `node_modules` (45 con este documento) |
| Presencia de `.git` | `False` |
| Archivos de código de app | Ninguno; solo `.opencode/package.json` |
| Agentes reconocidos | 11 agentes VOLTERRA |
| `default_agent` | Resuelto como `volterra-coordinator` |
| Codificación UTF-8 | 0 archivos con `U+FFFD` |
| Permisos V2 | Presentes en `options.permissions`; **ausentes** de la lista efectiva `permission` |
| ZIP | No abiertos |
| Tests/CI | No existen |
| Modificaciones realizadas | Ninguna |

---

## 9. Siguiente paso recomendado

**No aprobar ni construir todavía.** Antes de avanzar:

1. **Aclarar la versión real de OpenCode y validar los permisos** en el runtime que realmente ejecuta las sesiones. Es un requisito de seguridad, no una decisión de stack.
2. **Revisar con el usuario** si se acepta el estado documental actual y si se autoriza crear el repositorio Git.
3. **Decidir** `E-4`, `E-8` y `E-10` antes de tocar configuración global o copias.
4. **Responder las preguntas P1** y cerrar o declarar abiertos los `E-1`…`E-10` con asesoría jurídica colombiana.
5. **No seleccionar stack** hasta confirmar pesos, alcance y requisitos legales.

---

**Archivos modificados durante el diagnóstico:** ninguno.
**Este documento:** creado el 23/10/2026 a partir del diagnóstico entregado en la sesión, con autorización expresa del usuario.
