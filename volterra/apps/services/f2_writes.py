"""Escrituras de F2: envuelven las RPC ``SECURITY DEFINER`` de Supabase.

Igual que los servicios de F1, este módulo **no aplica reglas de autorización**:
cada llamada viaja con el JWT del usuario y es la función de base de datos la
que comprueba rol, ámbito e invariantes. Aquí solo se traducen los SQLSTATE de
PostgREST a errores de dominio; el estado HTTP lo decide ``apps.core.errors``.
"""

from __future__ import annotations

from typing import Any

from supabase import Client

from apps.services.postgrest_errors import translate_postgrest_error


def _rpc(client: Client, name: str, params: dict[str, Any]) -> Any:
    try:
        response = client.rpc(name, params).execute()
    except Exception as exc:  # postgrest.exceptions.APIError y errores de red
        raise translate_postgrest_error(
            exc, unavailable_message="No se pudo completar la operación"
        ) from exc
    return getattr(response, "data", None)


def create_athlete(
    client: Client,
    club_id: str,
    display_name: str,
    birth_date: str,
    position: str | None = None,
    gender: str = "unspecified",
    category: str | None = None,
) -> str:
    data = _rpc(
        client,
        "fn_create_athlete",
        {
            "p_club_id": club_id,
            "p_display_name": display_name,
            "p_birth_date": birth_date,
            "p_position": position,
            "p_gender": gender,
            "p_category": category,
        },
    )
    return str(data)


def update_athlete(
    client: Client,
    athlete_id: str,
    display_name: str | None = None,
    position: str | None = None,
    gender: str | None = None,
    category: str | None = None,
) -> None:
    _rpc(
        client,
        "fn_update_athlete",
        {
            "p_athlete_id": athlete_id,
            "p_display_name": display_name,
            "p_position": position,
            "p_gender": gender,
            "p_category": category,
        },
    )


def deactivate_athlete(client: Client, athlete_id: str) -> None:
    _rpc(client, "fn_deactivate_athlete", {"p_athlete_id": athlete_id})
