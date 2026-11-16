import os

import pytest

from apps.core.ratelimit import limiter


def pytest_sessionstart(session):
    # No permitir uso automático de service_role en tests
    if os.getenv("SUPABASE_SERVICE_ROLE_KEY") and os.getenv("ALLOW_SERVICE_ROLE_TESTS") != "1":
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY detectado. No se permite para tests ordinarios")


@pytest.fixture(autouse=True)
def _reinicia_limite_peticiones():
    """Aísla los contadores en memoria entre pruebas.

    Sin esto, el límite por IP o por usuario acumularía peticiones de pruebas
    distintas y algunas fallarían con 429 por orden de ejecución.
    """
    limiter.reset()
    yield
    limiter.reset()
