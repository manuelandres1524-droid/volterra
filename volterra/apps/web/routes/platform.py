"""Panel de plataforma (solo platform_admin)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from apps.auth.deps import AuthContext, require_platform_admin
from apps.web.templates import render

router = APIRouter()


@router.get("/platform", response_class=HTMLResponse)
def platform_page(
    request: Request,
    ctx: AuthContext = Depends(require_platform_admin),
):
    return render(request, "platform.html")
