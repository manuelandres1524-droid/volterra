# FASE 1 — A3: Requisitos de arquitectura, seguridad, privacidad, permisos y trazabilidad

> **SUPERADO — este no es el corpus vigente.** Investigación original de FASE 1 para **España/UE** (20/10/2026). El corpus vigente es **[`../fase1-colombia/`](../fase1-colombia/)** (Colombia, 21/10/2026), que sustituye la jurisdicción, las fuentes, los plazos y las decisiones. Este documento se conserva íntegro por trazabilidad histórica: **no usar sus requisitos, plazos ni base jurídica como vigentes**. Índice y alcance: [`README.md`](README.md).

**Área:** A3 · **Agente responsable:** `governance-analyst` (+`researcher` para fuentes normativas).
**Estado:** propuesta — NO aprobada. **Fecha de consulta de fuentes:** 20/10/2026.
**Modo:** solo lectura. No se modificó, creó ni borró ningún archivo durante la investigación; no se instaló ni se escribió código.
**Jurisdicción confirmada por el usuario:** España/UE, con **menores de edad** entre los atletas.

> **Aviso:** este documento NO declara ningún cumplimiento normativo. Es una propuesta de requisitos pendiente de aprobación humana y de revisión jurídica/de seguridad profesional. Tampoco selecciona tecnología ni proveedor.

---

## 1. Resumen ejecutivo

- Carta de gobernanza, estándar de evidencia y alcance de producto existen pero están **en estado de propuesta, no aprobados** (`governance-charter.md` L2; `research-evidence-standard.md` L2; `volterra-scope.md` L2).
- La jurisdicción y los menores activan obligaciones que condicionan decisiones de arquitectura desde el diseño: consentimiento/representación de menores (umbral 14 años, LOPDGDD art. 7.1 confirmado por AEPD), posible condición de **categoría especial** de datos de salud derivados de pruebas físicas (RGPD art. 9), y consulta sobre si es necesaria la designación de **DPD** (la AEPD lo confirma para federaciones deportivas que tratan datos de menores; para clubes/plataforma es cuestión de asesoría — P-01/P-02).
- **OWASP ASVS v5.0.0** (estable, mayo 2025) y **OWASP API Security Top 10 (2023)** proporcionan catálogos de requisitos verificables; citar siempre la versión (`v5.0.0-x.y.z`) porque los identificadores cambiaron respecto a 4.0.3.
- La documentación oficial de OpenCode confirma que los agentes se restringen con claves `permission` (`ask`/`allow`/`deny`) por herramienta y por comando shell, y que **por defecto OpenCode permite todas las operaciones sin aprobación**; el campo `tools` está deprecado en favor de `permission`. Valida `workspace/security-and-permissions.md`, pero **sustituye solo el control de agentes de desarrollo, no los permisos de la aplicación VOLTERRA**.

### Limitaciones de esta consulta (transparencia)

- **EUR-Lex bloqueó la recuperación del texto del RGPD** en tres intentos (20/10/2026). Las referencias al RGPD proceden de **documentos oficiales de la AEPD que citan artículos concretos**, no de lectura directa del texto consolidado. Verificar cada artículo contra EUR-Lex antes de cualquier decisión (P-08).
- El BOE devolvió correctamente la **LOPDGDD consolidada (última actualización 27/12/2025)**; las citas de artículos concretos (7.1, 34, 92) proceden de la AEPD.

### Fuentes consultadas (20/10/2026)

| # | Fuente | URL | Tipo | Estado |
|---|---|---|---|---|
| F1 | RGPD (Reglamento UE 2016/679) | eur-lex.europa.eu (múltiples URLs) | Norma | ⚠️ No recuperable (bloqueo/respuesta vacía); verificar manualmente |
| F2 | LOPDGDD (LO 3/2018), texto consolidado | https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673 | Norma (BOE) | ✅ Recuperada |
| F3 | AEPD — FAQ bases legitimación categorías especiales | https://www.aepd.es/preguntas-frecuentes/.../FAQ-0215-... | Guía autoridad | ✅ |
| F4 | AEPD — Guía para el Ciudadano (2018) | https://www.aepd.es/guias/guia-ciudadano.pdf | Guía autoridad | ✅ (extracción parcial) |
| F5 | AEPD — Infografía consentimiento de menores (2020) | https://www.aepd.es/sites/default/files/2020-12/infografia-consentimiento-menores.pdf | Guía autoridad | ✅ |
| F6 | AEPD — FAQ: federaciones y DPD | https://www.aepd.es/preguntas-frecuentes/10-menores-y-educacion/FAQ-1012-... | Guía autoridad | ✅ |
| F7 | AEPD — Guía del RGPD para responsables (2018) | https://www.aepd.es/guias/guia-rgpd-para-responsables-de-tratamiento.pdf | Guía autoridad | ✅ (índice/extracción parcial) |
| F8 | AEPD — Guía de Protección de Datos por Defecto (2020) | https://www.aepd.es/guias/guia-proteccion-datos-por-defecto.pdf | Guía autoridad | ✅ (extracción parcial) |
| F9 | AEPD — Guía del deber de informar (información por capas) | https://www.aepd.es/guias/guia-modelo-clausula-informativa.pdf | Guía autoridad | ✅ |
| F10 | AEPD — Menores, salud digital y privacidad (2024) | https://www.aepd.es/guias/estrategia-menores-aepd-lineas-accion.pdf | Estrategia AEPD | ✅ (extracción parcial) |
| F11 | AEPD — Gestión del riesgo y EIPD | https://www.aepd.es/guias/gestion-riesgo-y-evaluacion-impacto-en-tratamientos-datos-personales.pdf | Guía autoridad | ✅ (existencia confirmada; no leída íntegra) |
| F12 | AEPD — Resolución E-06752-2020 (federación de pádel, uso de imagen/datos de deportistas) | https://www.aepd.es/documento/e-06752-2020.pdf | Resolución | ✅ (extracción parcial) |
| F13 | OWASP ASVS — página del proyecto y release v5.0.0 | https://owasp.org/projects/asvs ; https://github.com/OWASP/ASVS/releases | Estándar | ✅ |
| F14 | OWASP Developer Guide — secciones ASVS (V1–V14) | https://devguide.owasp.org/en/03-requirements/05-asvs/ | Guía OWASP | ✅ |
| F15 | OWASP API Security Top 10 (2023) | https://owasp.org/API-Security/editions/2023/en/0x11-t10 | Estándar | ✅ |
| F16 | OpenCode — Config | https://docs.opencode.ai/docs/config/ | Doc oficial | ✅ |
| F17 | OpenCode — Agents | https://docs.opencode.ai/docs/agents/ | Doc oficial | ✅ |

Fuentes **no** consultadas y por tanto no usadas: guía sectorial específica de "ámbito deportivo" de la AEPD no localizada como documento único (los resultados fueron resoluciones, FAQ y guías generales); artículos de blogs comerciales (descartados como base de requisitos).

---

## 2. Requisitos propuestos

Clasificación: **H** = Hecho verificado · **F** = Hallazgo de fuente · **I** = Inferencia · **R** = Recomendación · **P** = Pendiente. Todos en estado **propuesto / pendiente de aprobación humana**.

### (a) Arquitectura y separación de datos multi-club

| ID | Requisito verificable | Fuente | Clas. | Prioridad |
|---|---|---|---|---|
| A-01 | Todo registro de datos de dominio (club, atleta, dupla, entrenamiento, prueba física, resultado, pago) porta un identificador de pertenencia a club aplicado como filtro obligatorio en **cada consulta de datos**, no solo en la interfaz. Verificable: existe prueba automatizada que demuestra que un usuario del club X no puede leer ni modificar registros del club Y mediante llamadas directas a API/persistencia. | `volterra-scope.md` L11; `security-and-permissions.md` L8 | I | Alta |
| A-02 | El historial de atletas, duplas (periodos de asociación) y resultados es **inmutable en sentido histórico**: los cambios de dupla crean periodos nuevos y no reescriben periodos anteriores; cada corrección conserva quién/cuándo/por qué. Verificable: no existe operación de negocio que elimine ni sobrescribra periodos históricos sin dejar rastro. | `volterra-scope.md` L8–9; `governance-charter.md` L20 | R | Alta |
| A-03 | La autorización se evalúa en el servidor y en la capa de datos para **todas** las operaciones de lectura y escritura; la interfaz no es la única barrera. Verificable: pruebas negativas de acceso contra la API con identidades de cada rol. | `volterra-scope.md` L11; OWASP API1/API5:2023 (F15) | R | Alta |
| A-04 | Existe separación explícita entre **ranking competitivo** e **indicadores de desarrollo** en el modelo de datos, y las reglas de ranking son configurables y versionadas. Verificable: cada valor de ranking almacenado referencia la versión de la regla que lo produjo. | `volterra-scope.md` L10; `governance-charter.md` L20 | R | Media |
| A-05 | Los entornos (desarrollo, pruebas, producción) están separados y los entornos no productivos usan **datos ficticios**. Verificable: no hay datos personales reales en entornos no productivos. | `security-and-permissions.md` L5–6; F8 | R | Alta |
| A-06 | Se define y documenta el modelo de **responsable/encargado** de tratamiento por cada tratamiento antes de operar con datos reales; el análisis depende de cómo se organice contractualmente la prestación (no hay respuesta única). | F12; F7 | P (requiere asesoría jurídica) | Alta |

### (b) Seguridad

| ID | Requisito verificable | Fuente | Clas. | Prioridad |
|---|---|---|---|---|
| S-01 | Se adopta un nivel de verificación ASVS definido para el proyecto (recomendado evaluar nivel 2 como punto de partida para aplicaciones con datos personales) y cada requisito aplicable se cita con versión (`v5.0.0-x.y.z`). Verificable: existe matriz requisito → estado (cumple/no cumple/no aplica). | F13, F14 | R | Alta |
| S-02 | Autorización a nivel de objeto verificada en cada endpoint que recibe identificadores (riesgo API1:2023 BOLA). Verificable: pruebas que intenten acceder a objetos por ID desde otra identidad/club y esperan denegación. | F15 | F→R | Alta |
| S-03 | Separación entre funciones administrativas (plataforma) y de club, y entre funciones de club y de usuario (riesgo API5:2023 Broken Function Level Authorization). Verificable: matriz rol × operación testeada en servidor. | F15 | F→R | Alta |
| S-04 | No se expone ni se acepta asignación de campos no autorizados en peticiones (riesgo API3:2023, prop-level authorization). Verificable: listas de campos permitidos por operación y pruebas de asignación masiva. | F15 | F→R | Alta |
| S-05 | Autenticación robusta y gestión de sesiones verificables (riesgo API2:2023); sin secretos ni claves privilegiadas en el frontend; sin tokens de agentes ni credenciales en prompts o logs. | F15; `security-and-permissions.md` L5, L7 | R | Alta |
| S-06 | Límites de consumo de recursos y protección frente a abuso de flujos de negocio sensibles (riesgos API4 y API6:2023), con relevancia directa si se aprueban pagos. | F15 | F→R | Media (Alta si pagos se activan) |
| S-07 | Inventario de endpoints/versión de API (riesgo API9:2023) y validación de datos de entrada, manejo de errores y comunicación segura conforme a los capítulos aplicables del ASVS. | F14, F15 | R | Media |
| S-08 | Cifrado en tránsito y en reposo de datos personales; las decisiones concretas de implementación requieren aprobación de stack (pendiente). | F8; `governance-charter.md` L27 | R | Alta |
| S-09 | Uso de las configuraciones de permisos de OpenCode para agentes de desarrollo: agentes de análisis/auditoría con `edit: deny` y shell restringido; `git push`, instalación y red sujetos a `ask`; **verificado contra doc oficial**: la config por defecto de OpenCode **permite todo sin aprobación**, por lo que la restricción debe configurarse explícitamente. El campo `tools` está deprecado; usar `permission`. | F16, F17; `security-and-permissions.md` | H (doc) + R | Alta |
| S-10 | La configuración de OpenCode **no** sustituye permisos de SO, repositorio, aplicación ni base de datos (los docs describen control de herramientas del agente, no control de acceso a datos de la aplicación). | F16, F17; `security-and-permissions.md` L10 | H | Alta |

### (c) Privacidad y protección de datos (menores y datos sensibles)

| ID | Requisito verificable | Fuente | Clas. | Prioridad |
|---|---|---|---|---|
| P-01 | **Menores:** para menores de 14 años, el consentimiento lo otorgan los padres/tutores (LOPDGDD art. 7.1, citado por AEPD); para 14–17 años, el menor puede consentir por sí salvo norma específica; el responsable debe hacer esfuerzos razonables de verificación del consentimiento parental (art. 8.2 RGPD, citado por AEPD). Verificable: el alta de un atleta menor registra quién consentió, con qué identidad y cuándo. | F5, F6 | F | Alta |
| P-02 | **Capacidad de DPD:** la AEPD confirma que las federaciones deportivas que tratan datos de menores están obligadas a designar DPD (LOPDGDD art. 34.1.º, 3 y 4, citados). Si VOLTERRA o sus clubes quedan dentro de supuestos análogos, procede designación y comunicación a la autoridad. **Requiere asesoría**; este informe no lo declara. | F6 | F + P | Alta |
| P-03 | **Datos de salud:** los datos relativos a la salud son categoría especial con prohibición general salvo excepciones del art. 9.2 RGPD. Si las pruebas físicas registran lesiones, diagnósticos o parámetros fisiológicos, el tratamiento entra en este ámbito. Verificable: inventario de campos de pruebas físicas clasificado como "salud / no salud" revisado antes de implementarlos. | F3, F4 | F | Alta |
| P-04 | **Minimización por diseño y por defecto:** cada fase recoge solo los datos mínimos; la configuración por defecto es la más restrictiva (perfiles/rankings no públicos por defecto; visibilidad de datos de menores restringida). Verificable: configuración por defecto documentada y revisada. | F8 | F→R | Alta |
| P-05 | **Información por capas** a los interesados en el alta y en la web (1.ª capa resumida; 2.ª capa detallada con plazos, destinatarios completos y derechos). | F9, F4 | F | Alta |
| P-06 | **Base jurídica por tratamiento** documentada antes de operar, especialmente para: ficha de atleta, imágenes/difusión de resultados, notificaciones y pagos. El consentimiento no puede ser tácito. | F3, F4, F12 | F | Alta |
| P-07 | **Conservación limitada:** plazos o criterios documentados por tipo de dato (historial deportivo vs. contacto vs. credenciales vs. auditoría), comunicados en la 2.ª capa. | F8, F9 | F→R | Alta |
| P-08 | **Derechos de las personas:** procedimiento operativo para acceso, rectificación, supresión, oposición, limitación y portabilidad, con responsable y plazos, compatible con la conservación del historial deportivo (conflicto potencial rectificación vs. integridad — ver P-09). | F7, F9 | F | Alta |
| P-09 | Las correcciones de datos personales **no reescriben silenciosamente** el historial: se registran como enmiendas con trazabilidad (compatibiliza exactitud con el principio de historial del producto). | F2 (art. 4 leído); `volterra-scope.md` L9 | I | Media |
| P-10 | **Evaluación de impacto (EIPD)** valorada antes de tratar datos de menores a escala, categorías especiales o seguimiento sistemático; la AEPD recomienda incluir riesgos de menores. Verificable: decisión documentada de realizarla o no, con justificación. | F10, F7, F11 | F→R | Alta |
| P-11 | **Transferencias internacionales:** si se eligen proveedores con tratamiento fuera de la UE/EEE, se documenta la garantía aplicable antes de contratar (decisión de stack pendiente). | F7 (cap. 7) | P | Media |
| P-12 | **Uso de imagen/resultados públicos:** la difusión de imágenes o datos de deportistas —con menores, con más razón— exige consentimiento específico para la finalidad promocional; no basta la relación con la entidad (criterio AEPD en ámbito deportivo). Verificable: registro de consentimientos de difusión por atleta y finalidad. | F12 | F | Alta |
| P-13 | **Datos de menores en ranking público:** evaluación explícita (decisión humana) de si los atletas menores aparecen en rankings/resultados visibles, con qué datos mínimos y con qué base; por defecto, máxima restricción. | F8, F10; `governance-charter.md` L22 | R + P | Alta |

### (d) Permisos por rol — **MATRIZ PROPUESTA, PENDIENTE DE APROBACIÓN HUMANA**

> ⚠️ **Esta matriz NO está aprobada.** Derivada de los roles candidatos de `volterra-scope.md` (L15–16) y del principio de mínimo privilegio (`governance-charter.md` L23). Cualquier adopción requiere aprobación explícita (`governance-charter.md` L28) y verificación de que la autorización aplica en servidor y datos (A-01, A-03).

Leyenda: C = crear/editar dentro de su club · L = lectura · — = denegado por defecto · ⚠ = requiere decisión/consentimiento específico.

| Operación | Plataforma | Admin club | Entrenador | Atleta |
|---|---|---|---|---|
| Gestionar clubes y usuarios del club | C/L (todos los clubes) | C/L (su club) | — | — |
| Categorías del club | C/L (todas) | C/L (su club) | L | L |
| Perfil de atleta (datos no sensibles) | L | L (su club) | L (su club) | L (el propio) |
| Pruebas físicas con posible dato de salud | — | ⚠ según resultado de P-03/P-06 | ⚠ idem | L (el propio) ⚠ |
| Duplas y periodos | L | C/L (su club) | C/L (su club) | L (propio/club) |
| Entrenamientos y asistencia | L | C/L | C/L (sus sesiones) | L (propio) |
| Observaciones/evaluaciones del entrenador | L | L (su club) | C/L (las propias) | L (las propias) ⚠ |
| Resultados de competencias | L | C/L | C/L | L |
| Rankings e informes | L | L | L | L (propio) ⚠ visibilidad menores (P-13) |
| Pagos | — | ⚠ dominio suspendido hasta aprobación (`volterra-scope.md` L23) | — | — |
| Gestión de consentimientos de menores | L | ⚠ (¿o solo tutor?) — decisión pendiente | — | — |
| Bitácora de auditoría | L | L (su club) | — | — |
| Configuración de la plataforma | C/L | — | — | — |

Clasificación de toda la matriz: **R + P (pendiente de aprobación)**. Regla transversal propuesta: todo acceso por defecto denegado salvo permiso explícito; revisión periódica (`governance-charter.md` L23).

### (e) Trazabilidad

| ID | Requisito verificable | Fuente | Clas. | Prioridad |
|---|---|---|---|---|
| T-01 | Bitácora de auditoría inmutable para acciones sensibles sobre datos personales de atletas (creación, modificación, eliminación, exportación, cambio de permisos, cambio de consentimiento), con quién, cuándo, qué, desde dónde y resultado. | `governance-charter.md` L24; F15 | R | Alta |
| T-02 | Registro de decisiones de gobernanza con el formato mínimo del `governance-charter.md` (ID, estado, proponente/aprobador, contexto, opciones, evidencia, decisión, riesgos, fechas). | `governance-charter.md` L35–44 | H (interno) | Alta |
| T-03 | Registro de fuentes de investigación con título, organización, URL, fecha de consulta y tipo de evidencia; las afirmaciones sin fuente se marcan como inferencia o pendiente. | `research-evidence-standard.md` L11–15 | H (interno) | Media |
| T-04 | Acciones de agentes IA que tocan datos reales o escriben en repositorio quedan registradas y pasan por revisión/aprobación humana; los agentes de auditoría operan en solo lectura. | `governance-charter.md` L16–17, L32; `security-and-permissions.md` L1–3; F17 | R | Alta |
| T-05 | Toda métrica mostrada (rankings, evolución) es trazable a su fuente de datos y a la versión de regla que la calculó. | `governance-charter.md` L20; A-04 | R | Media |
| T-06 | Cambios de esquema de datos, reglas de ranking, permisos y retención pasan por el ciclo de gobernanza (proponer → evidencia → aprobación → implementar → verificar). | `governance-charter.md` L26–33, L47 | H (interno) | Alta |

### (f) Operación

| ID | Requisito verificable | Fuente | Clas. | Prioridad |
|---|---|---|---|---|
| O-01 | Procedimiento de **brechas de seguridad**: detección, evaluación y notificación a la autoridad (AEPD) cuando proceda, y comunicación a afectados; plazo de referencia de 72 h — **verificar el artículo en el texto oficial** (P-08). Verificable: runbook documentado con roles y plazos. | F1 (no recuperable) + fuentes secundarias; F7 | P (verificar) | Alta |
| O-02 | **Evaluación de riesgos** del tratamiento y, según resultado, EIPD (P-10), revisada ante cambios relevantes. | F7, F11 | F→R | Alta |
| O-03 | **Respaldos y recuperación:** frecuencia, cifrado, retención y **pruebas periódicas de restauración** documentadas. | F8; R propia | R | Alta |
| O-04 | **Corrección de datos y de errores:** canal para que clubes/usuarios reporten inexactitudes; correcciones con trazabilidad (P-09); comunicación de cambios relevantes. | `governance-charter.md` L43–47; F2 art. 4 | R | Media |
| O-05 | **Revisión periódica** de permisos por rol, accesos de agentes, registros de consentimiento, plazos de conservación, inventario de API y estado de requisitos ASVS. Verificable: calendario de revisión con responsable y acta. | `governance-charter.md` L23, L47 | R | Media |
| O-06 | **Pagos permanecen fuera de operación** hasta aprobación explícita, incluyendo sus requisitos de seguridad y trazabilidad añadidos. | `volterra-scope.md` L23; `governance-charter.md` L30 | H (decisión interna) | Alta |

---

## 3. Riesgos

| ID | Riesgo | Descripción | Impacto | Mitigación propuesta (no aprobada) |
|---|---|---|---|---|
| R-01 | **Sesgo y confianza excesiva en métricas deportivas** | Rankings y "evolución medible" pueden capturar solo lo medible (resultados) y omitir contexto (lesión, carga, desarrollo); un número aislado puede usarse para decisiones de selección o evaluación de menores con más autoridad de la que merece. | Alto para atletas | Separar ranking de desarrollo (A-04); mostrar métricas con contexto y limitaciones; "la IA recomienda y explica, no decide" (`governance-charter.md` L21); revisión humana obligatoria; no automatizar decisiones deportivas sensibles. |
| R-02 | **Interpretación incorrecta de métricas** | Duplicar fuentes de verdad o versionar mal reglas produce rankings inconsistentes que invalidan comparaciones temporales. | Medio-alto (credibilidad) | Una sola fuente de verdad por dato (`governance-charter.md` L19); versionado de reglas (A-04, T-05). |
| R-03 | **Accesos indebidos entre clubes o dentro del club** | Un entrenador de club A accede a datos del club B, o ve pruebas físicas de atletas que no entrena (BOLA/BFLA, API1/API5:2023). | Alto (datos de menores y salud) | A-01, A-03, S-02, S-03; pruebas negativas automatizadas; mínimo privilegio y revisión (matriz (d)). |
| R-04 | **Reescritura de historial** | Cambios de dupla o correcciones sobrescriben el pasado, perdiendo la trayectoria deportiva y la trazabilidad. | Alto (integridad del producto) | A-02, P-09, T-01, T-06; operaciones de enmienda, no de sustitución. |
| R-05 | **Uso de datos fuera de finalidad** | Usar datos de atletas (especialmente menores) para entrenar modelos, análisis externos, marketing o difusión sin base ni consentimiento específico. | Muy alto (legal y reputacional) | `governance-charter.md` L33 exige aprobación explícita; P-06, P-12; inventario de finalidades; revisión de nuevas herramientas de agentes (T-04). |
| R-06 | **Datos de salud sin tratamiento como categoría especial** | Registrar "pruebas físicas" sin clasificar campos implica tratar datos de salud sin base art. 9 RGPD. | Muy alto | P-03, P-10; clasificación campo a campo antes de implementar. |
| R-07 | **Consentimiento de menores inválido o no verificado** | Alta de menores sin registro de consentimiento parental o sin verificación razonable (art. 8.2 RGPD). | Alto | P-01; registro de quién/cuándo/cómo se verificó. |
| R-08 | **Exposición por configuración por defecto** | Rankings, fotos o perfiles públicos por defecto exponen datos de menores sin decisión humana. | Alto | P-04, P-13; privacidad por defecto como regla de revisión. |

---

## 4. Preguntas que requieren asesoría profesional o decisión del usuario

**Asesoría jurídica (protección de datos):**
1. **P-01/P-02:** ¿La plataforma (y/o cada club) está obligada a designar DPD por el art. 34 LOPDGDD al tratar datos de menores en el ámbito deportivo?
2. **P-03:** ¿Qué campos concretos de "pruebas físicas" constituyen datos de salud (art. 9 RGPD) y cuál es la base legítima aplicable? Caso por caso.
3. **P-06:** Base jurídica de cada tratamiento: ficha de atleta, notificaciones, publicación de resultados e imágenes, y (si se aprueba) pagos.
4. **A-06:** Reparto de roles de responsable/encargado entre plataforma y clubes, y contratos necesarios (art. 28 RGPD).
5. **P-08:** Texto verificado del RGPD (EUR-Lex bloqueó la consulta) y de los plazos exactos de notificación de brechas (art. 33).
6. **P-12/P-13:** Legitimación para difusión de imágenes, nombres y resultados de atletas menores; ¿los menores aparecen en rankings públicos y con qué garantías?

**Asesoría/de seguridad profesional:**
7. **S-01:** Nivel ASVS a adoptar (2 vs. 3) y quién realiza la verificación.
8. **O-03:** Objetivos de respaldo y recuperación (RPO/RTO) realistas para un servicio deportivo con temporada.
9. **S-09:** Validar en la versión instalada de OpenCode que la configuración de `permission` produce el comportamiento esperado (el README ya lo prevé, L5).

**Decisiones del usuario (no aprobadas):**
10. Aprobar, modificar o rechazar la **matriz de permisos (d)** y la regla "todo por defecto denegado".
11. Aprobar la **carta de gobernanza** y el **estándar de evidencia** (hoy en propuesta) como base vinculante del registro de decisiones (T-02, T-06).
12. Definir la política de **visibilidad de datos de menores** (P-13) antes del primer piloto con clubes reales.
13. Confirmar si los dominios suspendidos (pagos, IA avanzada) siguen fuera y con qué umbral de reevaluación (`volterra-scope.md` L23).
14. Designar persona responsable de privacidad operativa (hasta decidir sobre DPD) y de revisión periódica O-05.

---

## Cierre (formato AGENTS.md)

- **Resumen:** Requisitos propuestos en 6 áreas (arquitectura multi-club, seguridad, privacidad con menores y salud, matriz de permisos pendiente, trazabilidad, operación), con 30+ requisitos etiquetados por clasificación/prioridad/estado, 8 riesgos y 14 preguntas de decisión/asesoría. Ninguna tecnología ni proveedor seleccionados; ningún cumplimiento declarado.
- **Archivos modificados:** ninguno durante la investigación.
- **Pruebas/ejecución real:** lectura de 5 archivos locales pedidos (los 5 existen); consultas web del 20/10/2026: BOE (LOPDGDD consolidada ✅), EUR-Lex RGPD (❌ 3 intentos — limitación registrada), AEPD (FAQ, guías e infografía ✅), OWASP (ASVS 5.0.0, API Security 2023 ✅), OpenCode docs config/agents ✅. No se ejecutaron pruebas de código (no aplica).
- **Riesgos:** R-01…R-08.
- **Decisiones pendientes:** matriz de permisos, carta de gobernanza, política de menores, base jurídica por tratamiento, DPD, nivel ASVS, umbral de reevaluación de dominios suspendidos.
- **Siguiente paso:** respuestas a las preguntas 1–6 con asesoría jurídica y 10–14 como decisiones; con ese resultado, una segunda iteración puede refinar la matriz de permisos y el inventario de datos de pruebas físicas. Ninguna recomendación de este informe está aprobada.
