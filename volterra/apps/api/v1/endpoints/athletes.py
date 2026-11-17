"""Endpoints de F2: fichas de atleta (solo mayores de edad).

Escritura solo para ``club_admin`` (la RPC valida rol, ámbito e invariantes);
``coach`` puede listar y ver. Ningún endpoint acepta ``select *``: RLS decide
la visibilidad y las RPC solo devuelven identificadores.
"""

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import BaseModel, Field, field_validator
from supabase import Client

from apps.api.v1.schemas import AthletesOut, IdOut
from apps.auth.deps import (
    AuthContext,
    require_club_role,
    require_csrf_if_cookie,
)
from apps.core.errors import InvalidInputError, NotFoundError
from apps.integrations.supabase.deps import get_data_client
from apps.services.f2_reads import get_athlete, list_club_athletes
from apps.services.f2_writes import (
    create_athlete,
    deactivate_athlete,
    update_athlete,
)

router = APIRouter()

AthleteGender = Literal["male", "female", "unspecified"]
AthleteStatus = Literal["active", "inactive", "all"]


def _blank_to_none(value: str | None, max_len: int | None = None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if max_len is not None and len(value) > max_len:
        raise ValueError(f"El campo supera los {max_len} caracteres")
    return value


class AthleteCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    birth_date: date
    position: str | None = Field(default=None, max_length=30)
    gender: AthleteGender = "unspecified"
    category: str | None = Field(default=None, max_length=30)

    @field_validator("display_name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El alias no puede estar vacío")
        return value

    @field_validator("position")
    @classmethod
    def _position_blank_to_none(cls, value: str | None) -> str | None:
        return _blank_to_none(value, 30)

    @field_validator("category")
    @classmethod
    def _category_blank_to_none(cls, value: str | None) -> str | None:
        return _blank_to_none(value, 30)


class AthleteUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    position: str | None = Field(default=None, max_length=30)
    gender: AthleteGender | None = None
    category: str | None = Field(default=None, max_length=30)

    @field_validator("display_name")
    @classmethod
    def _name_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("El alias no puede estar vacío")
        return value

    @field_validator("position")
    @classmethod
    def _position_blank_to_none(cls, value: str | None) -> str | None:
        return _blank_to_none(value, 30)

    @field_validator("category")
    @classmethod
    def _category_blank_to_none(cls, value: str | None) -> str | None:
        return _blank_to_none(value, 30)


def _athlete_in_club(client: Client, club_id: str, athlete_id: str) -> dict:
    athlete = get_athlete(client, athlete_id)
    if not athlete or str(athlete.get("club_id")) != str(club_id):
        raise NotFoundError("Atleta no encontrado o sin acceso")
    return athlete


@router.get("/{club_id}/athletes", response_model=AthletesOut)
def list_athletes(
    club_id: str,
    status_filter: AthleteStatus = Query(default="active", alias="status"),
    limit: int | None = Query(default=None, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    ctx: AuthContext = Depends(require_club_role(["club_admin", "coach"])),
    client: Client = Depends(get_data_client),
):
    if limit is None and offset:
        raise InvalidInputError("El desplazamiento requiere indicar un límite")
    rows = list_club_athletes(
        client,
        club_id,
        status=None if status_filter == "all" else status_filter,
        limit=limit,
        offset=offset,
    )
    return {
        "club_id": club_id,
        "athletes": rows,
        "status": status_filter,
        "limit": limit,
        "offset": offset,
    }


@router.post(
    "/{club_id}/athletes",
    status_code=status.HTTP_201_CREATED,
    response_model=IdOut,
)
def create_athlete_endpoint(
    club_id: str,
    payload: AthleteCreate,
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    _: None = Depends(require_csrf_if_cookie),
    client: Client = Depends(get_data_client),
):
    athlete_id = create_athlete(
        client,
        club_id,
        payload.display_name,
        payload.birth_date.isoformat(),
        position=payload.position,
        gender=payload.gender,
        category=payload.category,
    )
    return {"id": athlete_id}


@router.patch("/{club_id}/athletes/{athlete_id}", response_model=IdOut)
def update_athlete_endpoint(
    club_id: str,
    athlete_id: str,
    payload: AthleteUpdate,
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    _: None = Depends(require_csrf_if_cookie),
    client: Client = Depends(get_data_client),
):
    _athlete_in_club(client, club_id, athlete_id)
    fields = payload.model_dump(exclude_unset=True)
    update_athlete(
        client,
        athlete_id,
        display_name=fields.get("display_name"),
        position=fields.get("position"),
        gender=fields.get("gender"),
        category=fields.get("category"),
    )
    return {"id": athlete_id}


@router.delete(
    "/{club_id}/athletes/{athlete_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_athlete_endpoint(
    club_id: str,
    athlete_id: str,
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    _: None = Depends(require_csrf_if_cookie),
    client: Client = Depends(get_data_client),
):
    _athlete_in_club(client, club_id, athlete_id)
    deactivate_athlete(client, athlete_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
