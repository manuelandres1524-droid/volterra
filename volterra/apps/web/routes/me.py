"""Páginas de inicio y listado de clubes del usuario."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from supabase import Client

from apps.auth.deps import AuthContext, get_auth_context
from apps.integrations.supabase.deps import get_data_client
from apps.services.f1_reads import get_profile, list_my_clubs
from apps.web.templates import render
from apps.web.viewmodels import ClubsView, MeView

router = APIRouter()


@router.get("/me", response_class=HTMLResponse)
def me_page(
    request: Request,
    ctx: AuthContext = Depends(get_auth_context),
    client: Client = Depends(get_data_client),
):
    profile = get_profile(client, ctx.user_id)
    memberships = list_my_clubs(client, ctx.memberships)
    view = MeView(
        display_name=profile.get("display_name") if profile else None,
        memberships=memberships,
    )
    return render(request, "me.html", view.context())


@router.get("/clubs", response_class=HTMLResponse)
def clubs_page(
    request: Request,
    ctx: AuthContext = Depends(get_auth_context),
    client: Client = Depends(get_data_client),
):
    memberships = list_my_clubs(client, ctx.memberships)
    return render(request, "clubs.html", ClubsView(memberships=memberships).context())
