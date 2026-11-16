# F1 — Autorización, alcance y límites del arranque

**Fecha:** 25/10/2026 · **Estado:** registro de ejecución, no de aprobación técnica
**Autorizante:** propietario del proyecto · **Ejecutor:** coordinador VOLTERRA

Este documento existe porque el análisis de gobernanza previo a la primera migración concluyó que faltaba base documental. No crea decisiones nuevas: registra lo que el propietario autorizó y separa lo que sigue abierto.

---

## 1. Qué autorizó el propietario (25/10/2026)

Texto de referencia: instrucción «AUTORIZACIÓN E INICIO DE IMPLEMENTACIÓN F1».

| Autorización | Alcance literal | Límite explícito |
|---|---|---|
| Implementar F1 | Perfiles de club y usuarios, conforme a la documentación existente | No F7 (E-1 bloqueado) |
| Escribir en la base de datos | Proyecto Supabase conectado, `ref taevpaknhuoyiujqgjku` | Solo datos ficticios |
| Commits locales | Tras cada unidad validada | Sin `git add .`, sin reescritura de historial |
| Push al remoto | Commits de la implementación | Sin push forzado |
| Vercel | Inspeccionar y preparar conexión | **Sin desplegar**, sin servicios de pago |
| Servidor local | Levantar y probar | Sin infraestructura remota |

**No autorizado y por tanto no ejecutado:** despliegue a producción, datos reales de menores, cierre de bloqueos jurídicos, activación de planes pagos, creación de proyectos adicionales.

---

## 2. Decisión del propietario sobre entorno (no es calificación jurídica)

- El proyecto Supabase conectado se autoriza como **entorno de desarrollo no productivo** para F1.
- **Región: `us-east-1`.** Queda fijada por esta autorización al usar el proyecto existente. Con la base vacía (0 tablas) habría sido barato recrear en `sa-east-1`; se documenta que **no se hace** porque el propietario autorizó explícitamente «el proyecto Supabase que ya está conectado».
- **Lo que NO se afirma:** que la región sea conforme a la Ley 1581; que el art. 26 esté resuelto; que E-6 esté cerrado; que DEC-19 esté aprobada. La región es una variable de entorno con valor, no una prueba de cumplimiento.
- **DEC-19 permanece abierta.**

> **Actualización del 12/11/2026 (no modifica la autorización del 25/10/2026).** El propietario
> indicó un proyecto distinto, `tioeoswnhwrlbovkxocd`. El host del proyecto anterior
> (`taevpaknhuoyiujqgjku`) ya no existe en DNS. El pooler IPv4 y el prefijo IPv6 del proyecto
> nuevo apuntan a `us-east-2`, no a `us-east-1`. Se deja constancia de la discrepancia; la región
> sigue siendo materia de DEC-19/E-6 y **no se considera aprobada**.


---

## 3. Excepción explícita a «F1 no debe iniciar»

La nota de reanudación establecía que F1 no debía iniciar sin resolver O-03 (respaldo) y la región. El propietario autorizó el arranque sabiendo que ambos siguen abiertos — su instrucción lo dice: «No considerar que conectar Supabase o Vercel resuelve por sí solo los requisitos legales de privacidad, residencia de datos, conservación o copias de seguridad».

Por tanto:

- **DEC-07 aprobada; O-03 sigue abierta.** El 13/11/2026 el propietario fijó RPO 24 h, RTO 8 h,
  volcado diario cifrado fuera del proveedor, retención 30 días y responsable el propietario
  (DEC-07). Desde el 26/10/2026 hay primer volcado real y un ensayo de restauración en un
  PostgreSQL local, con 127/127 pruebas en verde sobre la copia. Sigue **sin probarse la
  restauración en otro proyecto Supabase**. Evidencia en
  `docs/operations/o-03-respaldo-restauracion.md` §4.2; contexto de la vía nativa en
  `workspace/reanudacion-sesion.md` §7.4.
- Esta excepción es válida **solo mientras los datos sean ficticios y desechables**. El primer dato real la invalida.

---

## 4. Datos ficticios: regla operativa

| Regla | Consecuencia |
|---|---|
| Sin nombres, clubes, documentos ni menores reales | Los fixtures usan identificadores inventados y correos en `example.com` (RFC 2606) |
| Sin importación de CSV, Excel o exportaciones reales | No hay ruta técnica que cargue datos reales |
| Sin integraciones con terceros | Sin claves de clubes, federaciones ni pasarelas |
| Efecto jurídico | Un registro ficticio no tiene titular, luego no hay transferencia internacional que calificar. **E-6 queda latente, no resuelto** |

**El día del primer dato real** cambian de golpe: exigibilidad de P-01…P-13, E-6 (transferencia), E-4 (retención), DEC-05 y E-10. DEC-06 y DEC-07 ya están aprobadas (13/11/2026), pero la matriz ASVS aún no existe y el respaldo no se ha restaurado en un proyecto Supabase real.

---

## 5. DEC-12 (stack): cómo se trata

> **Actualización del 12/11/2026.** DEC-12 está **cerrada**: el propietario ratificó **FastAPI como
> BFF** (`decisions/adr/ADR-013-fastapi-bff.md`). La decisión no cambia lo ya implementado en F1:
> Supabase sigue siendo la base de datos autorizada y la autoridad de RLS/RPC. El BFF usa el JWT del
> usuario, no `service_role` y no abre conexión directa como propietario. **No se despliega** y no
> se usan datos reales. Siguen abiertos DEC-19/E-6 y DEC-05 (DEC-06 y DEC-07 quedaron aprobadas el
> 13/11/2026).

- Supabase se usa como **entorno de base de datos autorizado para F1**, no como stack aprobado del producto.
- La capa de aplicación es FastAPI como BFF delgado, sin reglas de dominio propias.
- La decisión de DEC-12 no resuelve DEC-19/E-6 ni el techo US$0 (DEC-08); cualquier host o servicio
  de pago exige una decisión nueva.

---

## 6. Alcance funcional de F1

Fuente: `docs/research/fase1-colombia/02-mvp-vs-futuro.md:21` (F1) y recorrido vertical paso 1 (`:58`).

**Dentro:**
- Club como unidad de aislamiento (DEC-02).
- Perfil de usuario mínimo (identidad global, sin datos deportivos).
- Pertenencia de una persona a un club, con rol y vigencia.
- Alta de miembros por administrador, con trazabilidad.
- Aislamiento entre clubes verificado por pruebas negativas (A-01, S-02).
- Bitácora de acciones sobre permisos (T-01).

**Fuera, con motivo:**

| Excluido | Motivo |
|---|---|
| Ficha de atleta (F2) | Funcionalidad distinta; requiere P-13 y decisión de campos |
| Flujo de representante legal (F3) | Depende de DEC-04, E-7, E-8 |
| Roles `athlete` / `guardian` | Su asignación pertenece a F2/F3. El enum no los incluye todavía |
| Invitaciones por correo (F18) | Las notificaciones son FUTURO; no hay canal definido |
| Imágenes/avatares (F17) | DEC-10 pendiente |
| Observaciones privadas | N-05; pertenece a F6 |
| Exportación ARCO-P (F11/F23) | Fuera de perfiles |

**Valores por defecto adoptados** (los más restrictivos, documentados como provisionales):
- Solo el administrador de plataforma crea clubes y designa administradores de club.
- Solo el administrador de plataforma edita el perfil del club (`fn_update_club`); un
  administrador de club gestiona entrenadores, no la identidad del club.
- El administrador de club puede dar de alta entrenadores, no otros administradores.
- Sin alta pública de clubes ni auto-registro en un club.

**Escrituras (ampliación del 13/11/2026, DEC-21 v1.1).** El alcance funcional de F1 ya incluía
altas y cambios de rol; lo que faltaba era la interfaz. Se añaden formularios HTML que llaman a las
RPC `SECURITY DEFINER` existentes: crear y editar club (`fn_create_club`, `fn_update_club`), añadir
miembro (`fn_add_member`), cambiar rol (`fn_change_member_role`) y cerrar pertenencia
(`fn_end_membership`). Condiciones:

- **Local y datos ficticios**, sin despliegue ni datos reales.
- La autorización efectiva sigue en RLS + RPC; el BFF solo traduce errores y valida formato.
- CSRF obligatorio en formularios y en la API cuando la sesión viene por cookie.
- Un administrador de club solo gestiona entrenadores; la UI ni siquiera ofrece el rol que la RPC
  rechazaría, pero la decisión final es de la base.
- El alta de miembro pide el UUID a mano: F1 no incluye buscador de usuarios ni invitaciones.

---

## 7. Modelo de autorización

El rol **no** vive en el perfil del usuario. Vive en la pertenencia al club, con vigencia.

Razón: un perfil es global; una persona puede ser entrenadora en un club y tutora en otro. Un rol global no se puede revocar por club y convierte cualquier error de asignación en acceso transversal.

`platform_admin` es un ámbito **separado** de los roles de club, en su propia tabla, sin `club_id`. Es la excepción explícita a la regla A-01 («todo registro de dominio lleva `club_id`») y está aislada para poder auditarla.

Evaluación por petición: autenticar → resolver `club_id` desde el recurso, nunca desde el cliente → exigir pertenencia activa → resolver rol vigente → aplicar matriz → filtrar por `club_id` también en la base. Denegado por defecto.

---

## 8. Revisión de seguridad independiente y endurecimiento (26/10/2026)

Tras aplicar las cinco primeras migraciones se pidió una revisión de seguridad independiente
(agente `security-auditor`) sobre el esquema ya desplegado en el entorno de desarrollo. Encontró
cuatro defectos reales. Los cuatro se corrigieron en una sexta migración
(`20261026040817_f1_hardening`), no en las anteriores: el historial de migraciones aplicadas no
se reescribe.

| Defecto | Qué permitía | Corrección en la migración 6 |
|---|---|---|
| D1 · carrera en el «último administrador» | Dos cierres simultáneos podían dejar un club sin administrador activo | `fn_end_membership` y `fn_change_member_role` bloquean la fila del club (`for update`) antes de contar; si la fila cambió, `40001` |
| D2 · `profiles` escribible por tabla completa y sin auditoría | Un titular podía fijar `created_at`/`id`; los cambios de perfil no dejaban rastro | Privilegios por columna (`insert (id, display_name)`, `update (display_name)`), trigger de auditoría que **no copia el dato personal** |
| D3 · auditoría de `clubs` con `club_id` en `NULL` | El evento de alta de club no era visible para el `club_admin` de ese club | El trigger de auditoría deriva el `club_id` de la propia fila del club |
| D4 · historial de exmiembros visible a `club_admin` | Un administrador de club veía pertenencias cerradas de su club | La política de lectura de `club_memberships` limita a `club_admin` a las vigentes; el historial completo queda para `platform_admin` y el titular de cada fila |

Pruebas ejecutadas sobre la base con las seis migraciones (**no** son estimaciones):

| Suite | Comprobaciones | Conformes | Residuos |
|---|---|---|---|
| `supabase/tests/f1_rls_isolation.test.sql` | 65 | 65 | 0 |
| `supabase/tests/f1_hardening.test.sql` | 37 | 37 | 0 |
| `supabase/tests/f1_service_role.test.sql` | 25 | 25 | 0 |

Total **127/127**. La suite principal se re-ejecutó *después* de la migración 6 y se comparó en
SQL contra el mapa de valores esperados: 65 claves esperadas, 65 obtenidas, 0 diferencias,
0 faltantes, 0 sobrantes. Tras las pruebas, la base quedó con 0 usuarios, 0 filas en las cinco
tablas y 0 eventos de auditoría.

**Prueba del rol `service_role` (25/25, 26/10/2026).** No es un defecto del esquema: es una
propiedad del rol que hay que conocer antes de elegir la capa de aplicación. Resultados reales:

- `service_role` tiene `BYPASSRLS` y `SELECT`/`INSERT` sobre las 5 tablas, incluida
  `platform_admins`.
- Sin identidad de usuario lee los 2 clubes y los 3 perfiles de fixture, inserta un club, renombra
  un club ajeno y actualiza `platform_admins`.
- Las 5 RPC **sí deniegan** con `28000` (`auth.uid()` nulo): la autorización de dominio resiste.
- Si la conexión fija `request.jwt.claims` con el `sub` de otra persona, la RPC la acepta y
  atribuye la autoría al usuario suplantado.

Conclusión aplicable a DEC-12: la clave `service_role` **no puede usarse en ningún camino de
usuario**. No se revocaron sus privilegios: hacerlo es una decisión de arquitectura, no tomada.

**Limitaciones de esta verificación, declaradas:**

1. La carrera de D1 no se probó con dos conexiones simultáneas: la suite comprueba la estructura
   (el bloqueo existe y precede a la guarda) y el rechazo `40001`, no la concurrencia real.
2. El titular **no** ve la auditoría de su propio perfil. La política de `audit_events` solo
   admite `platform_admin` y `club_admin` del club del evento (T-01). Es denegación por defecto,
   no una fuga, pero deja sin resolver el acceso del titular a su propia traza.

---

## 9. Riesgos aceptados al arrancar

| Riesgo | Estado |
|---|---|
| Sin restauración probada en un proyecto Supabase (O-03) | Aceptado solo con datos ficticios. Primer volcado real ejecutado el 26/10/2026 y ensayo de restauración en local con 127/127 pruebas en verde; falta restaurar en otro proyecto. RPO/RTO, frecuencia, retención, destino y responsable ya están decididos (DEC-07, 13/11/2026) (`docs/operations/o-03-respaldo-restauracion.md` §4.2) |
| Región sin evaluación jurídica (E-6) | Aceptado solo con datos ficticios |
| Registro de decisiones desincronizado | **Corregido el 26/10/2026**: `decisions/decision-register.md` v1.1 asienta las aprobaciones del 25/10 (DEC-01, DEC-02, DEC-03, DEC-08 y las cinco N-xx). El cierre formal del ciclo de esas fichas (Q-xx respondidas, fecha de revisión) sigue pendiente |
| Nivel ASVS (DEC-06) | **Resuelto el 13/11/2026**: OWASP ASVS v5.0.0 nivel 2. Falta crear la matriz requisito → estado |
| Sin límite de peticiones ni observabilidad | **Resuelto el 13/11/2026 (DEC-22)**: ventana fija en memoria por proceso con perfil estricto y logging JSON con `X-Request-ID`. Limitación declarada: con varios workers el cupo se multiplica y los contadores se reinician al reiniciar; se revisa al elegir host (`decisions/adr/ADR-015-hardening-f1.md`) |
| Clave `service_role` anula RLS y las guardas de dominio | Probado (25/25); regla: nunca en camino de usuario. Revocar privilegios queda como decisión de arquitectura |
| Sin política de retención (DEC-05/E-4) | Sin purga; solo desactivación lógica |
| Carrera de D1 no probada con dos conexiones | Verificada estructuralmente; prueba de concurrencia pendiente |
| El titular no ve su propia traza de auditoría | Limitación documentada; decisión funcional pendiente |

---

## 10. Pendientes que requieren al propietario

1. ~~Stack de la capa de aplicación (DEC-12)~~ — **cerrado el 12/11/2026**: FastAPI como BFF
   (`decisions/adr/ADR-013-fastapi-bff.md`). Queda pendiente el **host** y el **endurecimiento**
   indicado en ADR-013; el despliegue no está autorizado.
2. ~~Sincronizar `decisions/decision-register.md` con las aprobaciones del 25/10~~ — **hecho el 26/10/2026** (v1.1). Queda pendiente, si lo quieres, el **cierre formal** de esas fichas: responder las `Q-xx` P1 que las bloquean y fijar fecha de revisión.
3. ~~Nivel ASVS objetivo (DEC-06)~~ — **cerrado el 13/11/2026**: OWASP ASVS v5.0.0 nivel 2. Queda
   pendiente crear la matriz requisito → estado.
4. Retención y baja de titulares (DEC-05/E-4).
5. Remoto Git: **configurado** `origin = https://github.com/Theruin117/volterra.git` (rama `main`),
   con `origin/main` sincronizado el 26/10/2026. Sin `push` forzado y sin reescritura de historial.
6. Acceso del titular a la auditoría de su propio perfil: hoy no la ve. Requiere decisión
   funcional (ampliar la política de `audit_events` al `actor_user_id` propio). No se amplió por
   cuenta propia: cambia la visibilidad de datos personales.
7. Respaldo y restauración (O-03): **primer volcado real ejecutado el 26/10/2026** y ensayo de
   restauración en local (§4.2 de `docs/operations/o-03-respaldo-restauracion.md`). Falta restaurar
   en otro proyecto Supabase. RPO/RTO, frecuencia, retención, destino y responsable ya están
   decididos (DEC-07, 13/11/2026); el volcado de roles (§3.2) no se ejecutó.
8. ~~Hardening mínimo del BFF (límite de peticiones y logging)~~ — **hecho el 13/11/2026**
   (DEC-22, `decisions/adr/ADR-015-hardening-f1.md`). Queda pendiente revisar la topología de
   workers y el destino/retención de logs cuando exista host y antes de usar datos reales.
9. **Accesibilidad y responsive:** pulido aplicado el 13/11/2026 y verificado con 7 pruebas de
   interfaz. Siguen pendientes las pruebas con navegador real, axe/Lighthouse y lector de
   pantalla; no se declara conformidad WCAG.
