"""Miembros de un club: listado, alta, cambio de rol y cierre."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from supabase import Client

from apps.auth.deps import AuthContext, require_club_role
from apps.auth.session import CSRF_FIELD, csrf_matches
from apps.core.errors import DomainError, InvalidInputError, http_status
from apps.integrations.supabase.deps import get_data_client
from apps.services.f1_writes import add_member, change_member_role, end_membership
from apps.web.routes.common import (
    assignable_roles,
    ensure_uuid,
    membership_in_club,
    render_members,
)

router = APIRouter()


@router.get("/clubs/{club_id}/members", response_class=HTMLResponse)
def members_page(
    request: Request,
    club_id: str,
    ctx: AuthContext = Depends(require_club_role(["club_admin", "coach"])),
    client: Client = Depends(get_data_client),
):
    return render_members(request, ctx, client, club_id)


@router.post("/clubs/{club_id}/members", response_class=HTMLResponse)
def member_add_submit(
    request: Request,
    club_id: str,
    user_id: str = Form(""),
    role: str = Form(""),
    csrf_token: str = Form("", alias=CSRF_FIELD),
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    client: Client = Depends(get_data_client),
):
    if not csrf_matches(request, csrf_token):
        return render_members(
            request,
            ctx,
            client,
            club_id,
            error="El formulario expiró. Inténtalo de nuevo.",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    if role not in assignable_roles(ctx):
        return render_members(
            request,
            ctx,
            client,
            club_id,
            error="No puedes asignar ese rol.",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    try:
        ensure_uuid(user_id.strip())
    except InvalidInputError as exc:
        return render_members(
            request,
            ctx,
            client,
            club_id,
            error=exc.message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        add_member(client, club_id, user_id.strip(), role)
    except DomainError as exc:
        return render_members(
            request, ctx, client, club_id, error=exc.message, status_code=http_status(exc)
        )

    return RedirectResponse(f"/clubs/{club_id}/members", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/clubs/{club_id}/members/{membership_id}/role", response_class=HTMLResponse)
def member_role_submit(
    request: Request,
    club_id: str,
    membership_id: str,
    role: str = Form(""),
    csrf_token: str = Form("", alias=CSRF_FIELD),
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    client: Client = Depends(get_data_client),
):
    if not csrf_matches(request, csrf_token):
        return render_members(
            request,
            ctx,
            client,
            club_id,
            error="El formulario expiró. Inténtalo de nuevo.",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    if role not in assignable_roles(ctx):
        return render_members(
            request,
            ctx,
            client,
            club_id,
            error="No puedes asignar ese rol.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    membership_in_club(client, club_id, membership_id)
    try:
        change_member_role(client, membership_id, role)
    except DomainError as exc:
        return render_members(
            request, ctx, client, club_id, error=exc.message, status_code=http_status(exc)
        )

    return RedirectResponse(f"/clubs/{club_id}/members", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/clubs/{club_id}/members/{membership_id}/end", response_class=HTMLResponse)
def member_end_submit(
    request: Request,
    club_id: str,
    membership_id: str,
    csrf_token: str = Form("", alias=CSRF_FIELD),
    ctx: AuthContext = Depends(require_club_role(["club_admin"])),
    client: Client = Depends(get_data_client),
):
    if not csrf_matches(request, csrf_token):
        return render_members(
            request,
            ctx,
            client,
            club_id,
            error="El formulario expiró. Inténtalo de nuevo.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    membership_in_club(client, club_id, membership_id)
    try:
        end_membership(client, membership_id)
    except DomainError as exc:
        return render_members(
            request, ctx, client, club_id, error=exc.message, status_code=http_status(exc)
        )

    return RedirectResponse(f"/clubs/{club_id}/members", status_code=status.HTTP_303_SEE_OTHER)
