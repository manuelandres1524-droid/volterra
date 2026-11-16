"""Errores de dominio del BFF y su única traducción a HTTP.

Las capas de servicios y las guardas de autenticación **no conocen códigos
HTTP**: lanzan un ``DomainError`` con un código estable. El estado, el título de
la página y las cabeceras se resuelven aquí, y el manejador registrado en
``main.py`` decide entre JSON y HTML. Así la API y la interfaz no pueden
divergir al traducir el mismo fallo.

La autoridad de autorización sigue en Postgres (RLS + RPC). Estos errores solo
transportan el resultado que la base ya decidió, o un fallo del BFF.
"""

from __future__ import annotations

from typing import Any


class DomainError(Exception):
    """Fallo esperable del BFF con un código estable y un mensaje mostrable."""

    code: str = "error"
    default_message: str = "No se pudo completar la operación"

    def __init__(self, message: str | None = None, *, details: Any = None):
        self.message = message or self.default_message
        self.details = details
        super().__init__(self.message)


class InvalidInputError(DomainError):
    code = "invalid_input"
    default_message = "Los datos enviados no son válidos"


class UnauthenticatedError(DomainError):
    code = "unauthenticated"
    default_message = "No autenticado"


class ForbiddenError(DomainError):
    code = "forbidden"
    default_message = "Acceso denegado"


class NotFoundError(DomainError):
    code = "not_found"
    default_message = "No se encontró el recurso o no tienes acceso"


class ConflictError(DomainError):
    code = "conflict"
    default_message = "La operación entra en conflicto con el estado actual"


class RateLimitedError(DomainError):
    code = "rate_limited"
    default_message = "Demasiadas peticiones"

    def __init__(self, retry_after: int, message: str | None = None):
        self.retry_after = int(retry_after)
        super().__init__(message)


class UnavailableError(DomainError):
    code = "unavailable"
    default_message = "Servicio no disponible"


# Única tabla de traducción código -> estado HTTP.
STATUS_BY_CODE: dict[str, int] = {
    "invalid_input": 400,
    "unauthenticated": 401,
    "forbidden": 403,
    "not_found": 404,
    "conflict": 409,
    "rate_limited": 429,
    "unavailable": 503,
    "error": 500,
}

# Título que se muestra en la página de error HTML.
TITLE_BY_CODE: dict[str, str] = {
    "invalid_input": "Solicitud inválida",
    "unauthenticated": "Acceso denegado",
    "forbidden": "Acceso denegado",
    "not_found": "Página no encontrada",
    "conflict": "Conflicto con el estado actual",
    "rate_limited": "Demasiados intentos",
    "unavailable": "Servicio no disponible",
    "error": "No se pudo completar la operación",
}

# Código para los fallos que produce el framework (ruta inexistente, método no
# permitido, validación de cuerpo). Mantiene un único vocabulario de ``code``
# aunque el estado no venga de un ``DomainError``.
CODE_BY_STATUS: dict[int, str] = {
    400: "invalid_input",
    401: "unauthenticated",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "invalid_input",
    429: "rate_limited",
    503: "unavailable",
}


def http_status(error: DomainError) -> int:
    """Estado HTTP del error; 500 si el código no está en la tabla."""
    return STATUS_BY_CODE.get(error.code, 500)


def code_for_status(status_code: int) -> str:
    """Código estable para un fallo del framework; ``error`` si no está mapeado."""
    return CODE_BY_STATUS.get(status_code, "error")


def title(error: DomainError) -> str:
    """Título legible para la página de error."""
    return TITLE_BY_CODE.get(error.code, TITLE_BY_CODE["error"])


def headers(error: DomainError) -> dict[str, str]:
    """Cabeceras adicionales; solo el límite de peticiones las necesita."""
    if isinstance(error, RateLimitedError):
        return {"Retry-After": str(error.retry_after)}
    return {}
