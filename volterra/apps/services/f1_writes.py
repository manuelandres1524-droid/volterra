"""Escrituras de F1: envuelven las RPC ``SECURITY DEFINER`` de Supabase.

Igual que los servicios de lectura, este módulo **no aplica reglas de
autorización**: cada llamada viaja con el JWT del usuario y es la función de
base de datos la que comprueba rol, ámbito e invariantes. Aquí solo se
traducen los SQLSTATE de PostgREST a errores de dominio; el estado HTTP lo
decide ``apps.core.errors``.
"""

from __future__ import annotations

from typing import Any

from supabase import Client

from apps.core import circuit_breaker
from apps.services.postgrest_errors import translate_postgrest_error


def _rpc(client: Client, name: str, params: dict[str, Any]) -> Any:
    breaker = circuit_breaker.supabase_breaker
    breaker.before_request()
    try:
        response = client.rpc(name, params).execute()
    except Exception as exc:  # postgrest.exceptions.APIError y errores de red
        # Con .code la base respondió: se considera servicio sano (éxito).
        if getattr(exc, "code", None):
            breaker.record_success()
        else:
            breaker.record_failure()
        raise translate_postgrest_error(
            exc, unavailable_message="No se pudo completar la operación"
        ) from exc
    breaker.record_success()
    return getattr(response, "data", None)


def create_club(
    client: Client,
    name: str,
    city: str | None = None,
    country: str = "CO",
) -> str:
    data = _rpc(
        client,
        "fn_create_club",
        {"p_name": name, "p_city": city, "p_country": country},
    )
    return str(data)


def update_club(
    client: Client,
    club_id: str,
    name: str | None = None,
    city: str | None = None,
    country: str | None = None,
    club_status: str | None = None,
) -> None:
    _rpc(
        client,
        "fn_update_club",
        {
            "p_club_id": club_id,
            "p_name": name,
            "p_city": city,
            "p_country": country,
            "p_status": club_status,
        },
    )


def add_member(
    client: Client,
    club_id: str,
    user_id: str,
    role: str,
) -> str:
    data = _rpc(
        client,
        "fn_add_member",
        {"p_club_id": club_id, "p_user_id": user_id, "p_role": role},
    )
    return str(data)


def change_member_role(
    client: Client,
    membership_id: str,
    new_role: str,
) -> str:
    data = _rpc(
        client,
        "fn_change_member_role",
        {"p_membership_id": membership_id, "p_new_role": new_role},
    )
    return str(data)


def end_membership(client: Client, membership_id: str) -> None:
    _rpc(client, "fn_end_membership", {"p_membership_id": membership_id})
