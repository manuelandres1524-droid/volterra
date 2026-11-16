"""Pruebas del logging estructurado.

Verifican que cada evento es una línea JSON válida, que solo se registran los
campos permitidos y que no se filtran correos, contraseñas, cookies, consultas
ni direcciones IP en claro.
"""

import json
import logging

import pytest
from fastapi.testclient import TestClient

from apps.core.config import settings
from apps.core.logging import JsonFormatter, fingerprint, sanitize_request_id
from apps.core.ratelimit import limiter
from main import app


class _Capture(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@pytest.fixture
def captura():
    logger = logging.getLogger("volterra")
    handler = _Capture()
    logger.addHandler(handler)
    try:
        yield handler.records
    finally:
        logger.removeHandler(handler)


@pytest.fixture(autouse=True)
def _limpia_limite():
    limiter.reset()
    yield
    limiter.reset()


def _record(**extra) -> logging.LogRecord:
    record = logging.LogRecord(
        name="volterra.http",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request",
        args=(),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_formateador_emite_json_con_campos_permitidos():
    line = JsonFormatter().format(
        _record(
            event="request",
            request_id="abc12345",
            method="GET",
            path="/me",
            status=200,
            duration_ms=1.5,
        )
    )
    payload = json.loads(line)

    assert payload["event"] == "request"
    assert payload["path"] == "/me"
    assert payload["status"] == 200
    assert payload["level"] == "INFO"
    assert payload["ts"].endswith("+00:00")


def test_formateador_descarta_campos_no_permitidos():
    line = JsonFormatter().format(
        _record(email="demo@example.com", password="secreta", cookie="volterra_access=x")
    )
    payload = json.loads(line)

    assert "email" not in payload
    assert "password" not in payload
    assert "cookie" not in payload


def test_fingerprint_no_revela_el_valor_original():
    huella = fingerprint("203.0.113.7")

    assert huella != "203.0.113.7"
    assert len(huella) == 16
    assert fingerprint("203.0.113.7") == huella
    assert fingerprint("203.0.113.8") != huella


def test_sanitize_request_id_acepta_solo_formatos_seguros():
    assert sanitize_request_id("abc12345-def") == "abc12345-def"
    assert sanitize_request_id("corto") is None
    assert sanitize_request_id("x" * 65) is None
    assert sanitize_request_id("abc 12345") is None
    assert sanitize_request_id("abc<script>") is None
    assert sanitize_request_id(None) is None


def test_cada_peticion_registra_metodo_ruta_y_estado(captura):
    client = TestClient(app, base_url="https://testserver")

    response = client.get("/health")

    assert response.status_code == 200
    eventos = [r for r in captura if getattr(r, "event", None) == "request"]
    assert len(eventos) == 1
    assert eventos[0].method == "GET"
    assert eventos[0].path == "/health"
    assert eventos[0].status == 200
    assert eventos[0].request_id == response.headers["x-request-id"]


def test_la_consulta_no_se_registra(captura):
    client = TestClient(app, base_url="https://testserver")

    client.get("/login?next_url=/clubs&correo=demo@example.com")

    eventos = [r for r in captura if getattr(r, "event", None) == "request"]
    assert eventos[0].path == "/login"
    assert "demo@example.com" not in json.dumps(
        {k: v for k, v in eventos[0].__dict__.items() if k != "msg"}, default=str
    )


def test_request_id_del_cliente_se_conserva_si_es_valido(captura):
    client = TestClient(app, base_url="https://testserver")

    response = client.get("/health", headers={"X-Request-ID": "cliente-12345678"})

    assert response.headers["x-request-id"] == "cliente-12345678"
    eventos = [r for r in captura if getattr(r, "event", None) == "request"]
    assert eventos[0].request_id == "cliente-12345678"


def test_request_id_invalido_se_sustituye(captura):
    client = TestClient(app, base_url="https://testserver")

    response = client.get("/health", headers={"X-Request-ID": "no valido!"})

    assert response.headers["x-request-id"] != "no valido!"
    assert len(response.headers["x-request-id"]) == 32


def test_el_rechazo_por_limite_registra_evento_sin_ip_en_claro(monkeypatch, captura):
    monkeypatch.setattr(settings, "RATE_LIMIT_LOGIN_ATTEMPTS", 0)
    client = TestClient(app, base_url="https://testserver")

    response = client.post(
        "/login",
        data={"email": "demo@example.com", "password": "secreta", "csrf_token": "x"},
    )

    assert response.status_code == 429
    rechazos = [r for r in captura if getattr(r, "event", None) == "rate_limited"]
    assert len(rechazos) == 1
    assert rechazos[0].scope == "login"
    assert rechazos[0].retry_after >= 1
    assert len(rechazos[0].identity) == 16

    peticiones = [r for r in captura if getattr(r, "event", None) == "request"]
    assert peticiones[0].status == 429
