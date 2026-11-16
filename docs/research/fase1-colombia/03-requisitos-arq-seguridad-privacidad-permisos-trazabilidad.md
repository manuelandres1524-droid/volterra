# FASE 1 (Colombia) — 03: Requisitos de arquitectura, seguridad, privacidad, permisos y trazabilidad

**Área:** A3 · **Estado:** propuesta — no aprobada · **Fecha:** 21/10/2026.
**Jurisdicción:** Colombia (Ley 1581 de 2012, D. 1074 de 2015, Ley 1098 de 2006, SIC). Modo solo lectura; sin código, instalaciones ni tecnología seleccionada.

> Reemplaza la jurisdicción española de `docs/research/fase1/03-requisitos-….md`. OWASP (no jurisdiccional) se conserva. Cada requisito indica: **[J]** requisito jurídico confirmado (texto íntegro), **[H]** hallazgo de fuente (extracto), **[R]** recomendación de diseño, **[I]** inferencia, **[A]** requiere asesoría jurídica.

---

## 1. Marco jurídico aplicable (verificación declarada por fila — 21/10/2026)

| Norma | Fuente | Verificación |
|---|---|---|
| **Ley 1581 de 2012** (protección de datos personales) | C-01, Secretaría del Senado | ✅ Arts. 1–29 leídos |
| **Ley 1098 de 2006** (Código de Infancia y Adolescencia) | C-02 | ✅ Íntegro (arts. 1, 33, 47.8, 153 verificados) |
| **D. 1074 de 2015**, Cap. 25 (reglamenta Ley 1581) | C-03 (URL 3, Cancillería) | ✅ Arts. 2.2.2.25.2.1–.9 leídos 21/10/2026 vía texto del D. 1377 con mapa oficial de compilación · resto del Cap. 25 = [H] (salvedad art. 3.1.1) |
| **Deberes y derechos** | Ley 1581 arts. 8, 14, 15, 16, 17 | ✅ |
| **Menores (NNA)** | Ley 1581 art. 7; D. 1074 art. 2.2.2.25.2.9 | ✅ (ambos; D. 1074 vía C-03-3, salvedad art. 3.1.1) |
| **Titulares mayores** | Ley 1581 arts. 8, 9, 12, 17 (autorización propia) | ✅ |
| **Datos sensibles** | Ley 1581 arts. 5, 6; D. 1074 art. 2.2.2.25.2.3 | ✅ (ambos; D. 1074 vía C-03-3, salvedad art. 3.1.1) |
| **Sanciones** | Ley 1581 arts. 23–24 (hasta 2.000 SMMLV) | ✅ |
| **Autoridad** | SIC — Delegatura para la Protección de Datos Personales (arts. 19, 21) | ✅ |
| **Transferencias internacionales** | Ley 1581 art. 26 | ✅ |
| **RNBD** | Ley 1581 art. 25; D. 090 de 2018 (>100.000 UVT) | [H] umbral no leído íntegro |

**Diferencias clave vs. España (evitar trasponer):** no hay RGPD/LOPDGDD/AEPD; no hay "interés legítimo" como base; no hay umbral 14/16 años (en Colombia **todo <18 = NNA**); no hay DPIA/DPO equivalentes; plazos propios (10/15 días hábiles); sanción hasta 2.000 SMMLV.

---

## 2. Requisitos propuestos

### (a) Arquitectura y separación multi-club

| ID | Requisito | Clas. | Prioridad |
|---|---|---|---|
| A-01 | Todo registro de dominio lleva `club_id` y **cada consulta lo filtra**; prueba automatizada de que el club X no lee/escribe club Y. | [R] | Alta |
| A-02 | Historial de duplas y resultados **inmutable**: cambios de integrante cierran periodo; correcciones dejan rastro quién/cuándo/por qué. | [R] | Alta |
| A-03 | Autorización evaluada en **servidor y capa de datos** para toda operación; la UI no es barrera. | [R] | Alta |
| A-04 | Separación explícita **ranking competitivo** (no oficial salvo acuerdo FVCV) vs. **indicadores de desarrollo**; reglas versionadas. | [R] | Media |
| A-05 | Entornos separados; no productivo con **datos ficticios** (nunca NNA reales sin autorización). | [R] | Alta |
| A-06 | Documentar modelo responsable/encargado **antes** de operar; análisis depende del modelo contractual (club cliente vs. SaaS). | [A] | Alta |

### (b) Privacidad (Ley 1581) — el corazón del MVP

| ID | Requisito | Clas. | Prioridad |
|---|---|---|---|
| P-01 | **NNA (<18):** tratamiento prohibido salvo datos de naturaleza pública; con autorización del **representante legal**, previo ejercicio del **derecho del menor a ser escuchado** (madurez/autonomía), respetando interés superior y derechos fundamentales. | **[J]** Ley 1581 art. 7 · **[J]** D. 1074 art. 2.2.2.25.2.9 (texto leído 21/10/2026 vía compilación D. 1377→D. 1074, C-03-3; salvedad art. 3.1.1) | Crítica |
| P-02 | **Prueba de autorización conservable:** alta de NNA registra quién autorizó, identidad del representante, finalidad, fecha y prueba (escrita/oral/conducta inequívoca documentada); **el silencio nunca es autorización**. | **[J]** arts. 9, 17.b · **[J]** 2.2.2.25.2.4/.5 (leídos vía C-03-3; salvedad art. 3.1.1) | Crítica |
| P-03 | Informar el **carácter facultativo** de responder sobre datos sensibles o de NNA (formulario de alta). | **[J]** art. 12.b | Alta |
| P-04 | **Datos sensibles** (incluye salud — art. 5): autorización expresa aparte, informando cuáles y para qué; **ninguna actividad condicionada** a suministrar sensibles. | **[J]** arts. 5–6 · **[J]** 2.2.2.25.2.3 (leído vía C-03-3; salvedad art. 3.1.1) | Alta |
| P-05 | **Autorización por finalidad** (datos vs. imágenes/difusión/marketing). Los precedentes SIC ordenaron eliminar imágenes de menores sin autorización de representantes. | [H]+[A] Res. SIC 21-349477/2022, 57093/2020 | Alta |
| P-06 | **Derechos ARCO-P** operativos: conocer/actualizar/rectificar, prueba de autorización, ser informado del uso, queja ante SIC, revocación/supresión; atención **consulta ≤10 días hábiles** (+5), **reclamo ≤15 días hábiles** (+8), requisito de procedibilidad. | **[J]** arts. 8, 14, 15, 16 | Alta |
| P-07 | **Deberes del responsable** (art. 17): informar finalidad, seguridad, actualización, rectificación, **manual interno de políticas y procedimientos**, tramitar consultas/reclamos. Sobre comunicación de violaciones a la autoridad: ver S-11 (literal exacto por verificar — **[H]+[A]**, no afirmado como [J]). | **[J]** art. 17 (parcial) · notificación de brechas = [H]+[A] | Alta |
| P-08 | **Transferencias internacionales** (cloud fuera de Colombia): verificar excepciones del art. 26 (autorización expresa, ejecución de contrato) antes de elegir proveedor. | **[J]** art. 26 + [A] | Alta (bloqueante de decisión de hosting) |
| P-09 | **RNBD:** evaluar si VOLTERRA queda obligada al registro (>100.000 UVT según [H] D. 090/2018); decisión pendiente. | [H]+[A] | Media |
| P-10 | **Imagen de NNA:** no hay ley especial de derecho de imagen; el uso se rige por Ley 1581 (imagen = dato personal) + Constitución art. 15 (no leído en esta sesión) + Ley 1098 art. 33 (intimidad). **No afirmar equivalencias europeas.** | [H]+[A] | Alta |
| P-11 | **Conservación limitada** por tipo de dato (historial vs. contacto vs. credenciales vs. bitácora); plazos documentados y comunicados. | [R] | Alta |
| P-12 | EIPD/DPIA **no es figura colombiana**; si se quiere análisis de riesgos, hacerlo como **buena práctica**, no como obligación legal. | [I] | Baja |
| P-13 | **Titulares mayores de edad:** recolección y tratamiento con **autorización previa y expresa del propio titular** (art. 9) salvo excepciones de la ley; informar finalidad, facultatividad y mecanismos de derechos (arts. 12, 17); ejercicio directo de ARCO-P (art. 8). **No extender por analogía el régimen de NNA a mayores (ni a la inversa).** | **[J]** arts. 8, 9, 12, 17 · **[A]** alcance de las excepciones del art. 9 | Alta |

### (c) Seguridad (OWASP — no depende de jurisdicción)

| ID | Requisito | Clas. | Prioridad |
|---|---|---|---|
| S-01 | Adoptar nivel ASVS (recomendado evaluar L2) citando versión `v5.0.0-x.y.z`; matriz requisito→estado. | [R] | Alta |
| S-02 | Autorización por objeto en cada endpoint (API1:2023 BOLA) con pruebas negativas. | [R] | Alta |
| S-03 | Separación funciones plataforma/club/usuario (API5:2023). | [R] | Alta |
| S-04 | Sin asignación masiva de campos (API3:2023). | [R] | Alta |
| S-05 | Autenticación robusta; sin secretos en frontend ni en prompts/logs de agentes. | [R] | Alta |
| S-06 | Límites de recursos y antiabuso (API4/API6:2023) — relevante si se retoman pagos. | [R] | Media |
| S-07 | Inventario de endpoints (API9:2023); validación de entrada; manejo de errores; comunicación segura. | [R] | Media |
| S-08 | Cifrado en tránsito y en reposo de datos personales (decisión técnica pendiente de stack). | [R] | Alta |
| S-09 | Permisos OpenCode para agentes de desarrollo: restringir con `permission` (v1) o esquema v2; **por defecto OpenCode permite todo** — la restricción debe configurarse explícitamente. | [H] docs OpenCode | Alta |
| S-10 | La config de OpenCode **no** sustituye permisos de SO, app ni base de datos. | [H] | Alta |
| S-11 | Respuesta a incidentes: runbook con roles y plazos. Comunicación de violaciones a la **SIC**: **[H]+[A]** — la lectura del art. 17 no identificó literal expreso de notificación de brechas; **verificar el literal y los plazos con asesoría** antes de fijarlo como obligación. | [H]+[A] | Alta |

### (d) Permisos por rol — matriz propuesta (NO aprobada)

> Derivada de `volterra-scope.md` + principio mínimo privilegio + Ley 1581. **Requiere aprobación humana.** L.: lectura · C.: crear/editar en su club · ⚠: requiere autorización/decisión · —: denegado.

| Operación | Plataforma | Admin club | Entrenador | Atleta | Tutor (representante) |
|---|---|---|---|---|---|
| Gestionar club/usuarios | C./L. (todos) | C./L. (su club) | — | — | — |
| Atleta menor: ficha y autorización | L. | C./L. | L. (su club) | — | **Gestiona/autoriza (el propio)** |
| Atleta mayor: ficha | L. | L. | L. | L. (propia) | — |
| Duplas/periodos | L. | C./L. | C./L. | L. (propio) | L. (del hijo) |
| Entrenamientos/asistencia | L. | C./L. | C./L. | L. (propio) | L. (del hijo) |
| Observaciones | L. | L. | C./L. | L. (propio) ⚠ | ⚠ decidir visibilidad |
| Pruebas físicas (futuro) | — | ⚠ si dato sensible | ⚠ | L. (propio) ⚠ | ⚠ autorización expresa |
| Imágenes (futuro) | — | ⚠ autorización por finalidad | — | — | **Autoriza explícitamente** |
| Resultados | L. | C./L. | C./L. | L. | L. |
| Ranking club (no oficial) | L. | L. | L. | L. | — |
| Bitácora auditoría | L. | L. (su club) | — | — | — |
| Exportación/rectificación (ARCO-P) | Procesa | Ejecuta | — | Solicita (mayor) | Solicita (menor) |

Regla: **todo por defecto denegado salvo permiso explícito**; autorización evaluada en servidor y datos (A-01, A-03).

### (e) Trazabilidad

| ID | Requisito | Clas. | Prioridad |
|---|---|---|---|
| T-01 | Bitácora inmutable de acciones sensibles sobre datos personales (crear/modificar/eliminar/exportar/cambiar permisos/cambiar autorización), con **énfasis prioritario en datos de NNA** y cobertura de todos los usuarios. | [R] | Alta |
| T-02 | Registro de decisiones (formato `governance-charter.md`); gobernanza transversal (decisión confirmada del usuario). | [H] interno | Alta |
| T-03 | Registro de fuentes con título/entidad/URL/fecha/afirmaciones/limitaciones (formato sección 1 de 05-bitacora). | [H] interno | Media |
| T-04 | Acciones de agentes IA sobre datos reales → registro + revisión/aprobación humana. | [R] | Alta |
| T-05 | Cada métrica/ranking traza a su fuente y versión de regla. | [R] | Media |
| T-06 | Cambios de esquema, reglas de ranking, permisos y retención pasan por gobernanza. | [H] interno | Alta |

### (f) Operación

| ID | Requisito | Clas. | Prioridad |
|---|---|---|---|
| O-01 | Runbook de incidentes de seguridad con evaluación y comunicación a la **SIC** (literal y plazos a confirmar con asesoría — ver E-10; coherente con S-11). | [H]+[A] | Alta |
| O-02 | Evaluación de riesgos documentada (buena práctica; no DPIA legal). | [R] | Media |
| O-03 | Respaldos cifrados con **pruebas de restauración**. | [R] | Alta |
| O-04 | Canal de corrección de datos con trazabilidad. | [R] | Media |
| O-05 | Revisión periódica: permisos, accesos de agentes, autorizaciones, retención, inventario API, estado ASVS. | [R] | Media |
| O-06 | Pagos fuera de operación hasta aprobación explícita. | [H] decisión interna | Alta |

---

## 3. Riesgos (revisados para Colombia)

| ID | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| R-01 | Tratar datos de NNA **sin autorización del representante** → tratamiento prohibido (art. 7) + sanciones SIC + precedentes de orden de eliminar imágenes. | Muy alto | P-01/P-02/P-05; alta bloqueada sin autorización |
| R-02 | Usar una autorización genérica para todas las finalidades (datos + imágenes + marketing). | Alto | P-05; autorización por finalidad (confirmar E-2) |
| R-03 | Accesos indebidos entre clubes o dentro del club (BOLA/BFLA). | Alto | A-01/A-03/S-02/S-03 |
| R-04 | Reescritura de historial de duplas/resultados. | Alto | A-02, T-01 |
| R-05 | Transferencia internacional (cloud EEUU/UE) sin evaluar art. 26. | Alto | P-08 antes de elegir hosting |
| R-06 | Registrar datos de salud (lesiones, pruebas) sin tratarlos como sensibles (arts. 5–6). | Muy alto | P-04; F15/F16 solo futuro con autorización expresa |
| R-07 | Confundir ranking del club con ranking federativo oficial. | Medio | A-04; etiqueta "no oficial" |
| R-08 | Configuración por defecto expuesta (perfiles públicos o datos visibles sin quererlo — con énfasis en menores). | Alto | P-04 + privacidad por defecto de **todos los usuarios** (datos mínimos; nada público sin decisión explícita) |
| R-09 | Copiar plazos europeos (30 días RGPD) u obligaciones DPIA/DPO que no existen en Colombia (o viceversa: omitir 10/15 días hábiles SIC). | Medio | P-06; este documento |
| R-10 | Asignar rol de "oficial de datos" pensando en DPD europeo: no es figura legal colombiana equivalente. | Medio | P-09/P-12; [A] |
| R-11 | Persona no autorizada se presenta como tutor/representante legal y obtiene acceso a ficha, historial o imágenes de un menor. | Alto | Verificación de identidad y vínculo con el atleta antes de activar el rol tutor; pruebas negativas; revisión periódica de tutores (O-05) |

---

## 4. Preguntas que requieren asesoría jurídica colombiana (prioridad P1)

1. **E-1:** ¿Resultados deportivos de menores (nombre, club, puesto) califican como "datos de naturaleza pública" (art. 7 / 2.2.2.25.2.9) o requieren autorización en todo caso?
2. **E-2:** ¿Una sola autorización cubre fotos/videos/resultados/marketing o exige autorizaciones separadas por finalidad?
3. **E-3:** Datos de salud de menores: ¿autorización expresa adicional y manejo reforzado? ¿Se articula con federaciones/seguros?
4. **E-4:** Conservación: ¿hasta cuándo retener historiales de menores tras dar de baja?
5. **E-5:** ¿VOLTERRA queda obligada al RNBD? Plazos y régimen vigentes.
6. **E-6:** Cloud fuera de Colombia: ¿excepción del art. 26 aplicable o declaración de conformidad?
7. **E-7:** ¿Es válida autorización electrónica en app para NNA y cómo se acredita la prueba?
8. **E-8:** Alcance del "derecho a ser escuchado" del menor en el alta según madurez.
9. **E-9:** ¿Desde cuándo se espera manual interno (art. 17.k) u oficina de cumplimiento según tamaño?
10. **E-10:** ¿Existe literal expreso en el art. 17 (u otra norma colombiana) que obligue a comunicar violaciones de seguridad a la SIC? Si existe, ¿qué plazo? (S-11 rebajado a [H]+[A] hasta verificar).

**Decisiones del usuario (no jurídicas):** aprobación de matriz de permisos (d), política de visibilidad de datos de menores, presupuesto, hosting/región (tras E-6), alcance federado (tras Q-10).

---

## Cierre

- **Resumen:** 30+ requisitos reclasificados para Colombia con evidencia [J]/[H]/[R]/[I]/[A] (incl. **P-13** para titulares mayores de edad); matriz de permisos propuesta; 11 riesgos (R-01…R-11, incl. verificación de identidad del tutor); 10 preguntas de asesoría (E-1…E-10).
- **Archivos modificados durante la investigación:** ninguno (los documentos de esta carpeta se crean por encargo aprobado).
- **Pruebas/ejecución:** consultas web 21/10/2026 documentadas en bitácora (Ley 1581 y 1098 íntegras; D. 1377 con mapa oficial de compilación al D. 1074 — arts. 2.2.2.25.2.1–.9 leídos vía C-03-3, salvedad art. 3.1.1); sin código.
- **Riesgos:** R-01…R-11.
- **Decisiones pendientes:** DEC-01…DEC-20 (05-bitacora) + E-1…E-10 asesoría.
- **Siguiente paso:** respuestas E-1…E-10 con abogado colombiano; aprobación de matriz de permisos y política de menores.
