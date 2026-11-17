"""Modelos de presentación de las páginas HTML.

Cada vista declara los campos que consume su plantilla y expone ``context()``
con las claves que Jinja espera. Así el contrato de la plantilla queda en un
solo lugar y las rutas no construyen diccionarios sueltos.

No contienen reglas de autorización: solo datos ya filtrados por RLS + RPC y
decisiones de presentación (por ejemplo, si se muestra el botón de gestionar).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LoginView:
    error: str | None = None
    email: str = ""
    next_url: str = "/me"

    def context(self) -> dict[str, Any]:
        return {"error": self.error, "email": self.email, "next_url": self.next_url}


@dataclass(frozen=True)
class MeView:
    display_name: str | None
    memberships: list[dict]

    def context(self) -> dict[str, Any]:
        return {"display_name": self.display_name, "memberships": self.memberships}


@dataclass(frozen=True)
class ClubsView:
    memberships: list[dict]

    def context(self) -> dict[str, Any]:
        return {"memberships": self.memberships}


@dataclass(frozen=True)
class ClubView:
    club: dict
    can_edit: bool

    def context(self) -> dict[str, Any]:
        return {"club": self.club, "can_edit": self.can_edit}


@dataclass(frozen=True)
class ClubFormView:
    mode: str
    club: dict | None
    form: dict
    error: str | None = None

    def context(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "club": self.club,
            "form": self.form,
            "error": self.error,
        }


@dataclass(frozen=True)
class MembersView:
    club: dict
    members: list[dict]
    can_manage: bool
    assignable_roles: list[str] = field(default_factory=list)
    error: str | None = None

    def context(self) -> dict[str, Any]:
        return {
            "club": self.club,
            "members": self.members,
            "error": self.error,
            "can_manage": self.can_manage,
            "assignable_roles": self.assignable_roles,
            "manageable_roles": self.assignable_roles,
        }


@dataclass(frozen=True)
class AthletesView:
    club: dict
    athletes: list[dict]
    can_manage: bool
    error: str | None = None

    def context(self) -> dict[str, Any]:
        return {
            "club": self.club,
            "athletes": self.athletes,
            "can_manage": self.can_manage,
            "error": self.error,
        }


@dataclass(frozen=True)
class AthleteFormView:
    mode: str
    club: dict
    athlete: dict | None
    form: dict
    error: str | None = None

    def context(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "club": self.club,
            "athlete": self.athlete,
            "form": self.form,
            "error": self.error,
        }
