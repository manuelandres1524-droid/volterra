# FASE 1 — A1: Problemas principales que VOLTERRA debe resolver

> **SUPERADO — este no es el corpus vigente.** Investigación original de FASE 1 para **España/UE** (20/10/2026). El corpus vigente es **[`../fase1-colombia/`](../fase1-colombia/)** (Colombia, 21/10/2026), que sustituye la jurisdicción, las fuentes, los plazos y las decisiones. Este documento se conserva íntegro por trazabilidad histórica: **no usar sus requisitos, plazos ni base jurídica como vigentes**. Índice y alcance: [`README.md`](README.md).

**Área:** A1 · **Agente responsable:** `researcher` (+apoyo de `product-analyst`).
**Estado:** propuesta — no aprobada. **Fecha de consulta de todas las fuentes:** 20/10/2026.
**Modo:** solo lectura. No se creó, modificó ni borró ningún archivo durante la investigación; no se escribió código.

---

## 1. Pregunta investigada

¿Cuáles son los problemas principales, verificables con fuentes reales, que una plataforma debe resolver para clubes y entrenadores de voleibol de playa en España/UE (con menores de edad entre los atletas), dentro del alcance y principios definidos en `product/volterra-scope.md` y clasificados según `governance/research-evidence-standard.md`?

---

## 2. Resumen ejecutivo

1. La normativa federativa española confirma que el voleibol de playa se organiza sobre **duplas ("Parejas") con identidad propia**: la Liga Nacional exige presentar tres parejas por equipo y su composición se determina por la **suma de puntos de ranking de cada jugador**, y la normativa de Copa establece literalmente que **los cambios de pareja obligan a recalcular los puntos de ranking** (Hallazgo de fuente, norma primaria).
2. El historial no es cosmético: la temporada de vóley playa va del **15 de septiembre al 14 de septiembre**, las licencias se tramitan **necesariamente a través de un club**, y solo se puede cambiar de club una vez por temporada salvo en la LNVP (Hallazgo de fuente, norma primaria). Esto exige conservar periodos de asociación sin reescribir el pasado.
3. Los requisitos administrativos son densos y con plazos: licencia de la Federación Autonómica **más** Autorización Federativa de la RFEVB, con antelación mínima de 72 h, más inscripción por intranet/boletín (Hallazgo de fuente).
4. Con menores de edad, el régimen de consentimiento es estricto (**<14 años: consentimiento de padres/tutores; 14–18: el propio menor salvo norma específica**) y la AEPD sanciona a clubes por publicar imágenes sin consentimiento válido; la propia AEPD ha **propuesto** subir la edad de consentimiento a 16 años (propuesta, no aprobada) (Hecho verificado + Pendiente).
5. En el plano científico, el monitoreo de carga con **s-RPE** está validado para voleibol de playa (élite y amateur) y hay evidencia de que sobrecarga mal gestionada eleva el riesgo de lesión; las lesiones por sobrecarga (lumbar, rodilla, hombro) son prevalentes aunque las lesiones "con pérdida de tiempo" sean bajas (Hallazgo de fuente, revisada por pares).
6. La evidencia sobre **adopción digital real en clubes amateurs españoles de vóley playa es escasa**: existe evidencia académica de adopción modesta en organizaciones deportivas y de subdesarrollo digital en el deporte de base, y existen proveedores que comercializan exactamente el problema que VOLTERRA plantea, pero esto último es marketing, no prueba de prevalencia.
7. **No se encontró** literatura específica sobre gestión de clubes españoles de voleibol de playa, ni testimonios primarios de entrenadores españoles: es el vacío de evidencia más relevante del informe.

---

## 3. Problemas identificados y PRIORIZADOS (12)

| # | Problema | A quién afecta | Impacto | Evidencia disponible | Confianza |
|---|---|---|---|---|---|
| **1** | **Historial de duplas con periodos de asociación, sin reescribir el historial al cambiar integrantes** | Club, atleta, entrenador | Alto | Norma: composición de parejas por suma de puntos RNVP; "los cambios de pareja supondrán recalcular los puntos de ranking" (Normas Copa de España VP 2025). Reglas FIVB: 2 jugadores y **no hay sustituciones** en partido → la dupla es la unidad de competición. Estudio 5C's sobre partnership exitoso en VP élite (Poczwardowski 2020) | **Alto** en que el dato histórico importa normativamente; **medio** en la frecuencia del problema en clubes concretos |
| **2** | **Protección de datos de menores: consentimiento <14 / 14–18, imágenes, verificación y registro de consentimientos** | Club, atleta (menor), entrenador | Alto (régimen sancionador) | LO 3/2018 art. 7 (BOE-A-2018-16673); infografía AEPD 14/12/2020; resolución AEPD E-04969-2020; Memorias AEPD 2023 y 2024; expediente PS/00494/2023 (vía fuente secundaria) | **Alto** (norma y resolución primarias) |
| **3** | **Altas, licencias, autorizaciones federativas y cambios de club con plazos y límites** | Club, atleta | Alto (burocrático y bloqueante) | Normas Generales Competición VP 2026; Reglamento General RFEVB (ed. 10-10-2025); Reglamento Disciplinario art. 25 (inhabilitación 2-3 años por doble licencia); Acta Asamblea RFEVB 06/04/2025 (art. 115) | **Alto** (norma primaria) |
| **4** | **Fragmentación de la operativa diaria: planificación, asistencia y comunicación en soportes dispersos** | Club, entrenador | Alto (pérdida de información, trabajo duplicado) | Evidencia académica: transformación digital "significativamente subdesarrollada" en deporte de base (PMC12406710, 2025); cambio digital predominantemente a pequeña escala en organizaciones deportivas sin ánimo de lucro (Sport Management Review 2024); encuesta SafeSport 2025 (entrenadores piden herramientas de planificación y desarrollo de club) | **Medio** (evidencia indirecta, no específica de vóley playa español) |
| **5** | **Registro de sesiones de entrenamiento, asistencia y observaciones del entrenador** | Entrenador, atleta | Alto (es el recorrido vertical candidato del scope) | Encuesta internacional de entrenadores (Sports Medicine Open 2023): 71% se describe como planificador "periodizado", 96% evalúa necesidades al inicio de temporada → hay proceso de planificación que hoy se documenta de forma heterogénea | **Medio-bajo** (la existencia de planificación es Hecho; el "problema de registro" es Inferencia, no hay dato directo) |
| **6** | **Control de carga, fatiga y disponibilidad para reducir riesgo de lesión/solescenimiento** | Entrenador, atleta | Alto | Bozzini 2021 (J Strength Cond Res): cargas internas/externas en VP universitaria; Oliveira 2018 (Motriz, citada 43 veces): s-RPE en 10 semanas con equipo olímpico; Timoteo 2024/2025 (Sports Health): ACWR elevado ↔ mayor riesgo de lesión (OR ≈ 2); estudio FIVB de lesiones 2003: sobrecarga lumbar 19%, rodilla 12%, hombro 10% | **Alto** en respaldo científico; **medio-bajo** en que los clubes amateurs lo estén pidiendo |
| **7** | **Pruebas físicas y evolución individual comparable** | Entrenador, atleta | Medio-alto | Volleyball Canada: batería de protocolos de VP (CMJ/SJ, salto con carrera, sprint 10 m en arena, agilidad 5-10-5, 30-15 IFT); Bishop 2003 (PMID 14767400): salto en arena más bajo que en piso pero muy correlacionado (r = 0,93); Sattler 2012 (PMID 21904238): fiabilidad de tests de salto | **Alto** en que existen baterías validadas; **medio** en su uso real en clubes |
| **8** | **Ranking: separar el ranking competitivo de los indicadores de desarrollo** | Club, atleta, entrenador | Alto (malentendidos de "progreso") | RNVP: puntuación **individual**, factores multiplicadores por competición, penalizaciones de −1.000 puntos y posibilidad de **puntos negativos** (Normas C. España Senior 2025); Ranking "página web dinámica alimentada desde la intranet de la RFEVB" + aportación de FFAA | **Alto** en el diseño del RNVP; **medio** en la confusión ranking/progreso (Inferencia) |
| **9** | **Permisos por rol y minimización de acceso a historiales (incluidos menores)** | Club, entrenador, atleta | Alto | Scope VOLTERRA ("permisos en servidor y datos"); LO 3/2018 menciona el tratamiento de menores por federaciones como supuesto de especial consideración; RGPD art. 7.1 (prueba del consentimiento a cargo del responsable) | **Alto** como obligación; la traducción concreta a roles es **Pendiente** |
| **10** | **Resultados, calendario y datos de competición distribuidos entre RFEVB y federaciones autonómicas** | Club, atleta | Medio-alto | RNVP alimentado por RFEVB (pruebas nacionales/internacionales) **y** por FFAA (torneos homologados); LNVP2: grupos nacionales (gestión RFEVB) y autonómicos (gestión FFAA); inscripciones por boletín/intranet; listas de entrada y plazos de 72 h | **Medio-alto** (norma primaria; la "dificultad" de consolidar datos es Inferencia) |
| **11** | **Informes accionables para club y entrenador (evolución, no solo marcadores)** | Club, entrenador | Medio | Principio de VOLTERRA ("información medible, visual y accionable"); evidencia de que la sobrecarga y las diferencias rol-específicas requieren monitoreo individualizado (revisión PMC10768657, 2024) | **Medio** (Inferencia a partir de 1 y 6) |
| **12** | **Barreras de adopción: tiempo, voluntariado y resistencia del entrenador a lo digital** | Club, entrenador | Alto (si falla, falla el producto) | Estudio COVID boxeo Noruega (2020): uso digital limitado a comunicación/administración; cita de Trabal (2008): entrenadores resisten más la innovación tecnológica que los atletas; Sellitto (2016): falta de pericia; Sport Management Review 2024 | **Medio** (evidencia de práctica, contexto no español ni de vóley playa) |

**Pagos:** quedan **fuera de esta priorización** por decisión de scope ("solo si se aprueban") — clasificado como **Pendiente de decisión del usuario**, no como problema investigado.

---

## 4. Hallazgos con citas y enlaces

### 4.1 Fuentes normativas y oficiales (prioridad según el estándar)

**F1. Reglas oficiales de voleibol de playa FIVB 2025-2028**
- Título: *Official Beach Volleyball Rules 2025-2028* | Organización: FIVB | URL: https://www.fivb.com/wp-content/uploads/2025/02/FIVB-BeachVolleyball_Rules2025_2028-EN-v01.pdf | Publicación: 22/01/2025 (fecha indicada por el buscador); aprobadas por el 39.º Congreso Mundial FIVB 2024, aplicables desde 01/01/2025 | Consulta: 20/10/2026 | Tipo: norma oficial primaria.
- **Clasificación: Hecho verificado** (existencia y vigencia del texto).
- Limitación: **no se descargó el PDF completo**; el extracto procede del buscador.

**F2. Reglas básicas del voleibol de playa (español)**
- Título: *Reglas básicas* | FIVB | URL: https://www.fivb.com/es/voleibol-playa/el-juego/reglas-basicas/ | Sin fecha | Consulta: 20/10/2026 | Tipo: página oficial.
- Cita: *"El voleibol playa es un deporte que juegan dos equipos de dos jugadores… **No hay sustituciones ni reemplazos de jugadores durante un partido**."*
- **Clasificación: Hecho verificado.**

**F3. Reglamento General de la RFEVB**
- Título: *Reglamento General RFEVB* | RFEVB | URL: https://esvoley.es/media/wn4cztod/reglamento-general.pdf | Edición 10-10-2025, ratificado por el CSD el 07/10/2025 | Consulta: 20/10/2026 | Tipo: norma primaria.
- Afirmaciones: art. 38 (jugador = quien firma licencia y queda vinculado a su club); art. 44 (categorías de jugadores); **Título IV: Reglamento de Voley Playa**.
- **Clasificación: Hecho verificado** (contenido del extracto) / **Hallazgo de fuente** para lo no leído.
- Limitación: solo extracto de búsqueda.

**F4. Normas Generales de Competición de Voley Playa — Temporada 2026**
- Título: *VOLEY PLAYA — Normas Generales de Competición Temporada 2026* | RFEVB | URL: https://esvoley.es/media/pqehzgrw/nevp-normas-generales-de-competici%C3%B3n-de-voley-playa-2026.pdf | Fecha del documento: JD 14/03/25; publicado 10/02/2026 | Consulta: 20/10/2026 | Tipo: norma primaria.
- Afirmaciones: inscripción por **Intranet de la RFEVB**; todas las licencias se tramitan **a través de la Federación Autonómica**; la licencia de voley playa es **independiente** de la de voleibol; datos obligatorios del deportista: nombre, apellidos, sexo, fecha de nacimiento, NIF/pasaporte, nacionalidad, federación de origen; para competir hace falta licencia **y** Autorización Federativa de la RFEVB con **antelación mínima de 72 horas**; salvo LNVP, **solo se puede cambiar de club una vez por temporada (máx. 2 altas y 2 bajas)**.
- **Clasificación: Hecho verificado.**
- Limitación: extracto; no se leyó el PDF entero.

**F5. Reglamento Disciplinario de la RFEVB**
- Título: *Reglamento Disciplinario* | RFEVB | URL: https://esvoley.es/media/wmdnzzd2/reglamento-disciplinario.pdf | Edición 13-02-2018 | Consulta: 20/10/2026 | Tipo: norma primaria.
- Cita: *"Artículo 25º Todo jugador que suscribiese licencia por dos o más clubes será sancionado con la inhabilitación de dos a tres años…"*
- **Clasificación: Hecho verificado.**

**F6. Acta de la Asamblea General RFEVB (06/04/2025)**
- Título: *Acta de la XXXVIII Asamblea General* | RFEVB | URL: https://esvoley.es/media/lkjprjrc/2025-1-acta-de-la-asamblea-general-06-04-2025.pdf | Publicación: 06/04/2025 | Consulta: 20/10/2026 | Tipo: acta institucional.
- Cita: modificación aprobada por unanimidad (45 a favor) del art. 115: temporada de vóley playa **del 15 de septiembre al 14 de septiembre**; licencias expedibles durante toda la temporada; *"Las licencias de Vóley Playa deberán ser tramitadas necesariamente a través de un club"*; una persona puede tener licencia de voleibol y de voley playa **simultáneamente, aunque sea por clubes distintos**.
- **Clasificación: Hecho verificado.**

**F7. Normas Liga Nacional de Vóley Playa — Primera División 2025-26**
- Título: *Normas Liga Nacional de Vóley Playa, Primera División, Temp. 2025-2026* | RFEVB | URL: https://www.rfevb.es/Files/Descargas/NEVP%202526%20-%20Normas%20Liga%20Nacional%20de%20V%C3%B3ley%20Playa-pdfEs20250823103434.pdf | Documento JD 14/03/25 | Consulta: 20/10/2026 | Tipo: norma primaria.
- Afirmaciones: cada equipo presenta **tres Parejas (P1, P2, P3)**; cada encuentro son **7 partidos**; la composición de las parejas se determina por la **suma de las puntuaciones individuales de ambos deportistas según el último RNVP publicado**, entregada por escrito al Juez Árbitro; inscripción por boletín LNVP-01; puntos RNVP con factor multiplicador 2 en Liga Regular.
- **Clasificación: Hecho verificado.**

**F8. Normas Liga Nacional de Vóley Playa — Segunda División 2025-26**
- Título: *Normas LNVP Segunda División 2025-26* | RFEVB | URL: http://www.cevp.es/Files/Descargas/NEVP%202526%20-%20%20Normas%20LNVP%20Segunda%20Divisi%C3%B3n-pdfEs20251202013848.pdf | RFEVB: 28/10/2025 | Consulta: 20/10/2026 | Tipo: norma primaria.
- Afirmaciones: hasta dos grupos nacionales y **tantos grupos autonómicos como ligas homologadas organicen las FFAA**; los clubes de FFAA con liga homologada **deben participar en ella**; puntuación RNVP con **factor 0,3** en grupos autonómicos.
- **Clasificación: Hecho verificado.**

**F9. Funcionamiento del RNVP (Reglamento Técnico, Anexo III)**
- Título: *Funcionamiento RNVP* | RFEVB | URL: http://www.cevp.es/RFEVB/Files/vplaya/ranking_nacional/RNVP_asifunciona.pdf | Sin fecha visible | Consulta: 20/10/2026 | Tipo: norma técnica primaria.
- Afirmaciones: tabla de puntos por clasificación (1.º = 100 … hasta 49.º = 0); cuadro especial para pruebas FIVB/CEV (1.º = 128); **factores multiplicadores por categoría de competición** (p. ej. 15 para pruebas 3★ de Circuito Nacional, 10 para Copa de España…).
- **Clasificación: Hecho verificado** (contenido del extracto).

**F10. Normas Copa de España de Vóley Playa 2025**
- Título: *Normas Específicas de Competición — Copa de España de Vóley Playa, Temp. 2025* | RFEVB | URL: https://www.rfevb.es/Files/Descargas/NEVP%20-%20Normas%20COPA%20DE%20ESPA%C3%91A%20DE%20VOLEY%20PLAYA%20-%202025-pdfEs20250312015447.pdf | marzo 2024 | Consulta: 20/10/2026 | Tipo: norma primaria.
- Cita: *"**Los cambios de pareja supondrán recalcular los puntos de ranking** y, en su caso, modificar su ubicación en el cuadro."*
- **Clasificación: Hecho verificado.** — **P1** (el núcleo del diseño de "duplas con periodos").

**F11. Normas Copa del Rey / Copa de la Reina 2025 y Normas Campeonato de España Senior 2025**
- Título: *Normas COPAS REY y REINA 2025* (http://www.cevp.es/Files/Descargas/NEVP%20-%20Normas%20COPAS%20REY%20y%20REINA%20-%202025-pdfEs20250312015206.pdf) y *Normas Campeonato de España Senior 2025* (https://www.rfevb.es/Files/Descargas/NEVP%20-%20Normas%20CAMPEONATO%20DE%20ESPA%C3%91A%20SENIOR%20-%202025-pdfEs20250820124430.pdf) | RFEVB | marzo 2024 / agosto 2025 | Consulta: 20/10/2026 | Tipo: norma primaria.
- Afirmaciones: acceso al torneo **por suma de puntos individuales del RNVP**; penalizaciones de −1.000 puntos por incomparecencia o descalificación; *"Los puntos de ranking de un deportista pueden ser negativos"*.
- **Clasificación: Hecho verificado.** — **P8** (el ranking mide participación/competición, no desarrollo).

**F12. Páginas de ranking RNVP (masculino/femenino)**
- Título: *Ranking Vóley Playa Masculino / Femenino* | RFEVB | URL: https://esvoley.es/voley-playa/ranking-nacional-de-voley-playa-rnvp/ranking-voley-playa-masculino | Sin fecha | Consulta: 20/10/2026 | Tipo: página oficial.
- Cita: *"El Ranking Nacional de Vóley Playa se confecciona mediante una **página web dinámica alimentada desde la intranet de la RFEVB**. La RFEVB introduce… las clasificaciones de las pruebas nacionales e internacionales, mientras que **las FFAA hacen lo propio con los torneos homologados** que organizan."*
- **Clasificación: Hecho verificado.** — **P10** (la autoría de los datos está distribuida).

**F13. Acta de la LXIV Asamblea General RFEVB**
- Título: *LXIV Asamblea General de la RFEVB* | RFEVB | URL: https://esvoley.es/media/j5ngra5m/2026-ag-acta-asamblea-6-junio-definitivo.pdf | Sesión 06/06/2026, publicado 08/09/2026 | Consulta: 20/10/2026 | Tipo: acta institucional.
- Afirmación: se votan y aprueban anualmente las normas de vóley playa (incluidas Normas Generales, LNVP, LNVP2, Copas, Circuito) y propuestas sobre puntos de ranking y plazos de listas de entrada.
- **Clasificación: Hecho verificado.** — la normativa **cambia cada temporada** → los modelos de datos deben tolerar cambios de reglas (Inferencia).

**F14. Federaciones autonómicas y competición autonómica**
- Título: *Federaciones Autonómicas* (https://esvoley.es/federacion/federaciones-autonomicas) y web de la **Federación de Madrid de Voleibol** (https://fmvoley.com/eventos) | RFEVB / FMVB | Consulta: 20/10/2026 | Tipo: sitio oficial.
- Afirmaciones: existen Liga Autonómica de Clubes de Vóley Playa, circuito autonómico, **ranking autonómico**, "jornadas circuitos (inscripción parejas fuera de Madrid)" y reserva de pistas.
- **Clasificación: Hecho verificado** (existencia de la estructura).

### 4.2 Fuentes de protección de datos (España/UE)

**F15. AEPD — Infografía sobre consentimiento de menores**
- Título: *Información sobre consentimiento para tratar datos personales de menores de edad* | AEPD | URL: https://www.aepd.es/infografias/infografia-consentimiento-menores.pdf | 14/12/2020 | Consulta: 20/10/2026 | Tipo: guía oficial del regulador.
- Afirmaciones: consentimiento como base (art. 6.1.a RGPD); información previa (art. 13.1); **prueba del consentimiento a cargo del responsable (art. 7.1 RGPD)**; art. 92 LOPDGDD (interés superior del menor); **"El consentimiento para la utilización de sus datos personales se otorgará por sus padres o tutores legales" (menores de 14)**; **de 14 a 18 años podrán otorgarlo por sí mismos salvo norma específica**; esfuerzos razonables de verificación (art. 8.2 RGPD); retirar el consentimiento tan fácil como darlo (art. 7.3).
- **Clasificación: Hecho verificado.**

**F16. LO 3/2018 (BOE)**
- Título: *Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales* | BOE | URL: https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673 | Consulta: 20/10/2026 | Tipo: norma legal primaria.
- Afirmaciones: art. 7 (consentimiento de menores, umbral 14 años); el texto incluye, entre los supuestos de especial consideración, *"o) Las federaciones deportivas cuando traten datos de menores de edad"*, seguido de designación de delegado de protección de datos.
- **Clasificación: Hecho verificado** para el art. 7; **Hallazgo de fuente** para el número exacto del artículo sobre DPD (no verificado en el extracto → **Pendiente**).

**F17. Resolución AEPD E-04969-2020**
- Título: *E-04969-2020* | AEPD | URL: https://www.aepd.es/documento/e-04969-2020.pdf | 22/04/2021 | Consulta: 20/10/2026 | Tipo: resolución administrativa primaria.
- Afirmaciones: incluir fotografías de menores en plataformas/web/foros **supone tratamiento de datos personales**; la única base legitimadora suele ser el consentimiento, y **quien publica debe demostrar que lo tiene**.
- **Clasificación: Hecho verificado.**

**F18. Memorias AEPD 2023 y 2024**
- Título: *Memoria Anual AEPD 2023* (https://www.aepd.es/memorias/memoria-aepd-2023.pdf) y *2024* (https://www.aepd.es/memorias/memoria-aepd-2024.pdf) | AEPD | Consulta: 20/10/2026 | Tipo: informe oficial.
- Afirmaciones: consultas recurrentes sobre **datos de menores en el ámbito deportivo**, especialmente grabación y difusión de imágenes en prácticas deportivas; consultas de clubes deportivos; en 2024 la AEPD **planteó modificar la LOPDGDD para incrementar de 14 a 16 años la edad mínima de consentimiento** (reunión del 5 de febrero).
- **Clasificación:** primeros puntos = **Hecho verificado**; el incremento a 16 = **Hecho verificado de que fue propuesto**, y **Pendiente** en cuanto a si se aprueba (no hay evidencia de aprobación → **no debe asumirse**).

**F19. Sanción a un club deportivo por imágenes de un menor (PS/00494/2023)**
- Título: *Sanción a un club deportivo por difundir imágenes de un menor en su página web* | Autor: Sandra Pérez, Prodat | URL: https://www.prodat.es/blog/sancion-a-un-club-deportivo-por-difundir-imagenes-de-un-menor-en-su-pagina-web | 10/07/2024 | Consulta: 20/10/2026 | Tipo: **fuente secundaria** (despacho jurídico).
- Afirmación: la AEPD estimó el recurso porque el club **no acreditó consentimiento para las fechas de publicación** (las casillas además venían premarcadas → art. 7 RGPD).
- **Clasificación: Hallazgo de fuente.** Limitación: no se consultó el expediente original de la AEPD.

### 4.3 Fuentes académicas (entrenamiento, carga, pruebas, lesiones)

**F20. Bozzini, McFadden, Scruggs & Arent (2021)** — *Evaluation of Performance Characteristics and Internal and External Training Loads in Female Collegiate Beach Volleyball Players* | J Strength Cond Res 35(6):1559-1567 | https://pubmed.ncbi.nlm.nih.gov/33927118 | 01/06/2021 | revisado por pares. Carga de competición superó a la de entrenamiento; "assess and manage training loads… to optimize performance and decrease injury risk". **Hallazgo de fuente.** Limitación: población universitaria de EE. UU.

**F21. Oliveira et al. (2018)** — *Monitoring training load in beach volleyball players: a case study with an Olympic team* | Motriz | https://www.scielo.br/j/motriz/a/RLBH8wsyF6p3LBfvPjzy8Jd/?lang=en | 2018 | revisado por pares. Monitoreo s-RPE durante 10 semanas; monotonia y strain; desequilibrio carga/recuperación → fatiga aguda, overreaching, overtraining. **Hallazgo de fuente.** Limitación: un solo equipo olímpico.

**F22. Validación de s-RPE en voleibol de playa** — referencia *Session-RPE is a valuable internal load evaluation method in beach volleyball for both genders, elite and amateur players…* — Kinesiology 2020, 52, 30–38, DOI 10.26582/k.52.1.4. Cita obtenida dentro de la bibliografía de PMC9517593 (acceso indirecto). **Hallazgo de fuente (acceso indirecto) — Pendiente:** verificar el texto original.

**F23. *Fatigue and Training Load Factors in Volleyball* (2022)** — https://pmc.ncbi.nlm.nih.gov/articles/PMC9517593 | 06/09/2022 | revisado por pares. Acelerómetros + RPE + TQR en 11 deportistas; s-RPE método "valuable and relatively quick-to-perform". **Hallazgo de fuente.** Limitación: n = 11.

**F24. Diferencias de carga externa indoor vs. playa (2024)** — https://pmc.ncbi.nlm.nih.gov/articles/PMC10768657 | 02/01/2024 | revisado por pares. 80% de rallies ≤10 s; distancia y PlayerLoad™ hasta 23% mayores en playa; recomendación de monitoreo individualizado. **Hallazgo de fuente.**

**F25. Scoping review: ML y monitoreo no invasivo en voleibol femenino (2026)** — https://pmc.ncbi.nlm.nih.gov/articles/PMC12944405 | 07/02/2026 | revisión por pares. Evidencia heterogénea; **el voleibol indoor domina (83,3%) frente al de playa (16,7%)**. **Hallazgo de fuente.** Se cita solo para ese dato — el componente ML queda fuera del MVP por decisión de scope.

**F26. Lesiones en voleibol de playa de élite (estudio FIVB)** — https://pubmed.ncbi.nlm.nih.gov/12531768 | 2003 | cohorte revisada por pares. 178 jugadores; 3,1/1.000 h competición y 0,8/1.000 h entrenamiento (pérdida de tiempo); **67 jugadores refirieron 79 lesiones por sobrecarga** (lumbar 19%, rodilla 12%, hombro 10%). **Hallazgo de fuente.**

**F27. FIVB Injury Surveillance System, 4 años (BJSM 2015)** — https://bjsm.bmj.com/content/49/17/1132 | 01/09/2015 | revisado por pares. Riesgo global bajo; **las lesiones por sobrecarga están probablemente infrarrepresentadas**; prevención → reducción de carga y corrección técnica. **Hallazgo de fuente.**

**F28. Timoteo et al. (2024/2025) — carga y lesiones (ACWR)** — *Training Load and Injuries in Volleyball: An Approach Based on Different Methods of Calculating Acute to Chronic Workload Ratio* | Sports Health 17(1):104-110 | https://pubmed.ncbi.nlm.nih.gov/39535079 | 13/11/2024 | observacional longitudinal revisado por pares. ACWR acoplado elevado ↔ mayor riesgo de lesión (OR ≈ 2,0); monitorización continua. **Hallazgo de fuente.** Limitación: voleibol indoor masculino profesional.

**F29. Baterías de pruebas físicas de voleibol de playa** — *Beach Volleyball Physical Testing Protocols* | Volleyball Canada | https://volleyball.ca/uploads/About/LTAD/Beach_Volleyball_Physical_Testing_Protocols.pdf | sin fecha | protocolo de federación (no revisado por pares). Squat jump y CMJ, salto con carrera y de bloqueo, sprint 10 m en arena (parcial 5 m), agilidad 5-10-5 reactiva, test 30-15 intermitente. **Hallazgo de fuente.**

**F30. Bishop (2003)** — *A comparison between land and sand-based tests for beach volleyball assessment* | J Sports Med Phys Fitness 43(4):418-23 | https://pubmed.ncbi.nlm.nih.gov/14767400 | 12/2003 | comparativo revisado por pares. Saltos en arena menores que en piso (p<0,05) con **correlación fuerte (r = 0,93)**. **Hallazgo de fuente.**

**F31. Sattler et al. (2012)** — tests de salto: fiabilidad alfa 0,97–0,99 | https://pubmed.ncbi.nlm.nih.gov/21904238 | revisión de fiabilidad revisada por pares (citada 386 veces). **Hallazgo de fuente.**

### 4.4 Fuentes sobre prácticas de planificación y adopción digital

**F32. *Coaches' Perceptions of Common Planning Concepts Within Training Theory* (2023)** — Sports Medicine Open | https://sportsmedicine-open.springeropen.com/counter/pdf/10.1186/s40798-023-00657-6.pdf | 21/11/2023 | encuesta internacional revisada por pares. 106 entrenadores; **71%** planes periodizados; **96%** evalúa necesidades al inicio de temporada. **Hallazgo de fuente.** Limitación: muestra mixta, no vóley playa.

**F33. Uso de herramientas digitales por entrenadores (COVID, boxeo Noruega)** — *#Quarantineworkout…* | https://pmc.ncbi.nlm.nih.gov/articles/PMC7739676 | 20/11/2020 | cualitativo revisado por pares. Uso más frecuente: comunicación y administración; **entrenadores resisten más la innovación tecnológica que los atletas** (Trabal, 2008); falta de pericia (Sellitto, 2016). **Hallazgo de fuente** (evidencia de práctica, no prueba universal). Limitación: Noruega, boxeo, 2020.

**F34. *Exploring the nexus of digital technology and organizational change in non-profit sport organizations* (2024)** — Sport Management Review 27(5) | https://www.tandfonline.com/doi/abs/10.1080/14413523.2024.2346633 | 07/05/2024 | estudio de caso múltiple revisado por pares. 5 organizaciones canadienses, 49 entrevistas, 151 documentos; **cambio digital de nivel pequeño**; alerta de tecnología "ignorada estratégicamente". **Hallazgo de fuente.**

**F35. Digitalización del deporte de base (fútbol de exalumnos, 2025)** — https://pmc.ncbi.nlm.nih.gov/articles/PMC12406710 | 20/08/2025 | cuantitativo revisado por pares. *"the digital transformation of grassroots and amateur level sports remains **significantly underdeveloped**"*; equipos amateur voluntarios **sin estructuras de gestión claras**. **Hallazgo de fuente.** Limitación: contexto chino; extrapolación a vóley playa = **Inferencia**.

**F36. *2025 National Coaches Survey Report* (SafeSport, EE. UU.)** — https://uscenterforsafesport.org/wp-content/uploads/2026/01/USCS-Coaches-Survey-Report-FINAL_020326.pdf | 03/02/2026 | informe de encuesta. *"better club development, planning tools, and train-the-trainer resources"*. **Hallazgo de fuente** (evidencia de práctica).

**F37. Señal de mercado: KAIZEA (y similares)** — https://kaizea.com/en | sin fecha | **página comercial de proveedor**. Afirma el problema: "Paper, chat, spreadsheet — and one volunteer", plan en papel, asistencia en una app, chat en otra, hoja de cálculo con `#REF!`. **Hallazgo de fuente con limitación severa — MARKETING, NO EVIDENCIA DE PREVALENCIA.** No se recomienda ni se descarta ningún proveedor.

**F38. FIVB — Estructura institucional** — https://www.fivb.com/inside-fivb/fivb/structure/ | asociación suiza (1947, Lausanne); Congreso Mundial autoridad suprema. **Hecho verificado** (contexto, baja relevancia).

**F39. Estructura federativa española (funciones)** — *Funciones y normativa* | RFEVB | https://esvoley.es/federacion/funciones-y-estructura/funciones-y-normativa | estatutos art. 3: gobierno, organización, control de competiciones oficiales estatales, formación y potestad disciplinaria (Ley 10/1990, RD 1591/1992). **Hecho verificado.**

---

## 5. Contradicciones entre fuentes y vacíos de información

**Contradicciones / tensiones**

1. **Lesiones: riesgo "bajo" vs. sobrecarga "prevalente".** FIVB 2003 y BJSM 2015 concluyen riesgo bajo con definición de "pérdida de tiempo", pero ambos reconocen que **las lesiones por sobrecarga están infrarregistradas**. Es un desacuerdo metodológico explícito que la propia literatura reconoce → **Hallazgo de fuente** en ambos lados; la síntesis es **Inferencia**.
2. **Tests en piso vs. arena.** Bishop (2003): proxy válido (r = 0,93); estudio 2023 (PMC10443322): efecto significativo de la superficie. Poblaciones y métricas distintas → **Inferencia:** registrar **en qué superficie** se testó. **Pendiente:** revisar ambos artículos íntegros antes de fijar protocolo.
3. **¿Quieren los clubes herramientas digitales?** SafeSport 2025 y PMC12406710 dicen que sí; Sport Management Review 2024 y boxeo COVID muestran adopción modesta; proveedores afirman que el dolor existe → **Contradicción no resuelta** entre deseo declarado y adopción observada. **Pendiente de validación con usuarios reales.**
4. **s-RPE:** validada para VP "élite y amateur" (Kinesiology 2020, acceso indirecto) pero **limitada para táctico y partidos** (mismo texto); la scoping review 2026 confirma que la evidencia de playa es minoritaria (16,7%). No presentar el s-RPE como solución universal.
5. **Edad de consentimiento:** vigente a 14 años; la AEPD **propuso** subirla a 16. **Hecho:** existe la propuesta. **Pendiente:** si se aprueba; **no asumir** cambio normativo.

**Vacíos de información (declarados explícitamente)**

- **V1 —** No hay, en lo consultado, investigación sobre clubes españoles de voleibol de playa ni sobre sus problemas de gestión. Pendiente.
- **V2 —** No se consultó a ningún entrenador ni club real (sin entrevistas ni testimonios primarios). Todo lo que se afirma sobre "lo que les duele" es **Inferencia**. Pendiente.
- **V3 —** Sin datos de tamaño de mercado (nº de clubes de vóley playa en España, federados por FFAA, cuota económica). Solo nombres de clubes inscritos en LNVP 2025-26 (Fuengirola, CVP Kzero 12 Castellón, NZA BV Academy, CD Élite Vóley Almería, Sideout, Playas de Llanes, Ourense VP — circular ci25_11/2025, 23/09/2025), lo que **no es un censo**. Pendiente.
- **V4 —** No se verificó el uso real de herramientas digitales por clubes españoles (¿hojas de cálculo, WhatsApp, papel?). Pendiente.
- **V5 — Pagos:** fuera de alcance hasta aprobación explícita. Pendiente de decisión.
- **V6 —** No se descargó ningún PDF completo: toda la evidencia normativa procede de extractos del buscador. **Antes de convertir cualquier requisito normativo en especificación, hay que leer el documento íntegro.** Pendiente.
- **V7 —** Artículo exacto de la LOPDGDD sobre delegado de protección de datos no confirmado en el extracto del BOE. Pendiente.
- **V8 —** No se investigó notificaciones/calendario ni informes con fuentes primarias: los problemas 10 y 11 se sostienen sobre normas de competición y sobre inferencias. Pendiente.

---

## 6. Implicaciones para VOLTERRA (sin elegir tecnología)

1. **El modelo de "dupla con periodos" no es una preferencia de diseño, es un requisito del dominio.** La composición de parejas se calcula con puntos individuales de ranking y los cambios de pareja recalculan esos puntos (F7, F10). Cualquier esquema que sobrescriba quién estuvo con quién en qué fecha **destruye información con valor federativo**.
2. **El historial de atleta debe ser un registro continuo de una temporada a otra** (temporada 15/09–14/09, F6), con capacidad de tolerar cambios de reglas anuales (F13).
3. **Hay dos "rankings" conceptualmente distintos:** el ranking competitivo (RNVP, con penalizaciones y puntos negativos) y el indicador de desarrollo (asistencia, pruebas, observaciones). El scope ya los separa; la investigación lo respalda (F9, F11).
4. **Los menores de edad imponen requisitos de producto, no solo legales:** captura de consentimiento con distinción <14 / 14–18, prueba de su existencia, retiro tan fácil como su concesión, y control estricto de publicación/difusión de imágenes (F15–F19). Esto afecta a perfiles, informes y cualquier función de difusión.
5. **Los permisos deben estar en servidor y datos**, coherente con la obligación RGPD de accountability y con el acceso sensible a historiales de menores.
6. **La carga de entrenamiento y las pruebas físicas tienen respaldo científico suficiente para ser dominios del MVP**, pero **sin prometer predicciones de lesión**: la evidencia es de asociación, con poblaciones mayoritariamente no españolas y de voleibol indoor en parte (F28).
7. **El riesgo de adopción está documentado** (F33, F34): si el producto exige más registro del que el entrenador tolera, no se usará. Apoya el recorrido vertical corto del scope.
8. **Riesgo regulatorio activo (no aprobado):** la posible subida del consentimiento a 16 años (F18) debe vigilarse, pero **no diseñarse como si ya existiera**.

---

## 7. Recomendación provisional (Recomendación — no aprobada)

1. Mantener el orden del **recorrido vertical candidato** del scope (club → usuarios → atleta/categoría → sesión → asistencia → observación → historial): toca los problemas 1, 3, 5 y 9 con evidencia normativa más sólida.
2. Tratar los problemas **1 (historial de duplas), 3 (licencias/plazos) y 2 (protección de datos de menores)** como requisitos duros de modelado de datos y permisos, no como "fases posteriores".
3. **No incorporar pagos, ranking completo ni funciones de difusión de imágenes** hasta aprobación explícita; el ranking interno de desarrollo sí es coherente con el scope.
4. **Abrir una fase de validación con 3-5 clubes/entrenadores reales de vóley playa en España** antes de fijar alcance definitivo (vacíos V1/V2/V4; problemas 4, 5, 11 y 12 con confianza media o baja).
5. **Antes de convertir cualquier requisito federativo en especificación, leer el PDF íntegro** correspondiente (vacío V6).

**Limitaciones:** extractos de búsqueda, no documentos íntegros; evidencia científica no española y parcialmente de voleibol indoor; sin validación con usuarios.

---

## 8. Preguntas que requieren decisión del usuario

1. ¿Pagos dentro o fuera del MVP?
2. ¿VOLTERRA replica/muestra el ranking federativo oficial o solo un indicador interno de desarrollo?
3. ¿Se aceptarán atletas menores de 14 años?
4. ¿Habrá publicación o difusión de imágenes/perfiles?
5. ¿El ámbito es solo clubes no federados, o también clubes afiliados a RFEVB/FFAA?
6. ¿Hay acceso a entrenadores/clubes reales para entrevistar en la FASE 1?
7. ¿Se quiere homologar una batería concreta de pruebas físicas (arena vs. piso, frecuencia)?
8. ¿Quién asume el rol de responsable de tratamiento / DPD?
9. ¿Se excluyen expresamente notificaciones/calendario e informes del MVP inicial?

---

## Cierre (formato AGENTS.md)

- **Resumen:** FASE 1/A1 completada en modo solo lectura. Se leyeron 2 archivos locales y se ejecutaron **8 búsquedas web**; se registraron **39 fuentes** con URL, fecha de publicación cuando constaba, fecha de consulta 20/10/2026, tipo y limitaciones; se clasificaron hallazgos con las categorías del estándar y se priorizaron **12 problemas** con grado de confianza explícito.
- **Archivos modificados:** ninguno durante la investigación.
- **Pruebas/resultados ejecutados:** lectura de `product/volterra-scope.md` y `governance/research-evidence-standard.md`; 8 búsquedas web revisadas una a una. **No** se descargó ningún PDF completo.
- **Riesgos:** evidencia normativa en extractos; evidencia científica no española y parcialmente indoor; marketing de proveedores no es prueba de problema; posible cambio normativo 14→16 propuesto, no aprobado.
- **Decisiones pendientes:** las 9 preguntas de la §8.
- **Siguiente paso:** validación con 3-5 clubes reales y lectura íntegra de las normas RFEVB citadas (F3, F4, F7, F10).
