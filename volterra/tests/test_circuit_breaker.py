"""Pruebas del circuit breaker de llamadas a Supabase."""

from types import SimpleNamespace

import pytest
from postgrest.exceptions import APIError

import apps.core.circuit_breaker as cb
from apps.core.errors import UnavailableError
from apps.services import f2_reads, f2_writes


def _api_error(code: str, message: str) -> APIError:
    return APIError({"code": code, "message": message})


def test_breaker_cerrado_inicial():
    breaker = cb.CircuitBreaker(failure_threshold=2, recovery_seconds=60.0)
    breaker.before_request()  # no lanza
    assert breaker.state == "closed"


def test_breaker_abre_tras_umbral_de_fallos():
    breaker = cb.CircuitBreaker(failure_threshold=2, recovery_seconds=60.0)
    breaker.record_failure()
    assert breaker.state == "closed"
    breaker.record_failure()
    assert breaker.state == "open"
    with pytest.raises(UnavailableError) as excinfo:
        breaker.before_request()
    assert "Servicio temporalmente no disponible" in excinfo.value.message


def test_breaker_recuperacion_half_open():
    breaker = cb.CircuitBreaker(failure_threshold=1, recovery_seconds=0.0)
    breaker.record_failure()
    # Con recovery 0 ya está en ventana de media-apertura: se admite 1 intento.
    breaker.before_request()
    breaker.record_success()
    assert breaker.state == "closed"
    assert breaker.consecutive_failures == 0


def test_breaker_half_open_fallo_vuelve_a_abrir():
    breaker = cb.CircuitBreaker(failure_threshold=1, recovery_seconds=0.0)
    breaker.record_failure()
    breaker.before_request()  # half-open
    breaker.record_failure()  # falla el intento de prueba
    assert breaker.state != "closed"
    assert breaker.consecutive_failures == 2


def test_breaker_deshabilitado_es_no_op():
    breaker = cb.CircuitBreaker(failure_threshold=1, recovery_seconds=60.0, enabled=False)
    breaker.record_failure()
    breaker.before_request()  # aunque alcanzó el umbral, no rechaza


class _Query:
    def __init__(self, error=None):
        self._error = error

    def select(self, *a, **k):
        return self

    def eq(self, *a, **k):
        return self

    def order(self, *a, **k):
        return self

    def limit(self, *a, **k):
        return self

    def execute(self):
        if self._error is not None:
            raise self._error
        return SimpleNamespace(data=[])


class _Client:
    def __init__(self, error=None, rpc_error=None):
        self.error = error
        self.rpc_error = rpc_error

    def table(self, name):
        return _Query(self.error)

    def rpc(self, name, params=None):
        return _Query(self.rpc_error)


def test_reads_open_breaker_fails_fast(monkeypatch):
    fresh = cb.CircuitBreaker(failure_threshold=2, recovery_seconds=60.0)
    monkeypatch.setattr(cb, "supabase_breaker", fresh)
    client = _Client(error=RuntimeError("sin conexión"))

    with pytest.raises(UnavailableError):
        f2_reads.list_club_athletes(client, "00000000-0000-4000-8000-000000000001")
    with pytest.raises(UnavailableError):
        f2_reads.list_club_athletes(client, "00000000-0000-4000-8000-000000000001")
    # Tercera llamada: circuito abierto, falla rápido sin ejecutar el query.
    with pytest.raises(UnavailableError) as excinfo:
        f2_reads.list_club_athletes(client, "00000000-0000-4000-8000-000000000001")
    assert "Servicio temporalmente no disponible" in excinfo.value.message


def test_reads_domain_error_does_not_open_breaker(monkeypatch):
    fresh = cb.CircuitBreaker(failure_threshold=2, recovery_seconds=60.0)
    monkeypatch.setattr(cb, "supabase_breaker", fresh)
    client = _Client(error=_api_error("42501", "denegado"))

    for _ in range(4):
        with pytest.raises(Exception):
            f2_reads.list_club_athletes(client, "00000000-0000-4000-8000-000000000001")
    # Los errores con .code son "servicio sano": el circuito sigue cerrado.
    assert fresh.state == "closed"


def test_writes_open_breaker_fails_fast(monkeypatch):
    fresh = cb.CircuitBreaker(failure_threshold=2, recovery_seconds=60.0)
    monkeypatch.setattr(cb, "supabase_breaker", fresh)
    client = _Client(rpc_error=RuntimeError("timeout"))

    with pytest.raises(UnavailableError):
        f2_writes.deactivate_athlete(client, "00000000-0000-4000-8000-0000000000a1")
    with pytest.raises(UnavailableError):
        f2_writes.deactivate_athlete(client, "00000000-0000-4000-8000-0000000000a1")
    with pytest.raises(UnavailableError) as excinfo:
        f2_writes.deactivate_athlete(client, "00000000-0000-4000-8000-0000000000a1")
    assert "Servicio temporalmente no disponible" in excinfo.value.message
