"""Atletas del club: listado, alta, edición y desactivación."""

from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from supabase import Client

from apps.auth.deps import AuthContext, require_club_role
from apps.auth.session import CSRF_FIELD, csrf_matches
from apps.core.errors import DomainError, InvalidInputError, NotFoundError, http_status
from apps.integrations.supabase.deps import get_data_client
from apps.services.f1_reads import get_club
from apps.services.f2_writes import create_athlete, deactivate_athlete, update_athlete
from apps.web.routes.common import athlete_in_club, render_athletes
from apps.web.templates import render
from apps.web.viewmodels import AthleteFormView

router = APIRouter()

_GENDERS = {"male", "female", "unspecified"}


def _club_or_404(client: Client, club_id: str) -> dict:
    club = get_club(client, club_id)
    if not club:
        raise NotFoundError("Club no encontrado o sin acceso.")
    return club


def _birth_date_ok(value: str) -> date | None:
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    today = date.today()
    oldest = (today - timedelta(days=100 * 366))
    youngest = today - timedelta(days=18 * 366)
    if parsed > youngest or parsed < oldest:
        return None
    return parsed


def _form_error(request: Request, club: dict, athlete: dict | None, form: dict, mode: str, error: str, status_code: int):
    return render(
        request,
        "athlete_form.html",
        AthleteFormView(mode, club, athlete, form, error).context(),
        status_code=status_code,
    )


@router.get("/clubs/{club_id}/athletes", response_class=HTMLResponse)
def athletes_page(
    request: Request,
    club_id: str,
    ctx: AuthContext = Depends(require_club_role(["club_admin", "coach"])),
    client: Client = Depends(get_data_client),
):
    return render_athletes(request, ctx, client, club_id)


@router.get("/clubs/{club_id}/athletes/new", response_class=HTMLResponse)
def athlete_new_page(
    request: Request,
    club_id: str,
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    client: Client = Depends(get_data_client),
):
    club = _club_or_404(client, club_id)
    today = date.today()
    try:
        birth_date_max = today.replace(year=today.year - 18)
    except ValueError:
        birth_date_max = today.replace(year=today.year - 18, month=2, day=28)
    form = {"display_name": "", "position": "", "birth_date": "",
            "birth_date_max": birth_date_max.isoformat(),
            "gender": "unspecified", "category": ""}
    view = AthleteFormView("new", club, None, form)
    return render(request, "athlete_form.html", view.context())


def _validate_payload(
    display_name: str,
    birth_date: str,
    position: str,
    gender: str,
    category: str,
    *,
    require_birth_date: bool,
) -> tuple[str | None, str | None, str | None, str | None, str | None]:
    display = display_name.strip()
    if not 2 <= len(display) <= 120:
        raise InvalidInputError("El nombre debe tener entre 2 y 120 caracteres.")

    position_value = position.strip() or None
    if position_value is not None and len(position_value) > 30:
        raise InvalidInputError("La posición debe tener 30 caracteres o menos.")

    category_value = category.strip() or None
    if category_value is not None and len(category_value) > 30:
        raise InvalidInputError("La categoría debe tener 30 caracteres o menos.")

    gender_value = gender.strip().lower() or "unspecified"
    if gender_value not in _GENDERS:
        raise InvalidInputError("El género no es válido.")

    parsed_birth: date | None = None
    if require_birth_date:
        if not birth_date.strip():
            raise InvalidInputError("La fecha de nacimiento es obligatoria.")
        parsed_birth = _birth_date_ok(birth_date.strip())
        if parsed_birth is None:
            raise InvalidInputError("El atleta debe ser mayor de edad (entre 18 y 100 años).")

    return display, (parsed_birth.isoformat() if parsed_birth else None), position_value, gender_value, category_value


@router.post("/clubs/{club_id}/athletes", response_class=HTMLResponse)
def athlete_create_submit(
    request: Request,
    club_id: str,
    display_name: str = Form(""),
    birth_date: str = Form(""),
    position: str = Form(""),
    gender: str = Form("unspecified"),
    category: str = Form(""),
    csrf_token: str = Form("", alias=CSRF_FIELD),
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    client: Client = Depends(get_data_client),
):
    club = _club_or_404(client, club_id)
    form = {
        "display_name": display_name,
        "position": position,
        "birth_date": birth_date,
        "gender": gender,
        "category": category,
    }
    if not csrf_matches(request, csrf_token):
        return _form_error(request, club, None, form, "new", "El formulario expiró. Inténtalo de nuevo.", status.HTTP_403_FORBIDDEN)
    try:
        display, parsed_birth, position_value, gender_value, category_value = _validate_payload(
            display_name, birth_date, position, gender, category, require_birth_date=True
        )
        create_athlete(client, club_id, display, parsed_birth, position_value, gender_value, category_value)
    except InvalidInputError as exc:
        return _form_error(request, club, None, form, "new", exc.message, status.HTTP_400_BAD_REQUEST)
    except DomainError as exc:
        return _form_error(request, club, None, form, "new", exc.message, http_status(exc))

    return RedirectResponse(f"/clubs/{club_id}/athletes", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/clubs/{club_id}/athletes/{athlete_id}/edit", response_class=HTMLResponse)
def athlete_edit_page(
    request: Request,
    club_id: str,
    athlete_id: str,
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    client: Client = Depends(get_data_client),
):
    club = _club_or_404(client, club_id)
    athlete = athlete_in_club(client, club_id, athlete_id)
    form = {
        "display_name": athlete.get("display_name") or "",
        "position": athlete.get("position") or "",
        "gender": athlete.get("gender") or "unspecified",
        "category": athlete.get("category") or "",
    }
    view = AthleteFormView("edit", club, athlete, form)
    return render(request, "athlete_form.html", view.context())


@router.post("/clubs/{club_id}/athletes/{athlete_id}/edit", response_class=HTMLResponse)
def athlete_edit_submit(
    request: Request,
    club_id: str,
    athlete_id: str,
    display_name: str = Form(""),
    position: str = Form(""),
    gender: str = Form("unspecified"),
    category: str = Form(""),
    csrf_token: str = Form("", alias=CSRF_FIELD),
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    client: Client = Depends(get_data_client),
):
    club = _club_or_404(client, club_id)
    athlete = athlete_in_club(client, club_id, athlete_id)
    form = {"display_name": display_name, "position": position, "gender": gender, "category": category}
    if not csrf_matches(request, csrf_token):
        return _form_error(request, club, athlete, form, "edit", "El formulario expiró. Inténtalo de nuevo.", status.HTTP_403_FORBIDDEN)
    try:
        display, _, position_value, gender_value, category_value = _validate_payload(
            display_name, "", position, gender, category, require_birth_date=False
        )
        update_athlete(client, athlete_id, display, position_value, gender_value, category_value)
    except InvalidInputError as exc:
        return _form_error(request, club, athlete, form, "edit", exc.message, status.HTTP_400_BAD_REQUEST)
    except DomainError as exc:
        return _form_error(request, club, athlete, form, "edit", exc.message, http_status(exc))

    return RedirectResponse(f"/clubs/{club_id}/athletes", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/clubs/{club_id}/athletes/{athlete_id}/deactivate", response_class=HTMLResponse)
def athlete_deactivate_submit(
    request: Request,
    club_id: str,
    athlete_id: str,
    csrf_token: str = Form("", alias=CSRF_FIELD),
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    client: Client = Depends(get_data_client),
):
    if not csrf_matches(request, csrf_token):
        return render_athletes(
            request,
            ctx,
            client,
            club_id,
            error="El formulario expiró. Inténtalo de nuevo.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    athlete_in_club(client, club_id, athlete_id)
    try:
        deactivate_athlete(client, athlete_id)
    except DomainError as exc:
        return render_athletes(
            request, ctx, client, club_id, error=exc.message, status_code=http_status(exc)
        )

    return RedirectResponse(f"/clubs/{club_id}/athletes", status_code=status.HTTP_303_SEE_OTHER)
