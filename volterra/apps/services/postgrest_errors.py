"""Traducción única de errores de PostgREST/PostgreSQL a errores de dominio.

Las lecturas y las escrituras comparten el mismo mapa de SQLSTATE para que un
mismo fallo de la base no se traduzca a estados distintos según el servicio.
Un código desconocido se trata como indisponibilidad: nunca se inventa un 403
ni se expone el texto crudo de un error no reconocido.
"""

from __future__ import annotations

from apps.core.errors import (
    ConflictError,
    DomainError,
    ForbiddenError,
    InvalidInputError,
    NotFoundError,
    UnauthenticatedError,
    UnavailableError,
)

# SQLSTATE -> error de dominio. Los códigos vienen de las guardas de las
# migraciones y de las restricciones de las tablas.
SQLSTATE_ERRORS: dict[str, type[DomainError]] = {
    "28000": UnauthenticatedError,  # no autenticado
    "42501": ForbiddenError,  # sin privilegios
    "P0002": NotFoundError,  # no existe
    "23505": ConflictError,  # duplicado
    "40001": ConflictError,  # conflicto de concurrencia
    "23503": InvalidInputError,  # referencia inexistente
    "23514": InvalidInputError,  # violación de CHECK / invariante
    "22023": InvalidInputError,  # argumento inválido
    "22P02": InvalidInputError,  # representación inválida (p. ej. UUID)
}

# Mensaje controlado por SQLSTATE. Evita propagar texto de la base (nombres de
# restricciones u otros detalles internos) al cliente (F-01).
SQLSTATE_MESSAGES: dict[str, str] = {
    "28000": "No autenticado.",
    "42501": "Acceso denegado.",
    "P0002": "Recurso no encontrado.",
    "23505": "El recurso ya existe.",
    "40001": "Conflicto de concurrencia. Inténtalo de nuevo.",
    "23503": "Referencia inexistente.",
    "23514": "Los datos no cumplen las reglas de validación.",
    "22023": "Argumento inválido.",
    "22P02": "Identificador inválido.",
}


def translate_postgrest_error(exc: Exception, *, unavailable_message: str) -> DomainError:
    """Convierte una excepción de PostgREST en un error de dominio.

    Los mensajes de los SQLSTATE conocidos provienen de los ``RAISE EXCEPTION``
    de nuestras RPC o de restricciones controladas. Los códigos desconocidos y
    los fallos de red no exponen el texto original: usan el mensaje genérico
    que recibe esta función.
    """
    code = str(getattr(exc, "code", "") or "")
    error_cls = SQLSTATE_ERRORS.get(code)
    if error_cls is None:
        return UnavailableError(unavailable_message)

    # Mensaje fijo por SQLSTATE; nunca se propaga el texto original de la base.
    text = SQLSTATE_MESSAGES.get(code, unavailable_message)
    return error_cls(text)
