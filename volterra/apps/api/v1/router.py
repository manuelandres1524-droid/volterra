from typing import Any

from fastapi import APIRouter

from apps.api.v1.endpoints import athletes, clubs, health, me, platform
from apps.api.v1.schemas import ErrorOut, ValidationErrorOut

# Respuestas de error documentadas en OpenAPI. Se declaran una vez para que el
# contrato no dependa de que cada endpoint recuerde añadirlas.
AUTH_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorOut, "description": "Sin autenticación"},
    429: {"model": ErrorOut, "description": "Límite de peticiones excedido"},
    503: {"model": ErrorOut, "description": "Dependencia no disponible"},
}

COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    **AUTH_RESPONSES,
    400: {"model": ErrorOut, "description": "Entrada inválida"},
    403: {"model": ErrorOut, "description": "Sin permisos para la operación"},
    404: {"model": ErrorOut, "description": "Recurso inexistente o sin acceso"},
    409: {"model": ErrorOut, "description": "Conflicto con el estado actual"},
    422: {"model": ValidationErrorOut, "description": "Cuerpo o parámetros inválidos"},
}

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(me.router, prefix="/me", tags=["me"], responses=AUTH_RESPONSES)
api_router.include_router(
    clubs.router, prefix="/clubs", tags=["clubs"], responses=COMMON_RESPONSES
)
api_router.include_router(
    platform.router, prefix="/platform", tags=["platform"], responses=COMMON_RESPONSES
)
api_router.include_router(
    athletes.router, prefix="/clubs", tags=["athletes"], responses=COMMON_RESPONSES
)
