"""Rutas de sesión: login, logout y renovación del token."""

from __future__ import annotations

from fastapi import APIRouter, Form, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from apps.auth.session import (
    CSRF_FIELD,
    CSRF_HEADER,
    clear_session_cookies,
    csrf_matches,
    get_access_token,
    get_refresh_token,
    refresh_session,
    revoke_session,
    set_csrf_cookie,
    set_session_cookies,
    sign_in,
)
from apps.core.errors import DomainError, ForbiddenError, UnauthenticatedError, http_status
from apps.web.routes.common import safe_next
from apps.web.templates import render
from apps.web.viewmodels import LoginView

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def root():
    return RedirectResponse("/me", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, next_url: str | None = None):
    return render(request, "login.html", LoginView(next_url=safe_next(next_url)).context())


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next_url: str = Form("/me"),
    csrf_token: str = Form("", alias=CSRF_FIELD),
):
    safe_target = safe_next(next_url)

    if not csrf_matches(request, csrf_token):
        return render(
            request,
            "login.html",
            LoginView(
                error="El formulario expiró. Inténtalo de nuevo.",
                email=email,
                next_url=safe_target,
            ).context(),
            status_code=status.HTTP_403_FORBIDDEN,
        )

    try:
        tokens = await sign_in(email.strip(), password)
    except DomainError as exc:
        return render(
            request,
            "login.html",
            LoginView(error=exc.message, email=email, next_url=safe_target).context(),
            status_code=http_status(exc),
        )

    response = RedirectResponse(safe_target, status_code=status.HTTP_303_SEE_OTHER)
    set_session_cookies(response, tokens)
    set_csrf_cookie(response)
    return response


@router.post("/logout")
async def logout_submit(
    request: Request,
    csrf_token: str = Form("", alias=CSRF_FIELD),
):
    if not csrf_matches(request, csrf_token):
        # El formulario de logout no tiene una página propia: se reutiliza la de error.
        raise ForbiddenError("El formulario expiró. Inténtalo de nuevo.")

    access_token = get_access_token(request)
    if access_token:
        await revoke_session(access_token)

    response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    clear_session_cookies(response)
    set_csrf_cookie(response)
    return response


@router.post("/auth/refresh")
async def refresh(request: Request):
    submitted = request.headers.get(CSRF_HEADER)
    if not csrf_matches(request, submitted):
        return JSONResponse({"detail": "CSRF inválido"}, status_code=403)

    refresh_token = get_refresh_token(request)
    if not refresh_token:
        response = JSONResponse({"detail": "No hay sesión que renovar"}, status_code=401)
        clear_session_cookies(response)
        return response

    try:
        tokens = await refresh_session(refresh_token)
    except DomainError as exc:
        response = JSONResponse({"detail": exc.message}, status_code=http_status(exc))
        if isinstance(exc, UnauthenticatedError):
            clear_session_cookies(response)
        return response

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    set_session_cookies(response, tokens)
    return response
