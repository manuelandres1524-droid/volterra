"""Circuit breaker por proceso para las llamadas a Supabase.

Estados: ``closed`` (normal) → ``open`` (se rechazan las llamadas de inmediato,
fallo rápido) → ``half_open`` (tras ``recovery_seconds``, se admite un único
intento de prueba). Un éxito desde ``half_open`` cierra el circuito; un fallo
desde ``half_open`` lo vuelve a abrir por otro periodo de recuperación.

El estado vive en memoria del proceso, igual que el rate limit (DEC-22), por lo
que cada instancia de la aplicación tiene el suyo. No sustituye un circuit
breaker distribuido si se despliega más de un proceso.

Solo los fallos de transporte (red, timeout, sin respuesta) cuentan como fallos
del circuito. Un error de dominio (p. ej. 42501, 23514) significa que la base
respondió y se considera un éxito para efectos del circuito.
"""

from __future__ import annotations

import threading
import time
from typing import Any

from apps.core.errors import UnavailableError

_OPEN_MESSAGE = "Servicio temporalmente no disponible. Inténtalo de nuevo en unos segundos."


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int,
        recovery_seconds: float,
        enabled: bool = True,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold debe ser al menos 1")
        if recovery_seconds < 0:
            raise ValueError("recovery_seconds no puede ser negativo")
        self._failure_threshold = failure_threshold
        self._recovery_seconds = recovery_seconds
        self._enabled = enabled
        self._consecutive_failures = 0
        self._opened_at: float | None = None
        self._half_open_in_flight = False
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        with self._lock:
            if self._opened_at is None:
                return "closed"
            if time.monotonic() - self._opened_at >= self._recovery_seconds:
                return "half_open"
            return "open"

    @property
    def consecutive_failures(self) -> int:
        with self._lock:
            return self._consecutive_failures

    def before_request(self) -> None:
        """Rechaza rápido cuando el circuito está abierto; se llama por petición."""
        with self._lock:
            if not self._enabled:
                return
            if self._opened_at is None:
                return
            if time.monotonic() - self._opened_at >= self._recovery_seconds:
                if self._half_open_in_flight:
                    raise UnavailableError(_OPEN_MESSAGE)
                self._half_open_in_flight = True
                return
            raise UnavailableError(_OPEN_MESSAGE)

    def record_success(self) -> None:
        with self._lock:
            self._consecutive_failures = 0
            self._opened_at = None
            self._half_open_in_flight = False

    def record_failure(self) -> None:
        with self._lock:
            self._consecutive_failures += 1
            if (
                self._half_open_in_flight
                or self._consecutive_failures >= self._failure_threshold
            ):
                self._opened_at = time.monotonic()
                self._half_open_in_flight = False

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            opened_at = self._opened_at
            failures = self._consecutive_failures
        if opened_at is None:
            state = "closed"
        elif time.monotonic() - opened_at >= self._recovery_seconds:
            state = "half_open"
        else:
            state = "open"
        return {"state": state, "consecutive_failures": failures}


def _build_breaker() -> CircuitBreaker:
    from apps.core.config import settings

    return CircuitBreaker(
        failure_threshold=settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
        recovery_seconds=settings.CIRCUIT_BREAKER_RECOVERY_SECONDS,
        enabled=settings.CIRCUIT_BREAKER_ENABLED,
    )


# Instancia única por proceso. Los servicios la importan en vez de crearse la suya.
supabase_breaker = _build_breaker()
