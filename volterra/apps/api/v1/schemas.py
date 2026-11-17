"""Modelos de respuesta de la API JSON ``/api/v1``.

Fijan el contrato observable: FastAPI valida la salida y OpenAPI documenta los
campos reales. Los campos de fecha se declaran como ``str`` a propósito para no
alterar la representación que ya devuelve PostgREST.

No contienen reglas de autorización: solo describen datos que RLS + RPC ya
filtraron.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorOut(BaseModel):
    """Cuerpo de error de la API: mensaje mostrable y código estable."""

    detail: str
    code: str


class ValidationErrorOut(BaseModel):
    """Error de validación del framework: detalle estructurado por campo."""

    detail: list[dict[str, Any]]
    code: str


class MembershipOut(BaseModel):
    """Pertenencia activa tal como la entrega el contexto de autenticación."""

    club_id: str | None = None
    user_id: str | None = None
    role: str | None = None
    started_at: str | None = None
    ended_at: str | None = None


class MeOut(BaseModel):
    user_id: str
    email: str | None = None
    display_name: str | None = None
    is_platform_admin: bool
    memberships: list[MembershipOut] = Field(default_factory=list)


class MyClubOut(BaseModel):
    club_id: str
    club_name: str | None = None
    city: str | None = None
    status: str | None = None
    role: str | None = None
    started_at: str | None = None
    ended_at: str | None = None


class MyClubsOut(BaseModel):
    user_id: str
    is_platform_admin: bool
    memberships: list[MyClubOut] = Field(default_factory=list)


class ClubOut(BaseModel):
    id: str
    name: str
    city: str | None = None
    country: str | None = None
    status: str | None = None
    created_at: str | None = None


class MemberOut(BaseModel):
    id: str
    user_id: str
    display_name: str | None = None
    role: str
    started_at: str | None = None


class MembersOut(BaseModel):
    club_id: str
    members: list[MemberOut] = Field(default_factory=list)
    limit: int | None = None
    offset: int = 0


class IdOut(BaseModel):
    id: str


class PlatformOverviewOut(BaseModel):
    ok: bool
    actor: str


class HealthOut(BaseModel):
    status: str


class AthleteOut(BaseModel):
    id: str
    club_id: str
    display_name: str
    position: str | None = None
    birth_date: str | None = None
    gender: str = "unspecified"
    category: str | None = None
    status: str = "active"
    created_at: str | None = None


class AthletesOut(BaseModel):
    club_id: str
    athletes: list[AthleteOut] = Field(default_factory=list)
    status: str | None = "active"
    limit: int | None = None
    offset: int = 0
