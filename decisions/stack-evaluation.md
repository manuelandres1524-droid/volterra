# Evaluación del stack — VOLTERRA
**Estado:** histórico. **DEC-12 aprobada** el 12/11/2026: FastAPI como BFF (`decisions/adr/ADR-013-fastapi-bff.md`). **DEC-21 aprobada** el 12/11/2026: frontend Jinja2 + HTMX con sesión por cookie (`decisions/adr/ADR-014-frontend-jinja-htmx.md`). La matriz se conserva como evidencia; no se reescribe.

## Matriz propuesta
Puntuar cada alternativa de 1 a 5, adjuntar evidencia y confirmar los pesos antes de comparar.

| Criterio | Peso inicial | Verificar |
|---|---:|---|
| Seguridad y aislamiento multi-club | 15% | Roles, políticas de datos y pruebas de acceso cruzado |
| Facilidad de desarrollo con OpenCode | 15% | Ecosistema, documentación, depuración y pruebas |
| Costo total | 12% | Límites gratuitos, cuotas, precios al crecer |
| Modelo de datos relacional | 12% | Atletas, clubes, duplas, entrenamientos, resultados e historial |
| Despliegue y operación | 10% | Migraciones, logs, rollback, backups, región |
| Mantenibilidad | 10% | Complejidad, documentación y disponibilidad de soporte |
| Autenticación y archivos | 8% | Sesiones, permisos, fotos y documentos |
| Integraciones y automatización | 6% | APIs, webhooks, correo y mensajería |
| Portabilidad | 6% | Exportación, migración y formatos estándar |
| Analítica futura | 6% | Consultas, métricas, exportación e historial |
| **Total** | **100%** | |

## Alternativas a comparar
- Frontend: React/Next.js con TypeScript u opción más sencilla justificada.
- Backend: Python/FastAPI, API TypeScript o backend administrado.
- Datos/auth: PostgreSQL administrado; Supabase es candidato, no decisión.
- Hosting: frontend separado, full-stack o serverless, comprobando límites y tareas en segundo plano.
- Automatización: código propio para reglas críticas; n8n u otra herramienta para integraciones secundarias.
- Agentes de desarrollo OpenCode y la IA dentro del producto VOLTERRA son dos decisiones distintas.

## Preguntas necesarias
1. ¿Multi-club desde el MVP?
2. ¿Qué funciones entran en la primera entrega?
3. ¿Qué volumen inicial de clubes y atletas se espera?
4. ¿Qué presupuesto mensual máximo hay para herramientas e infraestructura?
5. ¿Se necesitan archivos y tareas en segundo plano desde el comienzo?
6. ¿Qué requisitos de respaldo y recuperación se necesitan?
7. ¿Qué proveedor/modelo está disponible en la instalación de OpenCode?

El resultado será una matriz con fuentes y una propuesta de decisión ADR. No marcar como aprobada hasta confirmación del usuario.
