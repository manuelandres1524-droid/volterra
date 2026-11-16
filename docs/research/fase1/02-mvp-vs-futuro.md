# FASE 1 — A2: Delimitación del MVP y funciones futuras

> **SUPERADO — este no es el corpus vigente.** Investigación original de FASE 1 para **España/UE** (20/10/2026). El corpus vigente es **[`../fase1-colombia/`](../fase1-colombia/)** (Colombia, 21/10/2026), que sustituye la jurisdicción, las fuentes, los plazos y las decisiones. Este documento se conserva íntegro por trazabilidad histórica: **no usar sus requisitos, plazos ni base jurídica como vigentes**. Índice y alcance: [`README.md`](README.md).

**Área:** A2 · **Agente responsable:** `product-analyst` (+apoyo `researcher`).
**Estado:** propuesta — NO aprobada. **Fecha:** 20/10/2026.
**Modo:** solo lectura · sin stack seleccionado.

---

## 1. Resumen ejecutivo

Hecho verificado (archivos locales): `product/volterra-scope.md` es "base de discusión, no especificación aprobada"; no hay stack aprobado; los permisos por rol están explícitamente "pendientes"; pagos, ranking completo, WhatsApp e IA avanzada "no se consideran incluidos hasta aprobación explícita".

Hallazgo de fuente (A1, 20/10/2026): los problemas mejor sustentados son la inmutabilidad del historial de duplas, la protección de datos de menores, las licencias/autorizaciones federativas con plazos, la separación ranking/desarrollo y los permisos por rol. Hay vacíos serios: sin entrevistas a clubes españoles, sin datos de mercado, y la evidencia normativa procede de extractos, no de PDFs íntegros.

Inferencia central: el recorrido vertical candidato del scope (club → atleta/categoría → sesión → asistencia → observación → historial con permisos) es viable como MVP **solo si se acota por club_id en servidor** (propuesta de A3, no aprobada), y **si el MVP no replica el ranking federativo RNVP** (pendiente de decisión del usuario). Sin esa decisión, la separación "ranking vs desarrollo" se resuelve en el MVP solo como *estructura de datos separada*, sin cálculo de ranking.

Recomendación provisional: MVP = gestión operativa diaria de un club (problemas 4, 5, 9 en parte, 12 parcialmente) + estructura inmutable de duplas (problema 1, solo modelado, sin cálculo de puntos) + registro de consentimiento de menores (problema 2, funcionalidad mínima de registro, no de gestión legal completa). Fuera: ranking completo, competición/resultados oficiales, carga-fatiga validada, pruebas físicas estandarizadas, pagos, notificaciones, informes complejos, difusión de imágenes.

---

## 2. Inventario de funcionalidades candidatas

| # | Funcionalidad | Etiqueta | Problema A1 | Prioridad | Justificación |
|---|---|---|---|---|---|
| F1 | Gestión de club y usuarios (altas/bajas, roles asignables) | MVP | 4, 9, 12 | Alta | Primer paso del recorrido vertical; sin ello no hay operación. Los permisos concretos dependen de la matriz pendiente. |
| F2 | Perfil de atleta con categoría | MVP | 4, 5, 7 (parcial) | Alta | Entidad mínima sobre la que se registran asistencia y observaciones. |
| F3 | Duplas como pares con periodos de asociación (sin reescribir historial) | MVP (modelado de datos y consulta; sin cálculo de puntos) | 1 | Alta | Hecho verificado por scope y hallazgo A1: los periodos se acumulan, no se sobreescriben. El *cálculo* de puntos RNVP está FUERA-MVP o PENDIENTE (ver F11). |
| F4 | Registro de sesiones de entrenamiento (fecha, tipo, grupo) | MVP | 4, 5 | Alta | Núcleo del recorrido vertical. |
| F5 | Registro de asistencia por sesión | MVP | 4, 5 | Alta | Directamente en el recorrido vertical; problema 5. |
| F6 | Observaciones/evaluación libre del entrenador por sesión y atleta | MVP | 5, 11 (parcial) | Media | El scope lo sitúa en el recorrido vertical. Texto libre + escala simple; los informes derivados quedan fuera. |
| F7 | Registro de consentimiento de menores (quién, cuándo, para qué) | MVP (funcionalidad mínima de registro) | 2 | Alta | A3 lo propone; A1 lo clasifica con confianza alta. El MVP registra el hecho del consentimiento; la gestión legal completa (revocación, caducidad, denegación) es futura. **Pendiente:** ¿atletas <14 en el alcance? |
| F8 | Permisos por rol aplicados en servidor y datos | MVP (estructura; matriz concreta PENDIENTE-DE-DECISIÓN) | 9 | Alta | Scope y A3 lo exigen. La matriz de permisos está "PENDIENTE de aprobación" (A3). Etiqueta combinada: MVP con dependencia bloqueante. |
| F9 | Consulta de historial de atleta y de dupla según permisos | MVP | 1, 5, 9 | Alta | Corona el recorrido vertical; requiere F3, F5, F6, F8. |
| F10 | Aislamiento de datos por club (club_id en servidor) | MVP (propuesta A3, no aprobada) | 9 | Alta | Sin esto, los permisos por rol no son suficientes. Marcar como Pendiente de aprobación explícita. |
| F11 | Cálculo de ranking RNVP (puntos, negativos, penalizaciones) | FUERA-MVP-FUTURA | 8 | — | El scope lo excluye explícitamente; A1 pregunta si replicarlo o solo indicador interno. |
| F12 | Indicadores de desarrollo derivados (métricas de evolución) | FUERA-MVP-FUTURA (estructura de datos preparada en MVP) | 8, 11 | — | Separar *estructuras* sí (F3, F6); calcular indicadores derivados es fase futura. |
| F13 | Gestión de altas/licencias federativas, autorizaciones RFEVB (72 h), cambios de club con límite (1/temporada), control de doble licencia | FUERA-MVP-FUTURA | 3 | — | Requiere integración/interfaz con federaciones, plazos y régimen sancionador. Alto riesgo operativo y legal si se hace a medias. Inferencia: solo si el usuario confirma ámbito federado. |
| F14 | Importación/sincronización de datos de competición (RFEVB + federaciones autonómicas) | FUERA-MVP-FUTURA | 10 | — | Depende de F13 y de disponibilidad de fuentes oficiales (Pendiente: no se verificó existencia de API). |
| F15 | Pruebas físicas estandarizadas (CMJ, sprint 10 m arena, 5-10-5, 30-15 IFT) con registro de superficie | FUERA-MVP-FUTURA | 7 | — | Baterías validadas según A1, pero añade complejidad de protocolo, superficie y comparabilidad; además pueden implicar datos de salud (RGPD art. 9, A3). |
| F16 | Control de carga/fatiga (s-RPE, ACWR, disponibilidad) | FUERA-MVP-FUTURA | 6 | — | Evidencia científica alta, pero exige consistencia de registro y advertencias de interpretación clínica; el MVP registra asistencia y observaciones, que son insumos futuros. |
| F17 | Consentimiento y control de imágenes/perfiles (subida de fotos, difusión) | FUERA-MVP-FUTURA; si se suben fotos en MVP, solo F7 la cubre | 2 | — | A1 pregunta si habrá difusión de imágenes. Sin esa respuesta, fuera. |
| F18 | Pagos (in/out) | FUERA-MVP-FUTURA hasta aprobación | pregunta abierta A1 | — | Pagos "fuera de operación hasta aprobación" (A3); scope los excluye hasta aprobación explícita. |
| F19 | Calendario y notificaciones (WhatsApp, correo, push) | FUERA-MVP-FUTURA | 4 (parcial), 12 (parcial) | — | Scope los excluye; añade dependencias externas y coste operativo. |
| F20 | Informes complejos y paneles accionables | FUERA-MVP-FUTURA | 11 | — | El MVP cubre "consultar historial" (F9); los informes agregados requieren histórico de datos primero. |
| F21 | Asistencia de IA al entrenador (sugerencias, redacción) | FUERA-MVP-FUTURA | 12 (parcial) | — | Scope: "la IA puede asistir, no sustituir"; IA avanzada excluida hasta aprobación. |
| F22 | ML, deep learning y visión por computador | FUERA-MVP-FUTURA (excluido por principio) | — | — | Exclusión explícita en `volterra-scope.md`. |
| F23 | Exportación de datos del club (backup/retirada) | PENDIENTE-DE-DECISIÓN (recomendación: incluirla en MVP en forma mínima) | 9 (derechos RGPD) | Media | Inferencia: la minimización de acceso y el derecho de retirada sugieren exportación básica; no está en el scope ni en A1 explícitamente. |
| F24 | Registro de auditoría de acceso a historiales de menores | PENDIENTE-DE-DECISIÓN | 2, 9 | Media | A3 exige minimización de acceso; A1 señala sanciones a clubes. Inferencia: sin log de acceso, la minimización no es verificable. No aprobado. |

---

## 3. Recorrido vertical del MVP — paso a paso

Nota: "criterios de aceptación" son comprobables funcionalmente; la verificación técnica (cómo se prueba) queda para fases posteriores sin elegir tecnología aquí.

### Paso 1 — Crear club y usuarios
- **Actores:** administrador de plataforma (crea el club); administrador de club (crea usuarios del club); usuario que recibe invitación/alta (Pendiente: ¿flujo de invitación o alta directa? No definido en fuentes).
- **Casos de uso:** crear club; crear usuario; asignar rol (entrenador / atleta / admin de club); desactivar usuario.
- **Reglas de negocio:** un usuario pertenece a un club (o a ninguno); el admin de plataforma es el único que crea clubes; los roles son los del scope (4 roles candidatos), pero los permisos concretos dependen de la matriz pendiente.
- **Excepciones:** asignar rol de admin de club sin ser admin de plataforma; segundo club para un usuario si el modelo es 1 usuario–1 club (Pendiente: modelo multi-club no definido); usuario duplicado por correo/nombre.
- **Dependencias:** F8 (matriz pendiente), F10 (aislamiento por club).
- **Criterios de aceptación:**
  1. Se puede crear un club y, dentro, al menos dos usuarios con roles distintos.
  2. Un usuario sin rol autorizado no puede crear clubes ni asignar roles de administrador.
  3. Dos clubes de prueba no ven los datos del otro en ninguna consulta del sistema (caso de prueba de acceso cruzado).
  4. Toda alta de usuario queda registrada con fecha y actor.

### Paso 2 — Crear atleta y categoría
- **Actores:** administrador de club; entrenador (si la matriz lo permite; hasta entonces Pendiente).
- **Casos de uso:** crear atleta (nombre/alias, club, categoría, ¿menor de edad? y en ese caso datos de tutor); asignar atleta a categoría; reasignar de categoría dejando constancia.
- **Reglas de negocio:** el atleta pertenece a un club; la categoría es obligatoria; si el atleta es menor, se exige el campo de consentimiento (Paso 2b); reasignar de categoría no borra la asignación anterior (historial).
- **Excepciones:** atleta sin categoría; editar datos de un atleta de otro club; menor sin tutor registrado.
- **Dependencias:** Paso 1; F7 (consentimiento).
- **Criterios de aceptación:**
  1. Se puede registrar un atleta con categoría y ver su fecha de alta.
  2. Cambiar la categoría de un atleta conserva la asignación anterior visible.
  3. Un atleta marcado como menor no puede completarse sin el registro de consentimiento (o queda en estado "incompleto/inactivo" — decisión de diseño, Pendiente).
  4. Ningún usuario de otro club puede leer ni editar el atleta.

### Paso 2b — Registro de consentimiento de menores (integrado)
- **Actores:** administrador de club (registra); tutor legal (fuera del sistema en MVP: el admin registra manualmente; consentimiento *activo* del tutor dentro del sistema = fase futura — Inferencia/Pendiente).
- **Reglas:** registrar quién consiente (nombre/rol del tutor), cuándo, y para qué alcance (datos personales / imágenes — imágenes solo si se aprueba F17); menores <14 requieren siempre padre/tutor (LO 3/2018 art. 7); 14-17 el menor salvo norma específica.
- **Criterios de aceptación:**
  1. Para cada atleta menor consta: fecha, tutor/consentiente, alcance del consentimiento y estado (vigente/revocado).
  2. El registro es inmutable: corregir un consentimiento crea un nuevo registro, no sobrescribe el anterior.
  3. Es imposible dar de alta un atleta menor sin consentimiento registrado vigente.

### Paso 3 — Crear sesión
- **Actores:** entrenador; administrador de club.
- **Casos de uso:** crear sesión (fecha, grupo/categoría, tipo, lugar — campo "superficie" opcional, Futuro); asistente/sustituto Pendiente.
- **Reglas:** una sesión pertenece al club; se crea con antelación o a posteriori (Pendiente: ¿sesiones retroactivas?); cerrar una sesión habilita el registro de asistencia.
- **Excepciones:** sesión duplicada (misma fecha/grupo); sesión en club ajeno; editar una sesión cerrada.
- **Dependencias:** Paso 1; Paso 2.
- **Criterios de aceptación:**
  1. Se puede crear una sesión futura asociada a una categoría y verla en la lista del club.
  2. Una sesión cerrada no admite cambios estructurales (fecha/grupo), solo correcciones trazables (Inferencia mínima).
  3. El sistema impide crear sesiones fuera del club del usuario.

### Paso 4 — Registrar asistencia
- **Actores:** entrenador (principal); admin de club.
- **Casos de uso:** marcar presente/ausente/justificado por atleta y sesión; corregir marcado antes de cerrar.
- **Reglas:** la asistencia se registra por sesión y atleta; el estado inicial de un atleta inscrito es "sin registrar" (distinguir de ausente); toda corrección queda con fecha y autor.
- **Excepciones:** registrar asistencia tras cerrar la sesión; atleta de otra categoría no inscrito en la sesión.
- **Dependencias:** Paso 3.
- **Criterios de aceptación:**
  1. Se puede registrar la asistencia de todos los atletas de la categoría en una sesión y guardarla.
  2. Una sesión en curso muestra quiénes están "sin registrar".
  3. Cada cambio de estado posterior al primer guardado conserva el estado anterior y el autor (auditoría básica).
  4. Solo personal autorizado (entrenador/admin del club) puede registrar o corregir.

### Paso 5 — Guardar observación/evaluación
- **Actores:** entrenador.
- **Casos de uso:** añadir observación de texto libre por atleta en una sesión; puntuar con escala simple (Pendiente: definir escala; A1 no estandariza una; inventarla sería inventar requisito — se propone como Pendiente).
- **Reglas:** la observación está ligada a atleta + sesión; es visible según permisos (atleta ve las suyas — Pendiente de matriz); correcciones crean versión nueva o se marcan como editadas (Pendiente: política de edición).
- **Excepciones:** observación sobre atleta de otro club; borrar observaciones históricas.
- **Dependencias:** Paso 3, Paso 4, F8.
- **Criterios de aceptación:**
  1. Se puede guardar una observación de texto para un atleta en una sesión concreta y recuperarla igual.
  2. El autor y la fecha constan en toda observación.
  3. Una observación de un club no es visible ni editable desde otro club.
  4. El borrado físico de observaciones no está disponible (se archiva o se marca; Inferencia mínima alineada con inmutabilidad del scope).

### Paso 6 — Consultar historial según permisos
- **Actores:** atleta (suyo), entrenador (de sus atletas), admin de club (del club), admin de plataforma (según matriz — Pendiente).
- **Casos de uso:** ver historial de sesiones y asistencia de un atleta; ver historial de observaciones; ver periodos de duplas (aunque en MVP solo si se crean duplas; ver ambigüedad A10); filtrar por rango de fechas.
- **Reglas:** la consulta se limita al club del usuario; el historial es inmutable (solo lectura); separar visualmente lo competitivo (vacío en MVP) de lo de desarrollo (asistencia/observaciones).
- **Excepciones:** consulta cruzada de club; atleta intentando ver a otro atleta.
- **Dependencias:** todos los pasos anteriores; F3; F8.
- **Criterios de aceptación:**
  1. Un atleta ve su propio historial de asistencia y observaciones.
  2. Un entrenador ve el historial de los atletas asignados a sus grupos, y no de otros clubes.
  3. Un admin de club ve el historial completo de su club.
  4. Ninguna consulta devuelve datos de otro club (prueba sistemática).
  5. El historial no puede editarse retroactivamente; las correcciones se muestran como tales.

---

## 4. Reglas transversales del MVP

1. **Inmutabilidad del historial (duplas y todo registro histórico).** Hecho verificado (scope, principio 2; A1 problema 1 con confianza alta): cambiar integrantes de una dupla no reescribe el historial; las duplas son periodos con inicio (y fin si se disuelve). Aplicable también a categorías, asistencia y observaciones: corrección = registro nuevo o marcado de edición, nunca sobrescritura silenciosa. *Recomendación A2.*
2. **Consentimiento de menores.** Hecho verificado (A1, LO 3/2018 art. 7): <14 siempre padre/tutor; 14-17 el menor salvo norma específica. Regla MVP: sin consentimiento registrado vigente, no hay alta de atleta menor ni acceso a su historial más allá de lo estrictamente operativo. *Hallazgo de fuente + regla propuesta (no aprobada).*
3. **Permisos por rol, mínimos y en servidor.** Scope (principio 4) y A3 (permisos en servidor y datos; matriz PENDIENTE). Regla MVP: por defecto, todo denegado salvo permiso explícito; aislamiento por club_id; la matriz concreta es **dependencia bloqueante** pendiente de aprobación. *Hecho verificado (scope) + Pendiente (matriz).*
4. **Separación ranking vs desarrollo.** A1 problema 8 (confianza alta). Regla MVP: los datos de desarrollo (asistencia, observaciones, historial) se almacenan y consultan por separado de cualquier cálculo de ranking; el MVP **no calcula ranking**. La separación en el MVP es de modelado, no de cálculo. *Inferencia de A2 apoyada en hallazgo A1.*
5. **Aislamiento multi-club.** A3 lo propone; no aprobado. Mientras no se apruebe, los accesos cruzados son criterio de aceptación, pero el alcance "multi-club desde MVP" sigue siendo **pregunta abierta** (también en `stack-evaluation.md` pregunta 1). *Pendiente.*

---

## 5. Lo que NO entra en el MVP (con motivo)

| Excluido | Motivo |
|---|---|
| Pagos | A3: fuera de operación hasta aprobación; scope: no incluidos hasta aprobación explícita; A1 lo deja como pregunta abierta. |
| Ranking RNVP completo | Scope lo excluye; A1 pregunta si replicarlo o usar indicador interno; riesgo de error de cálculo con consecuencias federativas. |
| Indicadores de desarrollo derivados y paneles | Requieren histórico acumulado primero; F6 ya sienta la base. |
| Notificaciones (WhatsApp, correo, push) | Scope los excluye; integraciones externas y consentimiento de comunicación. |
| Informes complejos | A1 problema 11 es "medio"; sin datos históricos no hay informe que valga. |
| IA avanzada / asistencia IA | Scope: IA asiste, no sustituye; IA avanzada fuera del MVP. |
| ML, deep learning, visión por computador | Exclusión explícita por principio en el scope. |
| Imágenes, perfiles públicos, subida de fotos | A1 lo deja como pregunta abierta; A3: privacidad por defecto; riesgo sancionador AEPD por imágenes de menores. |
| Altas/licencias federativas, autorizaciones RFEVB | A1 problema 3 (alto), pero requiere plazos legales (72 h), integración federativa y régimen sancionador; hacerlo a medias es más peligroso que no hacerlo. Futuro, tras confirmar ámbito federado. |
| Sincronización con RFEVB/FFAA | Depende de lo anterior y de disponibilidad de fuentes (no verificada). |
| Baterías de pruebas físicas | A1 problema 7; añaden protocolo, superficie, comparabilidad y posible dato de salud (RGPD art. 9). Futuro. |
| Control de carga/fatiga (s-RPE, ACWR) | A1 problema 6 con buena base científica, pero exige disciplina de registro y advertencias de interpretación; el MVP ya registra asistencia y observaciones como insumo. |
| Calendario avanzado | Scope lo lista como dominio futuro. |
| Exportación masiva / informes externos | PENDIENTE (recomendación A2: considerar exportación básica por derechos RGPD; ver F23). |

---

## 6. Ambigüedades detectadas (señalar, no resolver)

- **A1. ¿Ámbito federado, no federado o ambos?** Condiciona F13, F14 y la utilidad del ranking RNVP. No decidir sin el usuario.
- **A2. ¿Atletas menores de 14 años en el alcance?** Si no, F7 se simplifica; si sí, se necesita el flujo de tutor dentro del sistema.
- **A3. ¿Habrá imágenes/perfiles o difusión?** Sin respuesta, F17 queda fuera.
- **A4. ¿Replicar el ranking federativo oficial o solo indicador interno?** Cambia el alcance de F11 y de la separación ranking/desarrollo.
- **A5. ¿Multi-club desde el MVP?** `stack-evaluation.md` lo lista como pregunta; A3 propone aislamiento por club_id; el volumen inicial es desconocido.
- **A6. Matriz de permisos por rol no aprobada** (A3). Dependencia bloqueante de F1, F5, F6, F9.
- **A7. Escala de evaluación del entrenador** no definida en ninguna fuente; proponer una sería inventar requisito → Pendiente.
- **A8. Modelo de pertenencia de usuarios:** ¿un usuario puede pertenecer a varios clubes? (entrenador en dos clubes, atleta que cambia).
- **A9. ¿Registro retroactivo de sesiones?** Afecta a la regla de inmutabilidad.
- **A10. Sesiones de duplas vs sesiones de categoría:** el recorrido vertical trabaja por categoría/grupo; las duplas (F3) tienen su propia vida. **Recomendación A2:** en MVP, modelar y consultar periodos de dupla, sin crearlos como flujo activo (inferencia; Pendiente).
- **A11. Evidencia normativa basada en extractos** (A1): los requisitos legales del MVP deben revalidarse contra los PDFs íntegros antes de considerarlos Hecho verificado.
- **A12. Sin entrevistas a clubes/entrenadores** (A1): la priorización de F4-F6-F9 como "corazón del MVP" es una inferencia del scope, no evidencia de demanda validada.

---

## 7. Criterios de aceptación de la fase A2

1. Todo ítem del inventario (§2) tiene etiqueta MVP / FUERA-MVP / PENDIENTE y justificación trazable a A1, al scope o a A3, sin requisitos inventados sin marcar.
2. El recorrido vertical completo (6 pasos) tiene criterios de aceptación verificables sin referencias a tecnología.
3. No se ha seleccionado ni recomendado stack, proveedor ni herramienta.
4. Las 12 ambigüedades de la §6 están listadas y ninguna está "resuelta" sin decisión del usuario.
5. Los requisitos legales citados están marcados como Hallazgo de fuente (extractos), no como Hecho verificado.
6. Todo lo propuesto por A3 aparece como "propuesta, no aprobada".
7. La separación ranking/desarrollo y la inmutabilidad del historial aparecen como reglas transversales explícitas.
8. Ninguna funcionalidad de la tabla de exclusión se ha colado en el MVP por "ser fácil".

---

## 8. Preguntas que requieren decisión del usuario

1. **Ámbito:** ¿solo clubes no federados, también afiliados a RFEVB/FFAA, o ambos?
2. **Ranking:** ¿replicar el ranking federativo RNVP o solo indicadores internos de desarrollo?
3. **Menores <14:** ¿entran en el alcance? Si sí, ¿el tutor opera en el sistema o solo se registra su consentimiento manualmente?
4. **Imágenes/perfiles:** ¿habrá subida o difusión de imágenes?
5. **Multi-club:** ¿el MVP es multi-club con aislamiento por club_id o un club por despliegue?
6. **Matriz de permisos:** ¿se aprueba la matriz por rol antes de arrancar F1?
7. **Pagos:** ¿se confirman fuera del MVP (recomendación A2) o se quiere lectura de estado de pago?
8. **Duplas en MVP:** ¿solo modelar historial de duplas o también crearlas/editarlas como flujo desde el día 1?
9. **Volumen inicial:** ¿cuántos clubes y atletas se esperan en los primeros meses?
10. **Exportación de datos:** ¿se exige exportación básica en el MVP por derechos RGPD? (F23)
11. **Auditoría de accesos:** ¿se registra quién consulta historiales de menores desde el MVP? (F24)
12. **Revalidación normativa:** ¿se pide al researcher leer los PDFs íntegros de LO 3/2018 y normas RFEVB antes de aprobar requisitos legales del MVP?

---

**Cierre:** FASE 1/A2 completada sin escritura de archivos ni selección de stack. MVP propuesto: operativa diaria de club + historial inmutable + consentimiento de menores + permisos mínimos; **4 dependencias bloqueantes** por aprobar (matriz de permisos, aislamiento multi-club, alcance federado, alcance de menores <14). Siguiente paso: que el usuario responda las preguntas de la §8, especialmente 1, 2, 5 y 6.
