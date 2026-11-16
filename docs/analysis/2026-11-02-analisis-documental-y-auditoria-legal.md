# VOLTERRA — Análisis documental y auditoría legal

**Fecha:** 02/11/2026
**Modo:** análisis de solo lectura sobre el repositorio y la documentación existente.
**Alcance:** documentos, decisiones, requisitos, riesgos, vacíos legales y evidencia de auditoría.
**Naturaleza:** **diagnóstico documental, no dictamen jurídico.** No sustituye la asesoría de un abogado colombiano.

---

## 0. Resumen ejecutivo

1. **La base documental es amplia y está bien clasificada**, pero sigue siendo mayoritariamente **propuesta no aprobada**. El corpus vigente es `docs/research/fase1-colombia/`; el corpus `fase1/` (España/UE) está marcado como superado y no debe usarse como requisito.
2. **Hay 20 decisiones `DEC`:** 4 aprobadas (DEC-01, DEC-02, DEC-03, DEC-08), 15 pendientes y 1 sin decidir (DEC-12). Además hay 5 decisiones `N-xx` aprobadas con asiento mínimo.
3. **Los 10 vacíos legales `E-1`…`E-10` siguen abiertos.** No consta asesoría jurídica colombiana contratada ni dictamen escrito. Esto bloquea el uso de datos reales, no solo el despliegue.
4. **Faltan los documentos legales operativos**: política de tratamiento, aviso de privacidad, manual interno (art. 17.k), autorizaciones, procedimiento ARCO-P, retención, transferencias internacionales, evaluación RNBD, incidentes y brechas, contratos/DPA con proveedores y modelo responsable/encargado.
5. **El riesgo principal sigue siendo el tratamiento de datos de menores**: no hay flujo documentado de verificación de identidad del representante, ni procedimiento del derecho del menor a ser escuchado, ni autorización separada por finalidad, ni política de imágenes.
6. **La región `us-east-1` y el uso de Supabase/Vercel no están evaluados jurídicamente** (E-6/DEC-19). El proyecto está en plan gratuito, sin backups automáticos ni PITR.
7. **No hay runbook de incidentes ni procedimiento de notificación a la SIC**; el literal exacto del art. 17 sobre brechas no está verificado (E-10). Tampoco hay registro de brechas.
8. **No está definido el modelo responsable/encargado** (A-06): club como responsable y VOLTERRA como encargado, o VOLTERRA como responsable. Sin eso no se pueden redactar contratos, avisos ni políticas de retención.
9. **La documentación está desincronizada con las aprobaciones del 25/10/2026**: la bitácora `05` sigue diciendo que todas las DEC están pendientes; `02-mvp-vs-futuro` y `03` no reflejan DEC-01/DEC-02/DEC-03; el `README` y `workspace-structure` siguen diciendo que el repositorio no existe.
10. **Conclusión:** VOLTERRA tiene una base de investigación y gobernanza por encima de la media para un MVP, pero **no está listo para datos reales ni para producción**. El siguiente trabajo no es más código: es cerrar el **Gate 0 legal y documental**.

---

## 1. Cómo leer este documento

### 1.1 Categorías

| Categoría | Significado |
|---|---|
| **Hecho** | Verificado en el repositorio o en una prueba ejecutada. |
| **Decisión aprobada** | Consta como aprobada por el propietario en `decisions/decision-register.md` v1.1. |
| **Propuesta** | Documento o requisito redactado, pero no aprobado. |
| **Vacío** | No existe el documento, la evidencia o la respuesta. |
| **Recomendación** | Acción propuesta por este análisis; no aprobada. |
| **Asesoría jurídica requerida** | Requiere abogado colombiano; no se resuelve por inferencia. |

### 1.2 Gates usados

| Gate | Cuándo se abre |
|---|---|
| **G0 — Datos reales** | Antes del primer dato personal real, incluido un adulto. |
| **G1 — Menores** | Antes del primer dato real de un menor. |
| **G2 — Producción** | Antes de publicar la aplicación o abrir acceso externo. |
| **G3 — Imágenes/difusión** | Antes de subir o publicar fotos/vídeos. |
| **G4 — Salud** | Antes de registrar pruebas físicas, lesiones o certificados médicos. |
| **G5 — Pagos** | Antes de habilitar cobros. |

---

## 2. Inventario documental

### 2.1 Documentos existentes y estado

| Documento | Contenido | Estado | Observación |
|---|---|---|---|
| `README.md` | Presentación del proyecto y uso | **Desactualizado** | Dice “no es un repositorio”; el repositorio y el código F1 ya existen. La parte “stack no definitivo” sigue vigente. |
| `AGENTS.md` | Reglas vinculantes del proyecto | **Vigente** | No es una decisión de producto; es el marco operativo. |
| `product/volterra-scope.md` | Alcance preliminar | **Borrador** | No refleja DEC-01/DEC-02 aprobadas. |
| `docs/research/fase1-colombia/00`–`05` | Investigación vigente (Colombia) | **Propuestas no aprobadas** | Base principal de requisitos y fuentes. `05` §6 no refleja las aprobaciones del 25/10. |
| `docs/research/fase1/` | Investigación anterior (España/UE) | **Superado** | Correctamente marcado; no usar como requisito. |
| `docs/recovery/` | Informes de recuperación y diagnóstico | **Histórico** | El diagnóstico del 23/10 dice “sin repo, sin código, sin tests”; ya no es el estado actual. |
| `decisions/decision-register.md` | Registro de 20 DEC y 5 N-xx | **Vigente (v1.1)** | 4 DEC aprobadas; faltan campos y cierre formal. |
| `decisions/stack-evaluation.md` | Matriz inicial de stack | **Insumo** | Sin decisión. |
| `decisions/dec-12-material-decision.md` | Material de evaluación DEC-12 | **Insumo** | Recomendación, no aprobación. |
| `decisions/dec-12-matriz-puntuada.md` | Matriz puntuada | **Insumo** | B 4,06 · A 3,96 · C 3,65 · D 2,58; empate técnico A/B. |
| `decisions/adr/ADR-012-capa-de-aplicacion.md` | ADR de capa de aplicación | **Propuesto** | Recomienda B (estático + PostgREST); no aprobado. |
| `docs/architecture/backend-choice.md` | Elección provisional de FastAPI | **Provisional** | Contradice parcialmente la recomendación B del ADR-012. |
| `governance/governance-charter.md` | Carta de gobernanza | **Propuesta** | Define 9 campos mínimos de decisión. |
| `governance/governance-operating-model.md` | Modelo operativo | **Propuesta** | Roles y revisiones mínimas. |
| `governance/research-evidence-standard.md` | Estándar de evidencia | **Propuesta** | Base de clasificación [J]/[H]/[R]/[I]/[A] del corpus. |
| `workspace/agent-workflow.md` | Flujo multiagente | **Propuesta** | Sin cambios recientes. |
| `workspace/security-and-permissions.md` | Reglas de seguridad de agentes | **Propuesta** | Reglas operativas; no sustituyen permisos de SO/app/BD. |
| `workspace/workspace-structure.md` | Estructura del “futuro repositorio” | **Desactualizado** | El repositorio ya existe y la estructura real difiere. |
| `integrations/notebooklm-opencode-assessment.md` | Evaluación NotebookLM/OpenCode | **Histórico** | Dice “el repositorio todavía no existe”; ya existe. |
| `docs/implementation/f1/00-autorizacion-y-alcance.md` | Autorización y alcance de F1 | **Registro de ejecución** | Documenta límites y excepción con datos ficticios. |
| `docs/implementation/f1/01-platform-admin-rpc.md` | Cambio RPC platform admin | **Implementado localmente** | Migración pendiente de aplicar al remoto. |
| `docs/implementation/f1/02-demo-local.md` | Guía de demo local | **Guía** | Requiere usuarios ficticios y credenciales locales. |
| `docs/operations/o-03-respaldo-restauracion.md` | Procedimiento de respaldo/restauración | **Parcial** | Volcado real y ensayo local; falta restaurar en Supabase real y fijar RPO/RTO. |
| `docs/operations/pendientes-bloqueantes.md` | Pendientes de DEC-12, DEC-07 y O-03 | **Parcial** | No incluye el resto de bloqueos legales. |
| `supabase/README.md` | Modelo de datos F1, migraciones y pruebas | **Vigente** | 6 migraciones aplicadas; 1 pendiente; 127/127 remoto y 134/134 local. |
| `supabase/migrations/` | 7 migraciones | **6 aplicadas + 1 pendiente** | La nueva RPC no está aplicada al remoto. |
| `supabase/tests/` | 4 suites SQL | **3 ejecutadas en remoto; 4 en local** | 65+37+25 remotas; 7 nuevas locales. |
| `volterra/` | Backend FastAPI | **Implementación inicial** | Health, auth, lectura de clubes/miembros; sin endpoints de escritura. |
| `scripts/smoke_f1.py` | Smoke test local | **Herramienta** | No ejecutado contra Supabase. |
| `.agents/skills/` | Skills de Supabase/Postgres | **Terceros** | Texto de terceros; una licencia no declarada. |

### 2.2 Lo que está realmente aprobado

**Decisiones aprobadas (25/10/2026):**

| ID | Texto asentado | Límite |
|---|---|---|
| DEC-01 | MVP = F1–F12 + F23, sin F7 (condicionada a E-1) | F7 sigue condicionada; alcance no actualizado en `product/`. |
| DEC-02 | Multi-club desde MVP, aislamiento por `club_id`, una afiliación activa, historial | Implementado en F1; F24 sigue “pendiente” en `02`. |
| DEC-03 | Matriz base de permisos por rol | Los valores concretos de F1 son provisionales. |
| DEC-08 | Techo de infraestructura y servicios: **US$0/mes** | No autoriza gastos; Vercel Hobby se mantiene por uso no comercial. |
| N-00 | El propietario es aprobador final | Base de autoridad. |
| N-05 | Observaciones privadas legibles solo por su autor | **Provisional**; tensión con ARCO (Ley 1581 art. 8). |
| N-07 | F23 exporta el club excluyendo observaciones privadas | Coherente con N-05; F23 fuera de F1. |
| N-09 | Estados `PENDIENTE`/`PROPUESTA`/`APROBADA`/`BLOQUEADA` | **No aplicado retroactivamente** al registro. |
| N-10 | No iniciar E-6, E-4, E-1 ni E-10 | **Tensión crítica:** son necesarios antes de datos reales. |

**No aprobado:** los 6 documentos de investigación, la carta de gobernanza, el modelo operativo, el estándar de evidencia, el alcance de producto, el ADR-012, la elección de FastAPI (provisional), la matriz de stack, el presupuesto de proveedores y cualquier política legal.

### 2.3 Documentos faltantes por área

| Área | Documento faltante | Gate | Por qué importa |
|---|---|---|---|
| Legal / privacidad | Política de tratamiento de datos personales | G0 | Ley 1581 art. 17; información al titular. |
| Legal / privacidad | Aviso de privacidad y textos de finalidad | G0 | Arts. 12 y 17; consentimiento informado. |
| Legal / privacidad | Manual interno de políticas y procedimientos (art. 17.k) | G0/G2 | DEC-15/E-9; obligación y evidencia. |
| Legal / privacidad | Procedimiento ARCO-P y formulario de solicitudes | G0 | Arts. 8, 14, 15; plazos 10/15 días hábiles. |
| Legal / menores | Autorización del representante legal | G1 | P-01/P-02; prueba conservable. |
| Legal / menores | Verificación de identidad y vínculo del representante | G1 | R-11; evitar suplantación. |
| Legal / menores | Registro del derecho del menor a ser escuchado | G1 | E-8; P-01. |
| Legal / menores | Autorización separada por finalidad (datos, imágenes, marketing) | G1/G3 | P-05; E-2. |
| Legal / menores | Política de imágenes, publicación y retirada | G3 | P-10; DEC-10; precedentes SIC. |
| Legal / adultos | Autorización propia del titular mayor | G0 | P-13; art. 9. |
| Legal / sensibles | Autorización expresa y política de datos de salud | G4 | P-04; E-3; DEC-16. |
| Legal / retención | Política de conservación y supresión | G0 | P-11; E-4; DEC-05. |
| Legal / transferencias | Análisis del art. 26 y registro de transferencias | G0 | P-08; E-6; DEC-19. |
| Legal / RNBD | Evaluación de inscripción y obligaciones | G0 | P-09; E-5. |
| Legal / roles | Modelo responsable/encargado y contrato con clubes | G0 | A-06; define quién responde. |
| Legal / proveedores | Registro de encargados, DPA y subencargados | G0 | Supabase, Vercel, OpenCode/modelo, GitHub, correo. |
| Legal / incidentes | Runbook de incidentes y brechas | G0/G2 | S-11/O-01; E-10. |
| Legal / incidentes | Registro de brechas y plantillas de comunicación | G0/G2 | Evidencia y respuesta. |
| Legal / gobernanza | Análisis de riesgos tipo DPIA (buena práctica) | G0 | P-12/O-02; no es figura colombiana obligatoria. |
| Legal / gobernanza | Registro de actividades de tratamiento / mapa de datos | G0 | Base para retención, transferencias y RNBD. |
| Seguridad | Política de seguridad y matriz ASVS | G0/G2 | DEC-06; S-01. |
| Seguridad | Modelo de amenazas y revisión de arquitectura | G2 | API/RLS/auth; evidencia de controles. |
| Seguridad | Política de secretos, accesos, MFA y revisión periódica | G2 | S-05; O-05. |
| Seguridad | Plan de vulnerabilidades, dependencias y parcheo | G2 | S-07; operación. |
| Operación | Plan de continuidad y recuperación | G2 | O-03/DEC-07; RPO/RTO. |
| Operación | Runbook de despliegue, rollback y monitoreo | G2 | Antes de producción. |
| Operación | Política de retención de logs y auditoría | G0/G2 | DEC-18; T-01. |
| Producto | Términos de servicio y uso aceptable | G2 | Relación con clubes/usuarios. |
| Producto | Política de cookies/analítica | G2 | Si se añaden cookies o métricas. |
| Producto | Política de safeguarding y código de conducta | G1 | Protección integral de menores, más allá de datos. |
| Producto | Política de certificado médico/aptitud | G4 | Q-34; Res. 1286/2024. |
| Producto | Metodología y aviso “no oficial” del ranking | Futuro | A-04; Q-07. |
| Producto | Accesibilidad (WCAG) | G2 | Uso por menores/entrenadores; no es requisito legal de datos, pero sí de producto. |
| Repositorio | `SECURITY.md`, `CONTRIBUTING.md`, licencia, código de conducta | G2 | Repo con terceros y futuros colaboradores. |
| Repositorio | Índice `docs/README.md` y README de `fase1-colombia/` | Ya | Navegabilidad y fuente única. |

### 2.4 Inconsistencias y documentos obsoletos

| Hallazgo | Evidencia | Impacto | Acción recomendada |
|---|---|---|---|
| El `README` dice que no es un repositorio | `README.md` líneas 1–3 | Confunde el estado real | Actualizar: repo existente, stack aún no aprobado. |
| `workspace-structure` dice “no se ha creado el repositorio” | `workspace/workspace-structure.md` | Estructura irreal | Marcar como histórica o reescribir con la estructura actual. |
| `notebooklm-opencode-assessment` dice que el repo no existe | `integrations/...` | Documento histórico | Añadir aviso de estado. |
| `diagnostico-2026-10-23` dice “sin código, tests, migraciones ni despliegue” | `docs/recovery/diagnostico...` | Snapshot obsoleto | Marcar como histórico; no usar para estado actual. |
| `05-bitacora-fuentes` §6 dice que las 20 DEC están pendientes | `05` §6 | Contradice el registro v1.1 | Actualizar o enlazar al registro como fuente única. |
| `02-mvp-vs-futuro` no refleja DEC-01/DEC-02 | `02` tabla F7/F24 | Alcance desalineado | Actualizar F7 (condicionada) y F24 (aprobada multi-club). |
| `03-requisitos` dice que la matriz de permisos no está aprobada | `03` §2(d) | Contradice DEC-03 | Marcar DEC-03 y separar los valores provisionales de F1. |
| `product/volterra-scope` sigue siendo “base de discusión” | `product/` | No refleja DEC-01 | Actualizar o declarar que el registro manda. |
| `backend-choice` (FastAPI provisional) vs. ADR-012 (opción B) | Ambos documentos | Dos direcciones técnicas | Cerrar DEC-12 con un ADR único. |
| `supabase/README` 127/127 remoto vs. 134/134 local | `README` §3 | Puede leerse como contradictorio | Mantener separado “remoto” y “local”; ya se hizo. |
| `C-01`/`C-02` siguen en `http://` | `05` §2 | Fuente no HTTPS | Corregir a HTTPS y verificar. |
| ZIP sin abrir | `fase1/00-plan-investigacion.zip`, `recovery/estado-recuperacion.zip` | Integridad no verificada | Abrir, comprobar y documentar o eliminar. |
| `docs/decisions/`, `docs/security/`, `docs/testing/` vacíos o ausentes | Diagnóstico 23/10 | Estructura incompleta | Crear índices y contenido. |

**Integridad de enlaces:** se comprobaron todos los enlaces Markdown locales del repositorio; **0 enlaces rotos**. Esto no valida el contenido, solo la navegación.

### 2.5 Lo que el corpus sí tiene bien

- Separación explícita entre **hecho, hallazgo, inferencia, recomendación y pendiente**.
- **Dos auditorías documentales** con 35 hallazgos; la mayoría cerrados.
- **Trazabilidad de fuentes** C-01…C-10 y D-01…D-22 con URL, fecha y limitaciones.
- **Matriz de riesgos R-01…R-11** y **10 preguntas legales E-1…E-10**.
- **Registro de decisiones** con 9 campos mínimos, aunque incompleto en varias fichas.
- **Diseño de datos F1** con RLS, RPC, auditoría y pruebas negativas.
- **Procedimiento de respaldo** con volcado real y ensayo local.
- **Presupuesto US$0** y uso no comercial declarado.

---

## 3. Mapa de decisiones

### 3.1 Decisiones aprobadas y su calidad documental

| ID | Estado | Bloqueo / límite | Calidad del asiento |
|---|---|---|---|
| DEC-01 | Aprobada 25/10 | F7 condicionada a E-1 | Sin opciones, justificación escrita ni fecha de revisión. |
| DEC-02 | Aprobada 25/10 | Implementación F1 | Sin justificación escrita; docs de producto no actualizadas. |
| DEC-03 | Aprobada 25/10 | Q-23; valores F1 provisionales | Matriz aprobada, pero `03` sigue diciendo “no aprobada”. |
| DEC-08 | Aprobada 25/10 | US$0/mes; no autoriza gastos | Sin justificación escrita; sin fecha de revisión. |
| N-00 | Aprobada 25/10 | — | Sin ficha de 9 campos. |
| N-05 | Aprobada 25/10, provisional | Tensión con ARCO (art. 8) | Sin ficha; requiere revisión jurídica. |
| N-07 | Aprobada 25/10 | F23 fuera de F1 | Sin ficha. |
| N-09 | Aprobada 25/10 | No aplicada al registro | Vocabulario no homologado. |
| N-10 | Aprobada 25/10 | Bloquea iniciar E-6/E-4/E-1/E-10 | **Incompatible con datos reales** mientras no se levante. |

### 3.2 Decisiones pendientes o sin decidir

| ID | Tema | Bloqueo principal | Gate |
|---|---|---|---|
| DEC-04 | Autorización de representante | E-2, E-7, E-8, Q-15/16/17 | G1 |
| DEC-05 | Retención y baja | E-4, Q-19 | G0 |
| DEC-06 | Nivel ASVS | Q-24 | G0/G2 |
| DEC-07 | RPO/RTO y respaldo | Q-27, O-03 | G2 |
| DEC-09 | Federado FVCV vs. no federado | Q-10, Q-33 | Producto |
| DEC-10 | Imágenes/difusión de menores | Q-09, E-2 | G3 |
| DEC-11 | Aceptar/mitigar R-01…R-11 | Sin tratamiento formal | G0 |
| DEC-12 | Stack / ADR | Empate A/B; host estático; no aprobado | G2 |
| DEC-13 | Proveedor/modelo OpenCode | Q-29; privacidad | G0/G2 |
| DEC-14 | Revalidación normativa | Responsable y periodicidad | G0 |
| DEC-15 | Figura de cumplimiento interno | E-9 | G0/G2 |
| DEC-16 | Datos de salud | E-3 | G4 |
| DEC-17 | Validación con clubes/mercado | Sin plan aprobado | Producto |
| DEC-18 | Alcance/retención de auditoría | Q-26 | G0/G2 |
| DEC-19 | Región/transferencia internacional | E-6, Q-21/Q-30 | G0 |
| DEC-20 | Adopción formal de requisitos y evidencia | Sin aprobar | G0 |

### 3.3 Decisiones que faltan y no tienen ID

Estas no están en el registro DEC, pero son necesarias:

1. **Modelo responsable/encargado** (A-06): quién es responsable de qué frente a clubes, atletas y tutores.
2. **Identidad legal del responsable** y datos de contacto para titulares/SIC.
3. **Mapa de datos y clasificación** (categorías, finalidades, base, destinatarios, transferencias, retención).
4. **Verificación de identidad del tutor** (R-11) y procedimiento de disputa.
5. **Derecho del menor a ser escuchado** (E-8) y registro.
6. **Procedimiento ARCO-P** con plazos y responsable.
7. **Notificación de brechas** (E-10) y registro.
8. **RNBD** (E-5) y obligaciones derivadas.
9. **Safeguarding/child protection** (más allá de datos): código de conducta, canal de denuncia, vetting de entrenadores.
10. **Proveedores/DPA/subencargados**: Supabase, Vercel, OpenCode/modelo, GitHub, correo.
11. **Términos de servicio, uso aceptable y cookies**.
12. **Retención de logs/auditoría y acceso del titular** (DEC-18; limitación actual).
13. **Criterios de go-live y producción**.
14. **Permisos de agentes OpenCode** y registro de acciones de IA (S-09/S-10/T-04).
15. **Licencias de terceros** (skills, dependencias, contenido).
16. **Seguro/ responsabilidad civil** y relación con clubes/federación.
17. **Certificado médico/aptitud** (Q-34/Res. 1286/2024).
18. **Ranking no oficial**: metodología, etiqueta y revisión.

### 3.4 Calidad del registro de decisiones

- **4 DEC aprobadas** no tienen opciones consideradas, justificación escrita ni fecha de revisión; el propio registro lo declara como desviación.
- **5 N-xx** no tienen ficha de 9 campos; se asentaron con texto mínimo.
- **N-09** define estados que el registro no usa; la homologación está pendiente.
- **N-05** sigue en tensión con el derecho de acceso ARCO.
- **N-10** impide iniciar E-6/E-4/E-1/E-10, pero el proyecto no puede operar con datos reales sin ellos. Es un bloqueo de gobernanza, no solo técnico.
- **DEC-12** tiene dos direcciones: ADR-012 recomienda B (estático + PostgREST) y `backend-choice` adoptó FastAPI provisional. El código actual es FastAPI. Falta la decisión del propietario.
- **No hay fecha de revisión** en ninguna ficha; no hay ciclo de revalidación.

---

## 4. Auditoría legal

> **Advertencia:** las normas y citas de esta sección provienen del corpus de investigación. No fueron verificadas de nuevo contra el Diario Oficial ni validadas por un abogado en esta sesión. Las clasificaciones [J]/[H]/[R]/[I]/[A] se conservan del corpus. Esto es un mapa de vacíos, no una opinión legal.

### 4.1 Marco documentado

| Norma / fuente | Uso en el corpus | Nivel de verificación declarado |
|---|---|---|
| Ley 1581 de 2012 | Protección de datos, NNA, derechos, deberes, SIC, transferencias | Texto íntegro leído (C-01) |
| Ley 1098 de 2006 | Infancia y adolescencia, intimidad | Texto íntegro leído (C-02) |
| Decreto 1074 de 2015, Cap. 25 | Reglamento de protección de datos | Arts. 2.2.2.25.2.1–.9 leídos vía D. 1377; resto parcial |
| Decreto 1377 de 2013 | Autorización, NNA, derecho a ser escuchado | Texto con mapa de compilación (C-03-3) |
| SIC Res. 21-349477/2022 y 57093/2020 | Imágenes de menores sin autorización | Notas oficiales, no resolución íntegra |
| Ley 181/1995, DL 1228/1995, Ley 1967/2019 | Marco deportivo | Extractos |
| Res. 1286/2024 y Circular IVC 009/2024 | Clubes, afiliación de menores, certificado médico | Extractos |
| FIVB Beach 2025-2028 | Reglas deportivas | Extracto |

**Diferencias clave que el corpus advierte:** no trasponer RGPD/LOPDGDD/AEPD; no hay “interés legítimo” equivalente; todo menor de 18 es NNA; no hay DPIA/DPO obligatorios equivalentes; plazos SIC de 10/15 días hábiles; sanciones hasta 2.000 SMMLV.

### 4.2 Vacíos legales E-1…E-10

| ID | Pregunta | Bloquea | Documento/evidencia que falta | Gate |
|---|---|---|---|---|
| **E-1** | ¿Resultados de menores son “datos públicos” o requieren autorización? | F7, DEC-01 | Dictamen jurídico con cita del art. 7 y D. 1074; criterio de publicación | G1 |
| **E-2** | ¿Una autorización o varias por finalidad? | DEC-04, DEC-10, imágenes | Dictamen + textos de autorización separados | G1/G3 |
| **E-3** | Datos de salud de menores: autorización y manejo reforzado | DEC-16, F15/F16 | Dictamen + política de datos sensibles | G4 |
| **E-4** | ¿Hasta cuándo retener historiales de menores tras baja? | DEC-05, retención | Dictamen + schedule de retención | G0 |
| **E-5** | ¿VOLTERRA obligada al RNBD? | P-09 | Dictamen + análisis del umbral D. 090/2018 | G0 |
| **E-6** | Cloud fuera de Colombia: art. 26 | DEC-19, región | Dictamen + análisis de transferencia | G0 |
| **E-7** | ¿Autorización electrónica válida para NNA y cómo probarla? | DEC-04, F3/F10 | Dictamen + diseño de evidencia | G1 |
| **E-8** | Derecho del menor a ser escuchado | DEC-04, F3 | Dictamen + procedimiento y registro | G1 |
| **E-9** | Manual interno/oficina de cumplimiento (art. 17.k) | DEC-15 | Dictamen + manual | G0/G2 |
| **E-10** | ¿Notificación de brechas a la SIC? Plazo | P-07/S-11/O-01 | Dictamen + runbook | G0/G2 |

**Hecho:** los 10 están abiertos. **No hay dictamen legal adjunto.** **No hay abogado colombiano identificado en el repositorio.**

### 4.3 Requisitos de privacidad P-01…P-13

| ID | Requisito | Estado documental | Evidencia existente | Falta |
|---|---|---|---|---|
| P-01 | NNA: autorización del representante + derecho a ser escuchado | **No implementado como flujo** | Requisito en `03` | Formulario, verificación, registro, prueba |
| P-02 | Prueba conservable de autorización | **No implementado** | F10 propuesto | Esquema/tabla de consentimientos y retención |
| P-03 | Carácter facultativo de datos sensibles/NNA | **No documentado en UI** | Requisito | Textos y flujo de alta |
| P-04 | Datos sensibles: autorización expresa separada | **No implementado** | F15/F16 futuro | Política y formulario |
| P-05 | Autorización por finalidad | **No implementado** | Requisito | Textos separados y registro |
| P-06 | ARCO-P operativo con plazos 10/15 días | **No implementado** | Requisito | Procedimiento, formulario, log, responsable |
| P-07 | Deberes del responsable; manual art. 17 | **No implementado** | Requisito | Manual interno |
| P-08 | Transferencias internacionales art. 26 | **No evaluado** | E-6/DEC-19 | Análisis y registro |
| P-09 | RNBD | **No evaluado** | E-5 | Análisis y registro si aplica |
| P-10 | Imagen de NNA | **No implementado** | DEC-10 pendiente | Política y consentimiento |
| P-11 | Conservación limitada | **No implementado** | E-4/DEC-05 | Schedule y purga |
| P-12 | Análisis de riesgos/DPIA (buena práctica) | **No documentado** | O-02 | Matriz de riesgos y revisión |
| P-13 | Titulares mayores: autorización propia | **No implementado** | F2/paso 2b | Formulario y flujo |

**Conclusión:** el diseño de datos F1 cubre aislamiento y permisos, pero **no cubre el ciclo de vida del consentimiento ni los derechos del titular**. Eso es esperable en F1, pero impide datos reales.

### 4.4 Requisitos de seguridad y trazabilidad

| Bloque | Estado | Evidencia | Falta |
|---|---|---|---|
| A-01/A-03: aislamiento y autorización en servidor/datos | **Parcial implementado** | RLS, RPC, guards, 65+37+25 pruebas | Matriz de autorización formal y revisión independiente |
| S-01: nivel ASVS | **No decidido** | DEC-06 pendiente | Nivel, versión y matriz requisito→estado |
| S-02/S-03/S-04: BOLA/BFLA/mass assignment | **Parcial** | RLS, column grants, RPC | Pruebas de API y revisión de endpoints |
| S-05: secretos y autenticación | **Parcial** | JWT estricto, no service_role en código | Política de secretos, rotación, MFA, escaneo |
| S-06: límites/antiabuso | **No implementado** | — | Rate limiting, cuotas, monitoreo |
| S-07: inventario/validación/errores | **Parcial** | FastAPI, tests básicos | OpenAPI versionado, validación, manejo de errores |
| S-08: cifrado tránsito/reposo | **No evidenciado** | Supabase TLS por defecto (no verificado) | Evidencia del proveedor y claves |
| S-09/S-10: permisos OpenCode | **No verificado** | Diagnóstico 23/10: reglas V2 no efectivas | Validación en runtime y política de agentes |
| S-11/O-01: incidentes | **No implementado** | E-10 | Runbook, roles, plazos, registro |
| T-01: bitácora | **Parcial** | `audit_events`, triggers | Retención, acceso del titular, exportación |
| T-02: registro de decisiones | **Parcial** | Register v1.1 | Cierre de fichas, revisión, homologación |
| T-03: registro de fuentes | **Parcial** | 05 bitácora | Cerrar vacíos §7.3 |
| T-04: IA/agentes sobre datos reales | **No aplica aún** | Sin datos reales | Política y log de acciones |
| O-02: evaluación de riesgos | **No documentada** | R-01…R-11 | Evaluación formal y tratamiento |
| O-03: backups | **Parcial** | Volcado + ensayo local | Restauración real, RPO/RTO, retención |
| O-04: corrección de datos | **No implementado** | — | Canal y trazabilidad |
| O-05: revisión periódica | **No definida** | — | Calendario, responsables |

### 4.5 Riesgos R-01…R-11

| ID | Riesgo | Estado de tratamiento | Observación |
|---|---|---|---|
| R-01 | NNA sin autorización | **No mitigado documentalmente** | Bloquea G1. |
| R-02 | Autorización genérica para todo | **No mitigado** | E-2. |
| R-03 | Acceso cruzado entre clubes | **Mitigado técnicamente** | RLS + pruebas; falta revisión de API. |
| R-04 | Reescritura de historial | **Mitigado en diseño** | Historial de membresías; duplas aún no implementadas. |
| R-05 | Transferencia internacional | **No mitigado** | E-6/DEC-19. |
| R-06 | Salud sin tratamiento sensible | **No mitigado** | F15/F16 fuera; E-3. |
| R-07 | Ranking confundido con oficial | **No aplica aún** | F20 futuro; etiqueta pendiente. |
| R-08 | Configuración expuesta por defecto | **Parcial** | RLS/deny by default; falta revisión de frontend. |
| R-09 | Plazos europeos mal aplicados | **Mitigado documentalmente** | Corpus Colombia; falta manual operativo. |
| R-10 | “Oficial de datos” como DPD europeo | **Mitigado documentalmente** | E-9/DEC-15. |
| R-11 | Tutor no verificado | **No mitigado** | Sin procedimiento de verificación. |

### 4.6 Vacíos de evidencia GC-01…GC-11

| ID | Vacío | Estado |
|---|---|---|
| GC-01 | Reglamentos FVCV de playa/licencias/ranking | Abierto (sitio JS) |
| GC-02 | PDF “Voleibol playa” Mindeporte | Abierto (>5 MB) |
| GC-03 | Guía SIC NNA | Abierto (extracto) |
| GC-04 | Umbral RNBD (D. 090/2018) | Abierto |
| GC-05 | Borradores Mindeporte 2025-2026 | Abierto |
| GC-06 | Constitución arts. 15/44 | Abierto |
| GC-07 | Entrevistas a clubes | Abierto |
| GC-08 | Datos de mercado | Abierto |
| GC-09 | Costos de afiliación/licencia | Abierto |
| GC-10 | Protocolo NNA en deporte | Abierto |
| GC-11 | Literal art. 17 sobre brechas | Abierto (E-10) |

### 4.7 Auditorías del corpus

- **Auditoría 1 (21/10):** 21 hallazgos (5 altos, 8 medios, 8 bajos); dictamen “requiere correcciones”.
- **Auditoría 2 (21/10):** 14 hallazgos (3 altos, 7 medios, 4 bajos); dictamen “requiere correcciones”.
- **Total:** 35 hallazgos; **32 cerrados, 1 parcial (E-10), 2 no aplicados** (URLs `http://` de C-01/C-02).
- **Vacío estructural:** el corpus Colombia **no tiene README/índice propio**; el único índice es el de `fase1/`, que apunta a él.
- **Vacío de gobernanza:** las auditorías no aprueban nada; el corpus sigue sin aprobación humana.

### 4.8 Temas legales que el corpus no cubre suficientemente

1. **Modelo responsable/encargado** (A-06): no hay contrato ni definición de roles.
2. **Safeguarding/child protection**: el corpus cubre datos, no protocolos de protección integral, vetting de entrenadores, códigos de conducta o canal de denuncia.
3. **Proveedores y DPA**: no hay evaluación de Supabase/Vercel/OpenCode/modelo, subencargados, retención, notificación de brechas ni transferencia.
4. **Incidentes y brechas**: no hay runbook ni registro; E-10 abierto.
5. **ARCO-P**: no hay procedimiento, formulario, SLA ni log.
6. **RNBD**: no hay evaluación.
7. **Términos, cookies y uso aceptable**: no existen.
8. **Seguro/ responsabilidad civil**: no evaluado.
9. **Federación/FVCV y certificado médico**: reglamentos no extraídos (GC-01/GC-02), Q-34 abierta.
10. **IA/agentes**: no hay política de datos para modelos/proveedores ni log de acciones (DEC-13, T-04, S-09).
11. **Licencias de terceros**: skills y dependencias; una skill no declara licencia.
12. **Accesibilidad**: no hay criterio WCAG ni revisión.

---

## 5. Gates de cumplimiento

### G0 — Antes de cualquier dato real

**No se puede abrir hasta:**

- [ ] Dictamen legal E-1…E-10 (o, como mínimo, E-6, E-4, E-1, E-10; pero G0 completo exige todos).
- [ ] Modelo responsable/encargado y contrato con clubes.
- [ ] Mapa de datos/RAT con categorías, finalidades, base, destinatarios, transferencias y retención.
- [ ] Política de tratamiento, aviso de privacidad y textos de consentimiento.
- [ ] Procedimiento ARCO-P y registro de solicitudes.
- [ ] Política de retención y supresión.
- [ ] Análisis de transferencia internacional y región.
- [ ] Evaluación RNBD.
- [ ] DPA/proveedores y subencargados.
- [ ] Runbook de incidentes/brechas y registro.
- [ ] Nivel ASVS y política de seguridad mínima.
- [ ] Permisos de agentes OpenCode validados.
- [ ] Levantar N-10 de forma explícita o sustituirla por una decisión nueva.

### G1 — Antes de datos de menores

- [ ] E-1, E-2, E-7, E-8 cerrados.
- [ ] Autorización del representante y prueba conservable.
- [ ] Verificación de identidad/vínculo del representante.
- [ ] Registro del derecho a ser escuchado.
- [ ] Autorización separada por finalidad.
- [ ] Política de imágenes y retirada.
- [ ] Safeguarding/código de conducta/canal de denuncia.
- [ ] Revisión de antecedentes de entrenadores (si aplica al modelo).
- [ ] Retención específica de datos de menores.

### G2 — Antes de producción

- [ ] ASVS L2 (o nivel aprobado) con matriz y evidencia.
- [ ] Modelo de amenazas y revisión de seguridad independiente.
- [ ] CI/CD, revisión de código, análisis de dependencias, secretos.
- [ ] Monitoreo, logs, alertas, rate limiting y respuesta a incidentes.
- [ ] Backup/restore probado en Supabase real; RPO/RTO.
- [ ] Plan de continuidad/DR y rollback.
- [ ] Contratos/DPA y subencargados.
- [ ] Términos, privacidad, cookies y accesibilidad.
- [ ] Criterios de go-live y responsable de aprobación.

### G3 — Antes de imágenes/difusión

- [ ] DEC-10 y E-2 cerrados.
- [ ] Consentimiento por finalidad y prueba.
- [ ] Política de publicación, retirada y takedown.
- [ ] Revisión de precedentes SIC.
- [ ] Separación marketing/datos.

### G4 — Antes de salud

- [ ] E-3 y DEC-16 cerrados.
- [ ] Autorización expresa adicional.
- [ ] Acceso restringido, cifrado y retención.
- [ ] Articulación con federación/seguros si aplica.
- [ ] Certificado médico/aptitud (Q-34).

### G5 — Antes de pagos

- [ ] F22 aprobada explícitamente.
- [ ] Proveedor de pagos, PCI DSS, términos, reembolsos, impuestos y datos.
- [ ] Evaluación de costos y DEC-08.

---

## 6. Plan de acción priorizado

> Las fechas y responsables concretos debe fijarlos el propietario. No se inventan aquí.

### P0 — Bloqueante para datos reales

| # | Acción | Artefacto | Responsable | Criterio de aceptación |
|---|---|---|---|---|
| 1 | Contratar asesoría jurídica colombiana y definir alcance E-1…E-10 | Contrato/encargo + plan | Propietario | Abogado identificado; preguntas y entregables acordados |
| 2 | Producir dictamen E-1…E-10 | `docs/legal/dictamenes/` | Abogado + propietario | Respuesta escrita, fuente, fecha, condiciones y límites |
| 3 | Definir modelo responsable/encargado | `docs/legal/01-modelo-roles.md` | Abogado + producto | Rol de VOLTERRA/club/tutor definido; contrato borrador |
| 4 | Crear mapa de datos/RAT | `docs/legal/02-mapa-tratamiento.md` | Producto + datos + abogado | Categorías, finalidades, base, destinatarios, transferencias, retención |
| 5 | Redactar política de tratamiento y aviso | `docs/legal/03-politica-tratamiento.md` | Abogado + technical writer | Texto publicable y comprensible |
| 6 | Diseñar autorizaciones y evidencia | `docs/legal/04-autorizaciones/` | Producto + abogado | Adulto, NNA, sensibles, imágenes, electrónica; prueba conservable |
| 7 | Diseñar ARCO-P | `docs/legal/05-arco.md` | Producto + operaciones | Formulario, plazos 10/15, log, responsable |
| 8 | Retención y supresión | `docs/legal/06-retencion.md` | Datos + abogado | Schedule por tipo; purga; excepciones |
| 9 | Transferencias/región | `docs/legal/07-transferencias.md` | Abogado + arquitectura | Art. 26 analizado; región decidida o condicionada |
| 10 | RNBD | `docs/legal/08-rnbd.md` | Abogado | Obligación y umbral evaluados |
| 11 | Incidentes/brechas | `docs/legal/09-incidentes.md` | Seguridad + abogado | Runbook, roles, plazos, registro, plantillas |
| 12 | Proveedores/DPA | `docs/legal/10-proveedores.md` | Propietario + seguridad | Supabase/Vercel/OpenCode/GitHub evaluados; DPA/subencargados |
| 13 | Levantar N-10 | Nueva decisión DEC | Propietario | Autorización explícita para iniciar E-1/E-4/E-6/E-10 |
| 14 | Actualizar registro y docs | Register + docs | Technical writer | Aprobaciones reflejadas; sin contradicciones |

### P1 — Antes de producción

| # | Acción | Artefacto |
|---|---|---|
| 15 | Fijar ASVS y matriz de controles | `docs/security/asvs.md` |
| 16 | Modelo de amenazas | `docs/security/threat-model.md` |
| 17 | Política de secretos/accesos/MFA | `docs/security/access.md` |
| 18 | Plan de vulnerabilidades/dependencias | `docs/security/vulnerability-management.md` |
| 19 | Backup/restore real + RPO/RTO | `docs/operations/backup.md` (actualizar O-03) |
| 20 | Monitoreo/alertas/on-call | `docs/operations/monitoring.md` |
| 21 | Términos, cookies, accesibilidad | `docs/legal/terms.md`, `cookies.md`, `accessibility.md` |
| 22 | Safeguarding/código de conducta | `docs/product/safeguarding.md` |
| 23 | Licencias de terceros | `docs/legal/licenses.md` |
| 24 | Criterios de go-live | `docs/operations/go-live.md` |

### P2 — Madurez

- Evaluación de riesgos tipo DPIA (buena práctica).
- Registro de acciones de IA/agentes.
- Plan de formación y confidencialidad.
- Auditoría interna periódica.
- Pruebas de penetración.
- Simulación de brecha.
- Revisión de accesibilidad.
- Revisión de contratos y seguros.
- Revisión de ranking no oficial y reglas deportivas.

---

## 7. Estructura documental recomendada

```text
docs/
├── legal/
│   ├── README.md
│   ├── 00-marco-normativo.md
│   ├── 01-modelo-responsable-encargado.md
│   ├── 02-mapa-tratamiento.md
│   ├── 03-politica-tratamiento.md
│   ├── 04-autorizaciones/
│   │   ├── adulto.md
│   │   ├── nna-representante.md
│   │   ├── datos-sensibles.md
│   │   └── imagenes.md
│   ├── 05-arco.md
│   ├── 06-retencion.md
│   ├── 07-transferencias.md
│   ├── 08-rnbd.md
│   ├── 09-incidentes.md
│   ├── 10-proveedores.md
│   ├── 11-safeguarding.md
│   ├── 12-datos-salud.md
│   ├── 13-imagenes.md
│   ├── 14-manual-art17k.md
│   └── dictamenes/
│       ├── E-01-resultados-menores.md
│       ├── E-02-autorizacion-por-finalidad.md
│       ├── E-03-salud.md
│       ├── E-04-retencion.md
│       ├── E-05-rnbd.md
│       ├── E-06-transferencias.md
│       ├── E-07-autorizacion-electronica.md
│       ├── E-08-derecho-a-ser-escuchado.md
│       ├── E-09-manual-cumplimiento.md
│       └── E-10-brechas.md
├── security/
│   ├── README.md
│   ├── asvs.md
│   ├── threat-model.md
│   ├── access-control.md
│   ├── secrets.md
│   └── vulnerability-management.md
├── operations/
│   ├── backup.md
│   ├── monitoring.md
│   ├── incident-response.md
│   ├── go-live.md
│   └── rollback.md
├── testing/
│   ├── strategy.md
│   ├── evidence.md
│   └── coverage.md
└── architecture/
    ├── system.md
    ├── data-model.md
    ├── api.md
    └── adr/
```

**Regla:** cada documento debe indicar estado (borrador/propuesta/aprobado), responsable, fecha, versión, fuentes y criterios de aceptación. No crear documentos “de cumplimiento” sin aprobación y sin evidencia.

---

## 8. Límites de este análisis

1. **No es asesoría jurídica.** No se verificaron las normas en el Diario Oficial ni se consultó a un abogado.
2. **Se basa en el corpus existente**, que declara lecturas parciales y vacíos (GC-01…GC-11).
3. **No verifica el estado remoto de Supabase** ni las credenciales; la migración nueva puede estar aplicada o no.
4. **No verifica los términos contractuales** de Supabase, Vercel, OpenCode ni del proveedor de modelo.
5. **No audita el cumplimiento real** de la Ley 1581; solo identifica evidencia y vacíos documentales.
6. **No sustituye** una revisión de seguridad independiente, una prueba de penetración ni una auditoría de código.
7. **Las fechas de revisión y los responsables** deben ser fijados por el propietario; no se inventan.

---

## 9. Conclusiones

1. **La investigación es sólida, pero no es un sistema de cumplimiento.** Falta convertir requisitos en políticas, procedimientos, formularios, contratos y evidencia.
2. **El bloqueo principal no es técnico: es legal y de gobernanza.** `E-1`…`E-10` y el modelo responsable/encargado deben resolverse antes de datos reales.
3. **Menores es el riesgo más alto.** Sin verificación de tutor, autorización por finalidad, derecho a ser escuchado y política de imágenes, no se debe abrir G1.
4. **La región y los proveedores son una decisión legal, no solo técnica.** `us-east-1`, Supabase, Vercel y OpenCode/modelo necesitan análisis de transferencia y DPA.
5. **La retención y la supresión están sin definir.** Sin schedule y purga, el historial se convierte en un pasivo.
6. **No hay respuesta a incidentes.** Sin runbook y registro, una brecha se gestiona improvisando.
7. **El registro de decisiones necesita cierre formal.** Aprobar no es cerrar: faltan justificación, opciones, revisión y homologación.
8. **La documentación está desincronizada.** El corpus dice “todo pendiente”; el registro dice 4 aprobadas. Hay que unificar la fuente de verdad.
9. **El código F1 tiene controles valiosos** (RLS, RPC, auditoría, pruebas), pero no sustituye las políticas legales.
10. **Recomendación:** abrir un workstream “Legal & Compliance Gate 0” con abogado colombiano, mapa de datos, modelo de roles, políticas/forms, proveedores, retención, transferencias e incidentes. No avanzar a datos reales hasta completarlo.

---

## Anexo A — Fuentes internas consultadas

- `AGENTS.md`
- `README.md`
- `product/volterra-scope.md`
- `decisions/decision-register.md` (v1.1)
- `decisions/stack-evaluation.md`
- `decisions/dec-12-material-decision.md`
- `decisions/dec-12-matriz-puntuada.md`
- `decisions/adr/ADR-012-capa-de-aplicacion.md`
- `governance/governance-charter.md`
- `governance/governance-operating-model.md`
- `governance/research-evidence-standard.md`
- `workspace/agent-workflow.md`
- `workspace/security-and-permissions.md`
- `workspace/workspace-structure.md`
- `workspace/reanudacion-sesion.md`
- `docs/research/fase1-colombia/00`–`05`
- `docs/research/fase1/README.md`
- `docs/recovery/diagnostico-2026-10-23.md`
- `docs/recovery/estado-recuperacion.md`
- `docs/operations/o-03-respaldo-restauracion.md`
- `docs/operations/pendientes-bloqueantes.md`
- `docs/implementation/f1/00-autorizacion-y-alcance.md`
- `docs/implementation/f1/01-platform-admin-rpc.md`
- `docs/implementation/f1/02-demo-local.md`
- `docs/architecture/backend-choice.md`
- `supabase/README.md`
- `supabase/migrations/` y `supabase/tests/`
- `integrations/notebooklm-opencode-assessment.md`

## Anexo B — Checklist mínimo de documentos antes de G0

- [ ] Dictamen E-1…E-10.
- [ ] Modelo responsable/encargado.
- [ ] Mapa de datos/RAT.
- [ ] Política de tratamiento.
- [ ] Aviso de privacidad.
- [ ] Autorización adulto.
- [ ] Autorización NNA + verificación de tutor.
- [ ] Registro del derecho a ser escuchado.
- [ ] Autorización de datos sensibles.
- [ ] Autorización de imágenes.
- [ ] Procedimiento ARCO-P.
- [ ] Retención y supresión.
- [ ] Transferencias internacionales.
- [ ] RNBD.
- [ ] Incidentes/brechas.
- [ ] Proveedores/DPA/subencargados.
- [ ] ASVS y política de seguridad.
- [ ] Backup/restore y RPO/RTO.
- [ ] Safeguarding/código de conducta.
- [ ] Términos/cookies/accesibilidad.
- [ ] Criterios de go-live.

---

**Fin del análisis.** Cualquier avance sobre datos reales, menores, imágenes, salud, proveedores o producción requiere decisión explícita del propietario y, cuando corresponda, dictamen jurídico colombiano.
