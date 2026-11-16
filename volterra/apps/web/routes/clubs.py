"""Páginas y formularios de club: alta, edición y detalle."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from supabase import Client

from apps.auth.deps import AuthContext, require_club_role, require_platform_admin
from apps.auth.session import CSRF_FIELD, csrf_matches
from apps.core.errors import DomainError, NotFoundError, http_status
from apps.integrations.supabase.deps import get_data_client
from apps.services.f1_reads import get_club
from apps.services.f1_writes import create_club, update_club
from apps.web.routes.common import normalize_country
from apps.web.templates import render
from apps.web.viewmodels import ClubFormView, ClubView

router = APIRouter()

_CLUB_STATUSES = {"active", "suspended", "closed"}


@router.get("/clubs/new", response_class=HTMLResponse)
def club_new_page(
    request: Request,
    ctx: AuthContext = Depends(require_platform_admin),
):
    view = ClubFormView("new", None, {"name": "", "city": "", "country": "CO"})
    return render(request, "club_form.html", view.context())


@router.post("/clubs", response_class=HTMLResponse)
def club_create_submit(
    request: Request,
    name: str = Form(""),
    city: str = Form(""),
    country: str = Form("CO"),
    csrf_token: str = Form("", alias=CSRF_FIELD),
    ctx: AuthContext = Depends(require_platform_admin),
    client: Client = Depends(get_data_client),
):
    form = {"name": name, "city": city, "country": country}
    if not csrf_matches(request, csrf_token):
        return render(
            request,
            "club_form.html",
            ClubFormView("new", None, form, "El formulario expiró. Inténtalo de nuevo.").context(),
            status_code=status.HTTP_403_FORBIDDEN,
        )

    normalized_country = normalize_country(country)
    if normalized_country is None:
        return render(
            request,
            "club_form.html",
            ClubFormView("new", None, form, "El país debe tener dos letras.").context(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        club_id = create_club(client, name.strip(), city.strip() or None, normalized_country)
    except DomainError as exc:
        return render(
            request,
            "club_form.html",
            ClubFormView("new", None, form, exc.message).context(),
            status_code=http_status(exc),
        )

    return RedirectResponse(f"/clubs/{club_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/clubs/{club_id}/edit", response_class=HTMLResponse)
def club_edit_page(
    request: Request,
    club_id: str,
    ctx: AuthContext = Depends(require_platform_admin),
    client: Client = Depends(get_data_client),
):
    club = get_club(client, club_id)
    if not club:
        raise NotFoundError("Club no encontrado o sin acceso.")

    view = ClubFormView("edit", club, dict(club))
    return render(request, "club_form.html", view.context())


@router.post("/clubs/{club_id}/edit", response_class=HTMLResponse)
def club_edit_submit(
    request: Request,
    club_id: str,
    name: str = Form(""),
    city: str = Form(""),
    country: str = Form("CO"),
    club_status: str = Form("active"),
    csrf_token: str = Form("", alias=CSRF_FIELD),
    ctx: AuthContext = Depends(require_platform_admin),
    client: Client = Depends(get_data_client),
):
    club = get_club(client, club_id)
    if not club:
        raise NotFoundError("Club no encontrado o sin acceso.")

    form = {"name": name, "city": city, "country": country, "status": club_status}
    if not csrf_matches(request, csrf_token):
        return render(
            request,
            "club_form.html",
            ClubFormView("edit", club, form, "El formulario expiró. Inténtalo de nuevo.").context(),
            status_code=status.HTTP_403_FORBIDDEN,
        )

    normalized_country = normalize_country(country)
    if normalized_country is None:
        return render(
            request,
            "club_form.html",
            ClubFormView("edit", club, form, "El país debe tener dos letras.").context(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if club_status not in _CLUB_STATUSES:
        return render(
            request,
            "club_form.html",
            ClubFormView("edit", club, form, "Estado de club no válido.").context(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        update_club(
            client,
            club_id,
            name=name.strip(),
            city=city.strip(),
            country=normalized_country,
            club_status=club_status,
        )
    except DomainError as exc:
        return render(
            request,
            "club_form.html",
            ClubFormView("edit", club, form, exc.message).context(),
            status_code=http_status(exc),
        )

    return RedirectResponse(f"/clubs/{club_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/clubs/{club_id}", response_class=HTMLResponse)
def club_page(
    request: Request,
    club_id: str,
    ctx: AuthContext = Depends(require_club_role(["club_admin", "coach"])),
    client: Client = Depends(get_data_client),
):
    club = get_club(client, club_id)
    if not club:
        raise NotFoundError("Club no encontrado o sin acceso.")

    view = ClubView(club=club, can_edit=ctx.is_platform_admin)
    return render(request, "club_detail.html", view.context())
