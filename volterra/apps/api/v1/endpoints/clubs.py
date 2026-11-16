from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import BaseModel, Field, field_validator
from supabase import Client

from apps.api.v1.schemas import ClubOut, IdOut, MembersOut, MyClubsOut
from apps.auth.deps import (
    AuthContext,
    require_auth,
    require_club_role,
    require_csrf_if_cookie,
    require_platform_admin,
)
from apps.core.errors import InvalidInputError, NotFoundError
from apps.integrations.supabase.deps import get_data_client
from apps.services.f1_reads import (
    get_club as read_club,
    get_membership,
    list_club_members,
    list_my_clubs,
)
from apps.services.f1_writes import (
    add_member,
    change_member_role,
    create_club,
    end_membership,
    update_club,
)

router = APIRouter()

ClubRole = Literal["club_admin", "coach"]
ClubStatus = Literal["active", "suspended", "closed"]


class ClubCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    city: str | None = Field(default=None, max_length=120)
    country: str = Field(default="CO", min_length=2, max_length=2)

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        return value

    @field_validator("city")
    @classmethod
    def _city_blank_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("country")
    @classmethod
    def _country_upper(cls, value: str) -> str:
        return value.strip().upper()


class ClubUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    city: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, min_length=2, max_length=2)
    status: ClubStatus | None = None

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        return value

    @field_validator("country")
    @classmethod
    def _country_upper(cls, value: str | None) -> str | None:
        return value.strip().upper() if value is not None else None


class MemberCreate(BaseModel):
    user_id: UUID
    role: ClubRole


class MemberRoleUpdate(BaseModel):
    role: ClubRole


@router.get("/me", response_model=MyClubsOut)
def my_clubs(
    ctx: AuthContext = Depends(require_auth),
    client: Client = Depends(get_data_client),
):
    memberships = list_my_clubs(client, ctx.memberships)
    return {
        "user_id": ctx.user_id,
        "is_platform_admin": ctx.is_platform_admin,
        "memberships": memberships,
    }


@router.post("", status_code=status.HTTP_201_CREATED, response_model=IdOut)
def create_club_endpoint(
    payload: ClubCreate,
    ctx: AuthContext = Depends(require_platform_admin),
    _: None = Depends(require_csrf_if_cookie),
    client: Client = Depends(get_data_client),
):
    club_id = create_club(client, payload.name, payload.city, payload.country)
    return {"id": club_id}


@router.patch("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_club_endpoint(
    club_id: str,
    payload: ClubUpdate,
    ctx: AuthContext = Depends(require_platform_admin),
    _: None = Depends(require_csrf_if_cookie),
    client: Client = Depends(get_data_client),
):
    fields = payload.model_dump(exclude_unset=True)
    update_club(
        client,
        club_id,
        name=fields.get("name"),
        city=fields.get("city"),
        country=fields.get("country"),
        club_status=fields.get("status"),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{club_id}", response_model=ClubOut)
def get_club(
    club_id: str,
    ctx: AuthContext = Depends(require_club_role(["club_admin", "coach"])),
    client: Client = Depends(get_data_client),
):
    club = read_club(client, club_id)
    if not club:
        raise NotFoundError("Club no encontrado o sin acceso")
    return club


@router.get("/{club_id}/members", response_model=MembersOut)
def list_members(
    club_id: str,
    limit: int | None = Query(default=None, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    ctx: AuthContext = Depends(require_club_role(["club_admin", "coach"])),
    client: Client = Depends(get_data_client),
):
    if limit is None and offset:
        raise InvalidInputError("El desplazamiento requiere indicar un límite")
    members = list_club_members(client, club_id, limit=limit, offset=offset)
    return {
        "club_id": club_id,
        "members": members,
        "limit": limit,
        "offset": offset,
    }


def _membership_in_club(client: Client, club_id: str, membership_id: str) -> None:
    membership = get_membership(client, membership_id)
    if not membership or str(membership.get("club_id")) != str(club_id):
        raise NotFoundError("Pertenencia no encontrada o sin acceso")


@router.post("/{club_id}/members", status_code=status.HTTP_201_CREATED, response_model=IdOut)
def add_member_endpoint(
    club_id: str,
    payload: MemberCreate,
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    _: None = Depends(require_csrf_if_cookie),
    client: Client = Depends(get_data_client),
):
    membership_id = add_member(client, club_id, str(payload.user_id), payload.role)
    return {"id": membership_id}


@router.patch("/{club_id}/members/{membership_id}", response_model=IdOut)
def change_member_role_endpoint(
    club_id: str,
    membership_id: str,
    payload: MemberRoleUpdate,
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    _: None = Depends(require_csrf_if_cookie),
    client: Client = Depends(get_data_client),
):
    _membership_in_club(client, club_id, membership_id)
    new_id = change_member_role(client, membership_id, payload.role)
    return {"id": new_id}


@router.delete("/{club_id}/members/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
def end_membership_endpoint(
    club_id: str,
    membership_id: str,
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    _: None = Depends(require_csrf_if_cookie),
    client: Client = Depends(get_data_client),
):
    _membership_in_club(client, club_id, membership_id)
    end_membership(client, membership_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
