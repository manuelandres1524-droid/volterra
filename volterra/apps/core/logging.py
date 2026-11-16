"""Logging estructurado del BFF.

Escribe una línea JSON por evento en la salida estándar. No registra secretos,
cabeceras, cookies, cuerpos de petición, correos ni direcciones IP en claro: la
IP se sustituye por una huella no reversible y el resto de datos personales no
se incluye. Los identificadores de usuario tampoco se escriben en claro.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import secrets
import sys
from datetime import datetime, timezone

from apps.core.config import settings

_LOGGER_NAME = "volterra"

# Campos adicionales que el formateador acepta. Cualquier otro `extra` se
# descarta a propósito para evitar fugas accidentales.
_ALLOWED_EXTRA = (
    "event",
    "request_id",
    "method",
    "path",
    "status",
    "duration_ms",
    "scope",
    "identity",
    "retry_after",
)

_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._-]{8,64}$")

# Sal de proceso: la huella de una IP o de un usuario no es reversible y no es
# comparable entre reinicios.
_FINGERPRINT_SALT = secrets.token_hex(16)


class JsonFormatter(logging.Formatter):
    """Formatea cada registro como un objeto JSON de una sola línea."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in _ALLOWED_EXTRA:
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging() -> logging.Logger:
    """Configura el logger del proyecto una sola vez, sin duplicar handlers."""
    logger = logging.getLogger(_LOGGER_NAME)
    if getattr(logger, "_volterra_configured", False):
        return logger

    handler = logging.StreamHandler(sys.stdout)
    if settings.LOG_FORMAT == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))

    logger.addHandler(handler)
    logger.setLevel(settings.LOG_LEVEL.upper())
    logger.propagate = False
    logger._volterra_configured = True  # type: ignore[attr-defined]
    return logger


def get_logger(name: str) -> logging.Logger:
    """Devuelve un logger bajo el espacio ``volterra``."""
    return logging.getLogger(f"{_LOGGER_NAME}.{name}")


def fingerprint(value: str | None) -> str:
    """Huella corta y no reversible de una IP o de un identificador de usuario."""
    if not value:
        return "unknown"

    return hashlib.sha256(f"{_FINGERPRINT_SALT}:{value}".encode("utf-8")).hexdigest()[:16]


def sanitize_request_id(value: str | None) -> str | None:
    """Acepta un ``X-Request-ID`` solo si tiene forma segura y longitud acotada."""
    if not value:
        return None
    candidate = value.strip()
    if not _REQUEST_ID_RE.fullmatch(candidate):
        return None
    return candidate
