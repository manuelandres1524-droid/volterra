"""Servicios de lectura de F2 (fichas de atleta) compartidos por API y HTML.

No aplican reglas de autorización: usan el cliente por petición con el JWT
del usuario y dejan que RLS decida qué filas son visibles. Los servicios solo
componen respuestas y evitan ``select *``.
"""

from __future__ import annotations

from typing import Any

from supabase import Client

from apps.core import circuit_breaker
from apps.services.postgrest_errors import translate_postgrest_error

_SELECT = "id,club_id,display_name,position,birth_date,gender,category,status,created_at"


def _execute(builder: Any) -> Any:
    breaker = circuit_breaker.supabase_breaker
    breaker.before_request()
    try:
        response = builder.execute()
    except Exception as exc:  # supabase-py propaga errores de red/PostgREST
        # Con .code la base respondió: se considera servicio sano (éxito).
        # Sin .code es transporte (red/timeout): cuenta como fallo.
        if getattr(exc, "code", None):
            breaker.record_success()
        else:
            breaker.record_failure()
        raise translate_postgrest_error(
            exc, unavailable_message="No se pudo consultar la base de datos"
        ) from exc
    breaker.record_success()
    return response


def _rows(response: Any) -> list[dict]:
    data = getattr(response, "data", None)
    return data if isinstance(data, list) else []


def get_athlete(client: Client, athlete_id: str) -> dict | None:
    response = _execute(
        client.table("athletes").select(_SELECT).eq("id", athlete_id).limit(1)
    )
    rows = _rows(response)
    return rows[0] if rows else None


def list_club_athletes(
    client: Client,
    club_id: str,
    *,
    status: str | None = "active",
    limit: int | None = None,
    offset: int = 0,
) -> list[dict]:
    builder = client.table("athletes").select(_SELECT).eq("club_id", club_id)
    if status:
        builder = builder.eq("status", status)
    builder = builder.order("display_name")
    if limit is not None:
        builder = builder.range(offset, offset + limit - 1)
    response = _execute(builder)
    return _rows(response)
