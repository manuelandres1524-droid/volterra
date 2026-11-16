"""Límite de peticiones en memoria, por proceso.

Implementa una ventana fija con reloj monótono y un diccionario protegido por
un cerrojo. No hay estado compartido: con varios workers cada proceso aplica su
propio cupo, y los contadores se reinician al reiniciar el proceso. Es una
decisión deliberada para no añadir dependencias ni coste (DEC-08); se revisa al
elegir host y topología de despliegue.

El límite complementa a RLS + RPC, no autoriza nada. Solo frena fuerza bruta y
ráfagas anómalas antes de llegar a Supabase.
"""

from __future__ import annotations

import ipaddress
import math
import threading
import time
from dataclasses import dataclass
from typing import Callable

from apps.core.config import settings
from apps.core.logging import fingerprint, get_logger

log = get_logger("ratelimit")

SCOPE_LOGIN = "login"
SCOPE_REFRESH = "refresh"
SCOPE_LOGOUT = "logout"
SCOPE_ANON_WRITE = "anon_write"
SCOPE_READ = "read"
SCOPE_WRITE = "write"

_WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_SKIP_PREFIXES = ("/static/",)
_SKIP_PATHS = frozenset(
    {
        "/health",
        "/health/live",
        "/health/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
    }
)
_ACCESS_COOKIE = "volterra_access"

_AUTH_ENDPOINTS = {
    ("POST", "/login"): SCOPE_LOGIN,
    ("POST", "/auth/refresh"): SCOPE_REFRESH,
    ("POST", "/logout"): SCOPE_LOGOUT,
}


@dataclass(frozen=True)
class Limit:
    max_requests: int
    window_seconds: int


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after: int


class FixedWindowLimiter:
    """Contador de ventana fija con expulsión acotada de claves."""

    def __init__(
        self,
        clock: Callable[[], float] = time.monotonic,
        max_keys: int = 20_000,
    ) -> None:
        self._clock = clock
        self._max_keys = max_keys
        self._lock = threading.Lock()
        # (scope, identity) -> (inicio_ventana, contador, expira_en)
        self._buckets: dict[tuple[str, str], tuple[float, int, float]] = {}

    def check(self, scope: str, identity: str, limit: Limit) -> RateLimitResult:
        now = self._clock()
        key = (scope, identity)
        with self._lock:
            self._prune(now, key)
            started, count, expires = self._buckets.get(key, (now, 0, now + limit.window_seconds))
            if now >= expires:
                started, count, expires = now, 0, now + limit.window_seconds
            count += 1
            self._buckets[key] = (started, count, expires)
            allowed = count <= limit.max_requests
            remaining = max(0, limit.max_requests - count)
            retry_after = max(1, math.ceil(expires - now))

        return RateLimitResult(allowed=allowed, remaining=remaining, retry_after=retry_after)

    def reset(self) -> None:
        with self._lock:
            self._buckets.clear()

    def _prune(self, now: float, current_key: tuple[str, str]) -> None:
        """Elimina ventanas expiradas y, si hace falta, la más antigua.

        Nunca vacía el estado completo: eso reiniciaría los contadores de todos
        los clientes y permitiría saltarse el límite inundando identidades
        nuevas. La clave de la petición en curso no se expulsa.
        """
        expired = [key for key, (_, _, expires) in self._buckets.items() if expires <= now]
        for key in expired:
            del self._buckets[key]

        if len(self._buckets) < self._max_keys or current_key in self._buckets:
            return

        while len(self._buckets) >= self._max_keys:
            oldest = min(self._buckets, key=lambda key: self._buckets[key][0])
            del self._buckets[oldest]


limiter = FixedWindowLimiter()


def _limit_for(scope: str) -> Limit:
    limits = {
        SCOPE_LOGIN: Limit(
            settings.RATE_LIMIT_LOGIN_ATTEMPTS, settings.RATE_LIMIT_LOGIN_WINDOW_SECONDS
        ),
        SCOPE_REFRESH: Limit(
            settings.RATE_LIMIT_REFRESH_ATTEMPTS, settings.RATE_LIMIT_REFRESH_WINDOW_SECONDS
        ),
        SCOPE_LOGOUT: Limit(
            settings.RATE_LIMIT_LOGOUT_ATTEMPTS, settings.RATE_LIMIT_LOGOUT_WINDOW_SECONDS
        ),
        SCOPE_ANON_WRITE: Limit(
            settings.RATE_LIMIT_ANON_WRITE_REQUESTS, settings.RATE_LIMIT_WRITE_WINDOW_SECONDS
        ),
        SCOPE_WRITE: Limit(
            settings.RATE_LIMIT_WRITE_REQUESTS, settings.RATE_LIMIT_WRITE_WINDOW_SECONDS
        ),
        SCOPE_READ: Limit(
            settings.RATE_LIMIT_READ_REQUESTS, settings.RATE_LIMIT_READ_WINDOW_SECONDS
        ),
    }
    return limits[scope]


def client_ip(request) -> str:
    """IP del cliente, validada. ``X-Forwarded-For`` solo se usa si se confía en el proxy."""
    candidate: str | None = None
    if settings.RATE_LIMIT_TRUST_FORWARDED_FOR:
        raw = request.headers.get("x-forwarded-for")
        if raw:
            parts = [part.strip() for part in raw.split(",") if part.strip()]
            # El proxy propio añade la IP del cliente al final de la cadena.
            candidate = parts[-1] if parts else None
    if not candidate:
        client = getattr(request, "client", None)
        candidate = getattr(client, "host", None)
    if not candidate:
        return "unknown"
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return "unknown"


def check(scope: str, identity: str) -> RateLimitResult:
    """Cuenta una petición y devuelve el resultado, sin lanzar excepciones."""
    return limiter.check(scope, identity, _limit_for(scope))


def log_rejection(scope: str, identity: str, retry_after: int) -> None:
    log.warning(
        "rate_limited",
        extra={
            "event": "rate_limited",
            "scope": scope,
            "identity": fingerprint(identity),
            "retry_after": retry_after,
        },
    )


def _normalized_path(path: str) -> str:
    if len(path) > 1 and path.endswith("/"):
        return path.rstrip("/")
    return path


def anonymous_scope(request) -> str | None:
    """Ámbito aplicable antes de autenticar, o ``None`` si no corresponde limitar."""
    if not settings.RATE_LIMIT_ENABLED:
        return None

    path = _normalized_path(request.url.path)
    if path in _SKIP_PATHS or path.startswith(_SKIP_PREFIXES):
        return None

    method = request.method.upper()
    known = _AUTH_ENDPOINTS.get((method, path))
    if known:
        return known

    # Escrituras sin cookie de sesión: no hay usuario que identificar todavía.
    if method in _WRITE_METHODS and not request.cookies.get(_ACCESS_COOKIE):
        return SCOPE_ANON_WRITE
    return None


def user_scope(request) -> str:
    """Ámbito de una petición ya autenticada."""
    method = str(getattr(request, "method", "") or "").upper()
    return SCOPE_WRITE if method in _WRITE_METHODS else SCOPE_READ


def evaluate(scope: str | None, identity: str) -> RateLimitResult | None:
    """Evalúa un ámbito; devuelve ``None`` si no hay nada que limitar."""
    if not scope or not settings.RATE_LIMIT_ENABLED:
        return None
    result = check(scope, identity)
    if not result.allowed:
        log_rejection(scope, identity, result.retry_after)
    return result
