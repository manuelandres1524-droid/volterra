"""Servicios de lectura de F1 compartidos por la API JSON y las páginas HTML.

No aplican reglas de autorización: usan el cliente por petición con el JWT del
usuario y dejan que RLS + RPC decidan qué filas son visibles. Los servicios solo
componen respuestas y evitan ``select *``.
"""

from __future__ import annotations

from typing import Any

from supabase import Client

from apps.services.postgrest_errors import translate_postgrest_error


def _execute(builder: Any) -> Any:
    try:
        return builder.execute()
    except Exception as exc:  # supabase-py propaga errores de red/PostgREST
        raise translate_postgrest_error(
            exc, unavailable_message="No se pudo consultar la base de datos"
        ) from exc


def _rows(response: Any) -> list[dict]:
    data = getattr(response, "data", None)
    return data if isinstance(data, list) else []


def get_profile(client: Client, user_id: str) -> dict | None:
    response = _execute(
        client.table("profiles").select("id,display_name").eq("id", user_id).limit(1)
    )
    rows = _rows(response)
    return rows[0] if rows else None


def list_my_clubs(client: Client, memberships: list[dict]) -> list[dict]:
    club_ids = sorted({str(m["club_id"]) for m in memberships if m.get("club_id")})
    clubs: dict[str, dict] = {}
    if club_ids:
        response = _execute(
            client.table("clubs").select("id,name,city,status").in_("id", club_ids)
        )
        clubs = {str(row["id"]): row for row in _rows(response)}

    result: list[dict] = []
    for membership in memberships:
        club_id = str(membership.get("club_id") or "")
        club = clubs.get(club_id)
        if not club:
            continue
        result.append(
            {
                "club_id": club_id,
                "club_name": club.get("name"),
                "city": club.get("city"),
                "status": club.get("status"),
                "role": membership.get("role"),
                "started_at": membership.get("started_at"),
                "ended_at": membership.get("ended_at"),
            }
        )

    return sorted(result, key=lambda item: (item.get("club_name") or "").casefold())


def get_club(client: Client, club_id: str) -> dict | None:
    response = _execute(
        client.table("clubs")
        .select("id,name,city,country,status,created_at")
        .eq("id", club_id)
        .limit(1)
    )
    rows = _rows(response)
    return rows[0] if rows else None


def get_membership(client: Client, membership_id: str) -> dict | None:
    """Pertenencia visible para el usuario; RLS decide si existe para él."""
    response = _execute(
        client.table("club_memberships")
        .select("id,club_id,user_id,role,started_at")
        .eq("id", membership_id)
        .limit(1)
    )
    rows = _rows(response)
    return rows[0] if rows else None


def list_club_members(
    client: Client,
    club_id: str,
    *,
    limit: int | None = None,
    offset: int = 0,
) -> list[dict]:
    """Pertenencias activas del club, con paginación opcional.

    ``offset`` solo tiene sentido junto a ``limit``; la ruta valida esa
    combinación antes de llamar. El orden secundario por ``id`` mantiene
    estable la paginación cuando varias pertenencias comparten ``started_at``.
    """
    query = (
        client.table("club_memberships")
        .select("id,user_id,role,started_at")
        .eq("club_id", club_id)
        .is_("ended_at", "null")
        .order("started_at")
        .order("id")
    )
    if limit is not None:
        query = query.range(offset, offset + limit - 1)

    response = _execute(query)
    members = _rows(response)

    user_ids = sorted({str(member["user_id"]) for member in members if member.get("user_id")})
    profiles: dict[str, str] = {}
    if user_ids:
        profiles_response = _execute(
            client.table("profiles").select("id,display_name").in_("id", user_ids)
        )
        profiles = {
            str(row["id"]): row.get("display_name")
            for row in _rows(profiles_response)
            if row.get("id")
        }

    return [
        {
            "id": member.get("id"),
            "user_id": member.get("user_id"),
            "display_name": profiles.get(str(member.get("user_id"))),
            "role": member.get("role"),
            "started_at": member.get("started_at"),
        }
        for member in members
    ]
