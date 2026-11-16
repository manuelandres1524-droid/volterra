# ADR-015 — Hardening de F1: límite de peticiones en memoria y logging estructurado

**Estado:** **Aprobada** por el propietario el 13/11/2026. Cierra DEC-22.
**Fecha:** 13/11/2026 · **Versión:** 1.0 · **Sustituye a:** —
**Relacionado:** DEC-06 (ASVS v5 nivel 2), DEC-08 (US$0/mes), DEC-12 (BFF), DEC-21 (frontend),
DEC-19/E-6 (región y transferencia).
**Insumo:** `docs/operations/pendientes-bloqueantes.md` §1, `apps/core/ratelimit.py`,
`apps/core/logging.py`, `main.py` y las pruebas `tests/test_ratelimit.py`,
`tests/test_logging.py`.

> Este documento registra una decisión técnica y su primera entrega. **No autoriza despliegue,
> contratación, gasto ni acceso a datos reales.** No cierra DEC-19/E-6 ni DEC-05.

---

## 1. Contexto

El BFF de F1 ya tenía lecturas, escrituras, sesión por cookie, CSRF y cabeceras de seguridad.
Quedaban dos condiciones de entrega sin cumplir: **[H]**

1. **Límite de peticiones.** `docs/operations/pendientes-bloqueantes.md` §1 lo registra como
   «no implementado; condición de entrega, no hecho». Sin él, `/login` permite intentos
   ilimitados contra GoTrue y cualquier ruta puede saturar el BFF o PostgREST.
2. **Observabilidad mínima.** No había registro de peticiones ni forma de correlacionar un
   error con una respuesta concreta. DEC-06 (ASVS v5 nivel 2) exige controles de
   anti-automatización y de registro; la matriz `requisito → estado` sigue pendiente, así que
   esta entrega **no** se declara conforme a ASVS.

Restricciones vigentes: US$0/mes (DEC-08), sin despliegue autorizado, sin datos reales,
autorización efectiva en RLS + RPC y host aún no elegido. **[H]**

## 2. Decisión

**Aplicar un límite de peticiones de ventana fija en memoria del proceso, con perfil estricto,
y logging estructurado en una línea JSON por evento, sin datos personales.**

### 2.1 Perfil aprobado

| Ámbito | Clave | Cupo | Ventana |
|---|---|---|---|
| Login (`POST /login`) | IP | 5 intentos | 5 min |
| Renovación (`POST /auth/refresh`) | IP | 15 | 5 min |
| Cierre de sesión (`POST /logout`) | IP | 15 | 5 min |
| Escritura sin sesión | IP | 15 | 1 min |
| Escritura autenticada | usuario (`sub`) | 15 | 1 min |
| Lectura autenticada | usuario (`sub`) | 120 | 1 min |

Los umbrales son configurables por variables de entorno; no son constantes ocultas.

### 2.2 Invariantes

1. **No autoriza.** El límite solo frena volumen. La autorización sigue en RLS + RPC y en las
   guardas del BFF. Un `429` no sustituye a un `403`. **[H]**
2. **Estado por proceso.** Un diccionario con cerrojo y reloj monótono. Sin Redis, sin
   dependencia nueva y sin coste (DEC-08). Los contadores se reinician al reiniciar y **no se
   comparten entre workers**. **[H]**
3. **Sin datos personales en el registro.** Se escriben método, ruta sin consulta, estado,
   duración, identificador de petición y huella no reversible de IP o usuario. No se registran
   correos, contraseñas, cookies, cabeceras, cuerpos ni IP en claro. **[H]**
4. **`X-Forwarded-For` no se confía por defecto.** Solo se usa si
   `RATE_LIMIT_TRUST_FORWARDED_FOR=true`, y se toma el último valor de la cadena (el que añade
   el proxy propio). Con el valor por defecto, la clave es la IP de la conexión. **[H]**
5. **La respuesta conserva `Retry-After`.** La API devuelve JSON; las páginas HTML devuelven la
   página de error con la misma cabecera. **[H]**
6. **Acotado en memoria.** Al alcanzar `max_keys` se podan ventanas expiradas; si no basta, se
   descarta el estado y se registra el evento. No hay crecimiento sin límite. **[R]**
7. **Identificador de petición.** Se acepta `X-Request-ID` solo con forma segura
   (`[A-Za-z0-9._-]{8,64}`); en cualquier otro caso se genera uno nuevo y se devuelve en la
   respuesta. **[H]**

## 3. Alternativas descartadas

| Alternativa | Motivo para no elegirla ahora |
|---|---|
| Redis o almacén compartido | Añade dependencia, configuración y posible coste; choca con DEC-08 y con el host aún no elegido. |
| Límite en el proxy/host | No hay host elegido. Delegarlo habría dejado la condición de entrega abierta. |
| Sin límite | Mantiene abierta una condición de entrega y deja `/login` expuesto a fuerza bruta. |
| Limitar también las lecturas anónimas | No aporta frente a la fuerza bruta y complica el flujo de login; las lecturas autenticadas ya se limitan por usuario. |

## 4. Consecuencias

**Positivas**

- `/login` deja de aceptar intentos ilimitados; las escrituras y lecturas autenticadas tienen
  techo por usuario.
- Cada respuesta lleva `X-Request-ID` y cada petición deja una línea JSON correlacionable.
- No se añaden dependencias, servicios ni coste.

**Costes y riesgos**

- **Multi-worker:** con N workers el cupo efectivo se multiplica por N. Se revisa al elegir host
  y topología; si se despliega con más de un worker, esta decisión debe reabrirse.
- **Reinicio:** los contadores se pierden al reiniciar el proceso.
- **IP compartida:** el perfil estricto puede afectar a varias personas tras una misma IP
  (oficina, NAT). El umbral es configurable; si aparece un falso positivo real, se ajusta con
  una decisión nueva.
- **Proxy:** si se despliega detrás de un proxy sin activar
  `RATE_LIMIT_TRUST_FORWARDED_FOR`, todos los clientes compartirán la IP del proxy.
- **Logging:** stdout puede contener rutas con UUID; no son datos personales, pero el destino y
  la retención de logs deberán decidirse antes de usar datos reales.

## 5. Verificación

- `pytest` completo: **137 passed, 1 warning** (13/11/2026), sobre 130 previas más 7 de
  interfaz. Incluye 21 pruebas nuevas de límite y logging: ventana fija, expiración,
  aislamiento de claves, poda, confianza en `X-Forwarded-For`, bloqueo de login, escritura
  anónima, lectura autenticada por usuario, desactivación, formato JSON, campos descartados,
  huella no reversible, saneado de `X-Request-ID`, ausencia de consulta en el registro y evento
  de rechazo.
- `compileall` sobre `apps/` y `main.py`: sin errores.
- **No ejecutado:** prueba de carga real, prueba con varios workers, ni verificación de que el
  destino de logs cumple retención. No se declara conformidad ASVS.

## 6. Disparadores de revisión

1. Se elige host o se despliega con más de un worker.
2. Se usan datos reales o se abre el acceso a usuarios externos.
3. Aparecen falsos positivos por IP compartida.
4. Se crea la matriz ASVS `requisito → estado` y se determine que estos controles no bastan.
5. Cambia el destino de logs o se exige retención concreta.
