# VOLTERRA — OpenCode Architecture Starter
**Estado:** borrador; no es un repositorio ni una selección de tecnologías definitiva.

## Propósito
Preparar agentes, reglas de trabajo y documentación antes de crear el repositorio y programar.

## Decisiones pendientes
Frontend, backend, base de datos/auth, hosting, pruebas/CI, observabilidad/backups, proveedor/modelo para OpenCode y herramientas de organización.

## Uso
1. Revisar `decisions/stack-evaluation.md`.
2. Confirmar el alcance preliminar en `product/volterra-scope.md`.
3. Revisar estructura y flujo en `workspace/`.
4. Tras aprobarlo, copiar `.opencode/agents/` y `AGENTS.md` a la raíz del futuro repo.
5. Validar los permisos con la versión instalada de OpenCode.
6. Crear el repositorio solo después de aprobar las decisiones mínimas.

No se incluye proveedor/modelo en la configuración: debe decidirse según opciones disponibles, calidad, privacidad y costo.
Documentación oficial: https://docs.opencode.ai/docs/agents/ y https://docs.opencode.ai/docs/config/

## Gobernanza añadida
Se incluyeron `governance/governance-charter.md`, `governance/research-evidence-standard.md` y el agente `.opencode/agents/governance-analyst.md`. Son propuestas pendientes de aprobación.
