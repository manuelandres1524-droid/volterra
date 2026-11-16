# FASE 1 (Colombia) — 04: Preguntas antes de elegir tecnologías

**Área:** A4 · **Estado:** propuesta — no aprobada · **Fecha:** 21/10/2026.
**Jurisdicción:** Colombia. Ninguna pregunta está respondida; ninguna tecnología seleccionada.

**Prioridad:** P1 = bloqueante antes de elegir stack · P2 = antes de la primera entrega · P3 = antes de ampliar alcance.

---

## 1. Lista consolidada (actualizada a Colombia; 38 preguntas)

| ID | Pregunta | Categoría | Quién responde | Prior. | Estado |
|---|---|---|---|---|---|
| Q-01 | ¿Multi-club desde el MVP (varios clubes con aislamiento por `club_id`)? | producto | usuario | P1 | A |
| Q-02 | ¿Confirmar o ajustar el MVP propuesto (F1–F12 + F23 mínimo)? | producto | usuario + clubes piloto | P1 | AP (propuesta A2 existe) |
| Q-03 | ¿Qué volumen inicial de clubes y atletas se espera? | producto | usuario + clubes | P1 | A |
| Q-04 | ¿Un usuario puede pertenecer a varios clubes a la vez? | producto | usuario | P1 | A |
| Q-05 | ¿Las duplas son solo modelo de datos o también operan asistencia/observaciones ligadas? | producto | usuario | P1 | A |
| Q-06 | ¿Se permiten sesiones retroactivas? | producto | usuario | P3 | A |
| Q-07 | ¿Ranking del club (no oficial) dentro o fuera del MVP, y con qué etiqueta? | producto | usuario | P2 | A |
| Q-08 | ¿Qué significa "evolución medible" (escala acordada con clubes)? | producto | usuario + clubes | P3 | A |
| Q-09 | ¿Imágenes/difusión de menores dentro o fuera del alcance (futuro F17)? | legal | usuario + asesoría | P1 | A |
| Q-10 | ¿Ámbito **federado colombiano** (liga→FVCV) o club/escuela no federado? | legal | usuario + FVCV | P1 | A |
| Q-11 | ¿IA/ML dentro del producto en horizonte cercano? (fuera de MVP) | producto | usuario | P3 | A |
| Q-12 | ¿Pagos, calendario y notificaciones en horizonte cercano? | producto | usuario | P3 | A |
| Q-13 | ¿Presupuesto mensual máximo para herramientas e infraestructura? | presupuesto | usuario | P1 | A |
| Q-14 | **E-1:** ¿Resultados de menores = datos públicos o requieren autorización siempre? | legal | asesoría jurídica | P1 | A |
| Q-15 | **E-2:** ¿Autorización única del representante o por finalidad (datos/imágenes/marketing)? | legal | asesoría jurídica | P1 | A |
| Q-16 | **E-7:** ¿Es válida autorización electrónica en app para NNA y cómo probarla? | legal | asesoría jurídica | P1 | A |
| Q-17 | **E-8:** ¿Cómo operacionalizar el derecho del menor a ser escuchado en el alta? | legal | asesoría + usuario (diseño) | P1 | A |
| Q-18 | **E-3:** Datos de salud de menores (pruebas físicas, lesiones): ¿autorización expresa adicional? | legal | asesoría jurídica | P2 | A |
| Q-19 | **E-4:** Conservación: ¿hasta cuándo retener historiales de menores tras baja? | legal | asesoría jurídica | P2 | A |
| Q-20 | **E-5:** ¿VOLTERRA obligada al RNBD (>100.000 UVT)? | legal | asesoría jurídica | P2 | A |
| Q-21 | **E-6:** Cloud fuera de Colombia: ¿excepción art. 26 o declaración de conformidad? | legal | asesoría jurídica | P1 | A |
| Q-22 | **E-9:** ¿Cuándo se espera manual interno/oficina de cumplimiento (art. 17.k)? | legal | asesoría jurídica | P2 | A |
| Q-23 | ¿Se aprueba la matriz de permisos por rol (propuesta A3-Colombia)? | seguridad | usuario | P1 | AP (propuesta) |
| Q-24 | ¿Nivel ASVS (L1/L2/L3) y alcance de pruebas de seguridad? | seguridad | usuario | P1 | A |
| Q-25 | ¿Alcance/responsables de pruebas de acceso cruzado entre clubes? (depende Q-01) | seguridad | usuario | P1 | A |
| Q-26 | ¿Bitácora de auditoría: alcance, quién accede, retención? | seguridad | usuario + asesoría | P2 | A |
| Q-27 | ¿RPO/RTO y política de respaldo? | operación | usuario | P1 | A |
| Q-28 | ¿Archivos (fotos/docs) y tareas en segundo plano desde el comienzo? | operación | usuario | P2 | A |
| Q-29 | ¿Proveedor/modelo de OpenCode disponible? (herramienta de desarrollo) | operación | usuario | P2 | A |
| Q-30 | ¿Requisito de **región de datos en Colombia**? (relacionado Q-21) | operación | usuario + asesoría | P2 | A |
| Q-31 | ¿Quién, cuántas y cuándo entrevistas a clubes colombianos? | operación | usuario + clubes | P1 | A |
| Q-32 | ¿Se investiga mercado colombiano (nº clubes vóley playa, presupuestos)? | operación | investigación | P2 | A |
| Q-33 | ¿Contacto directo FVCV para reglamentos de playa, licencias y ranking vigentes (sitio JS no extraíble)? | operación | usuario | P1 | A |
| Q-34 | ¿Gestiona la plataforma el certificado médico de aptitud (Res. 1286/2024) o solo lo registra el club? | producto | usuario + asesoría | P2 | A |
| Q-35 | ¿Los borradores Mindeporte 2025-2026 (clubes) fueron expedidos? Revalidar antes de asumir requisitos. | legal | investigación | P2 | A |
| Q-36 | ¿Qué nivel de precisión de evidencia se exige antes de aprobar requisitos jurídicos (extractos vs. íntegros)? | operación | usuario | P2 | A |
| Q-37 | **Alcance por edades:** ¿el producto cubre atletas y titulares de **todas las edades** (no solo menores), con protección reforzada de NNA desde el MVP y privacidad/seguridad de todos los usuarios? (instrucción 21/10/2026) | producto | usuario + clubes | P1 | A |
| Q-38 | **E-10:** ¿Existe literal expreso en el art. 17 (u otra norma colombiana) que obligue a comunicar violaciones de seguridad a la **SIC**? Si existe, ¿qué plazo? | legal | asesoría jurídica | P2 | A |

---

## 2. Eliminadas respecto a la FASE 1 (España)

- ~~Nivel de DPD / LO art. 34 (España)~~ → sustituido por E-9 (manual interno art. 17.k, figura colombiana propia).
- ~~Base jurídica RGPD (interés legítimo, ejecución de contrato)~~ → en Colombia las bases son autorización (y excepciones del art. 6 para sensibles; datos públicos para NNA).
- ~~Umbral de consentimiento 14/16 años~~ → no aplica; todo <18 = NNA (Q-14…Q-17).
- ~~EIPD/DPIA obligatoria~~ → P-12 (`03`): buena práctica, no obligación legal (reclasificada).
- ~~RNVP/RFEVB/FFAA~~ → Q-10, Q-33 (modelo colombiano FVCV/ligas).
- ~~Plazos RGPD 30 días~~ → plazos SIC 10/15 días hábiles (integrados en Q-14…Q-16).

## 3. Resumen por prioridad

- **P1 (20):** Q-01…Q-05, Q-09, Q-10, Q-13…Q-17, Q-21, Q-23…Q-25, Q-27, Q-31, Q-33, Q-37.
- **P2 (14):** Q-07, Q-18…Q-20, Q-22, Q-26, Q-28…Q-30, Q-32, Q-34, Q-35, Q-36, Q-38.
- **P3 (4):** Q-06, Q-08, Q-11, Q-12.

**Cierre:** 38 preguntas (P1=20, P2=14, P3=4), ninguna respondida, ninguna tecnología seleccionada. Relación con decisiones: Q-23 → DEC-03; Q-15/Q-16/Q-17 → DEC-04 (E-2, E-7, E-8); Q-14 → E-1 (condiciona F7/DEC-01); Q-19 → DEC-05 (E-4); Q-24 → DEC-06; Q-27 → DEC-07; Q-13 → DEC-08; Q-10/Q-33 → DEC-09; Q-09 → DEC-10; Q-29 → DEC-13; Q-26 → DEC-18; Q-21/Q-30 → DEC-19; Q-37 → DEC-01 (alcance por edades); Q-38 → E-10. **Siguiente paso:** respuestas P1 del usuario o encargo Q-31/Q-33.
