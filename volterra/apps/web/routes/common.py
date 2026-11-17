"""Utilidades compartidas por las rutas HTML de F1."""

from __future__ import annotations

from uuid import UUID

from fastapi import Request
from supabase import Client

from apps.auth.deps import AuthContext
from apps.core.errors import InvalidInputError, NotFoundError
from apps.services.f1_reads import get_club, get_membership, list_club_members
from apps.services.f2_reads import get_athlete, list_club_athletes
from apps.web.templates import render
from apps.web.viewmodels import AthletesView, MembersView


def safe_next(value: str | None, default: str = "/me") -> str:
    """Solo permite rutas internas; evita redirecciones abiertas."""
    if (
        not value
        or not value.startswith("/")
        or value.startswith("//")
        or "\\" in value
        or "\r" in value
        or "\n" in value
    ):
        return default
    return value


def club_role(ctx: AuthContext, club_id: str) -> str | None:
    """Rol del usuario en el club según las membresías ya verificadas."""
    if ctx.is_platform_admin:
        return "platform_admin"
    for membership in ctx.memberships:
        if membership.get("ended_at") is not None:
            continue
        if str(membership.get("club_id")) == str(club_id):
            return membership.get("role")
    return None


def assignable_roles(ctx: AuthContext) -> list[str]:
    """Roles que la UI ofrece; la RPC vuelve a comprobarlo en servidor."""
    if ctx.is_platform_admin:
        return ["club_admin", "coach"]
    return ["coach"]


def normalize_country(value: str | None) -> str | None:
    value = (value or "").strip().upper()
    return value if len(value) == 2 and value.isalpha() else None


def ensure_uuid(value: str) -> str:
    """Valida forma de UUID; no comprueba que exista (lo decide la RPC)."""
    try:
        UUID(value)
    except ValueError as exc:
        raise InvalidInputError("El identificador de usuario no es un UUID válido.") from exc
    return value


def athlete_in_club(client: Client, club_id: str, athlete_id: str) -> dict:
    """Ficha de atleta visible y del club indicado, o ``NotFoundError``."""
    athlete = get_athlete(client, athlete_id)
    if not athlete or str(athlete.get("club_id")) != str(club_id):
        raise NotFoundError("Atleta no encontrado o sin acceso.")
    return athlete


def render_athletes(
    request: Request,
    ctx: AuthContext,
    client: Client,
    club_id: str,
    *,
    error: str | None = None,
    status_code: int = 200,
):
    """Carga y renderiza la página de atletas con un estado consistente."""
    club = get_club(client, club_id)
    if not club:
        raise NotFoundError("Club no encontrado o sin acceso.")

    athletes = list_club_athletes(client, club_id)
    role = club_role(ctx, club_id)
    view = AthletesView(
        club=club,
        athletes=athletes,
        can_manage=ctx.is_platform_admin or role == "club_admin",
        error=error,
    )
    return render(request, "athletes.html", view.context(), status_code=status_code)


def membership_in_club(client: Client, club_id: str, membership_id: str) -> dict:
    """Pertenencia visible y del club indicado, o ``NotFoundError``."""
    membership = get_membership(client, membership_id)
    if not membership or str(membership.get("club_id")) != str(club_id):
        raise NotFoundError("Pertenencia no encontrada o sin acceso.")
    return membership


def render_members(
    request: Request,
    ctx: AuthContext,
    client: Client,
    club_id: str,
    *,
    error: str | None = None,
    status_code: int = 200,
):
    """Carga y renderiza la página de miembros con un estado consistente."""
    club = get_club(client, club_id)
    if not club:
        raise NotFoundError("Club no encontrado o sin acceso.")

    members = list_club_members(client, club_id)
    role = club_role(ctx, club_id)
    view = MembersView(
        club=club,
        members=members,
        can_manage=ctx.is_platform_admin or role == "club_admin",
        assignable_roles=assignable_roles(ctx),
        error=error,
    )
    return render(request, "members.html", view.context(), status_code=status_code)
