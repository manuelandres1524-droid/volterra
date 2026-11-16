"""Rutas de sesión: login, logout y renovación del token."""

from __future__ import annotations

from fastapi import APIRouter, Form, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from apps.auth.session import (
    CSRF_FIELD,
    CSRF_HEADER,
    clear_session_cookies,
    csrf_matches,
    enroll_mfa,
    get_access_token,
    get_csrf_token,
    get_refresh_token,
    list_mfa_factors,
    refresh_session,
    request_password_reset,
    revoke_session,
    set_csrf_cookie,
    set_session_cookies,
    sign_in,
    unenroll_mfa,
    update_password,
    verify_mfa,
)
from apps.core.errors import (
    DomainError,
    ForbiddenError,
    UnauthenticatedError,
    http_status,
)
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


# ─── MFA (TOTP) ────────────────────────────────────────────────────────────────

@router.get("/mfa/enroll", response_class=HTMLResponse)
async def mfa_enroll_page(request: Request):
    access_token = get_access_token(request)
    if not access_token:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    try:
        data = await enroll_mfa(access_token)
    except DomainError as exc:
        return render(
            request,
            "error.html",
            {"title": "Error MFA", "message": exc.message},
            status_code=http_status(exc),
        )

    # Supabase returns: id, type, totp (secret, uri, qr_code)
    factor_id = data.get("id")
    totp = data.get("totp", {})
    uri = totp.get("uri", "")
    secret = totp.get("secret", "")

    return render(
        request,
        "mfa_enroll.html",
        {
            "factor_id": factor_id,
            "uri": uri,
            "secret": secret,
            "csrf_token": get_csrf_token(request) or set_csrf_cookie(Response()),
        },
    )


@router.post("/mfa/verify", response_class=HTMLResponse)
async def mfa_verify_submit(
    request: Request,
    factor_id: str = Form(...),
    code: str = Form(...),
    csrf_token: str = Form("", alias=CSRF_FIELD),
):
    if not csrf_matches(request, csrf_token):
        return RedirectResponse("/mfa/enroll", status_code=status.HTTP_303_SEE_OTHER)

    access_token = get_access_token(request)
    if not access_token:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    try:
        tokens = await verify_mfa(access_token, factor_id, code.strip())
    except DomainError as exc:
        return render(
            request,
            "mfa_enroll.html",
            {
                "factor_id": factor_id,
                "error": exc.message,
                "csrf_token": get_csrf_token(request) or "",
            },
            status_code=http_status(exc),
        )

    response = RedirectResponse("/me", status_code=status.HTTP_303_SEE_OTHER)
    set_session_cookies(response, tokens)
    set_csrf_cookie(response)
    return response


@router.get("/mfa/factors", response_class=HTMLResponse)
async def mfa_factors_page(request: Request):
    access_token = get_access_token(request)
    if not access_token:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    factors = await list_mfa_factors(access_token)
    return render(
        request,
        "mfa_factors.html",
        {
            "factors": factors,
            "csrf_token": get_csrf_token(request) or "",
        },
    )


@router.post("/mfa/unenroll")
async def mfa_unenroll_submit(
    request: Request,
    factor_id: str = Form(...),
    csrf_token: str = Form("", alias=CSRF_FIELD),
):
    if not csrf_matches(request, csrf_token):
        raise ForbiddenError("El formulario expiró. Inténtalo de nuevo.")

    access_token = get_access_token(request)
    if not access_token:
        raise UnauthenticatedError("No hay sesión activa.")

    success = await unenroll_mfa(access_token, factor_id)
    if not success:
        raise DomainError("No se pudo desactivar MFA.")

    return RedirectResponse("/mfa/factors", status_code=status.HTTP_303_SEE_OTHER)


# ─── Password Recovery ─────────────────────────────────────────────────────────

@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return render(request, "forgot_password.html", {"csrf_token": get_csrf_token(request) or ""})


@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password_submit(
    request: Request,
    email: str = Form(...),
    csrf_token: str = Form("", alias=CSRF_FIELD),
):
    if not csrf_matches(request, csrf_token):
        return render(
            request,
            "forgot_password.html",
            {"error": "El formulario expiró. Inténtalo de nuevo.", "csrf_token": get_csrf_token(request) or ""},
            status_code=status.HTTP_403_FORBIDDEN,
        )

    try:
        await request_password_reset(email.strip())
    except DomainError as exc:
        return render(
            request,
            "forgot_password.html",
            {"error": exc.message, "csrf_token": get_csrf_token(request) or ""},
            status_code=http_status(exc),
        )

    return render(
        request,
        "forgot_password.html",
        {
            "success": "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.",
            "csrf_token": get_csrf_token(request) or "",
        },
    )


@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request, access_token: str | None = None):
    if not access_token:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    return render(
        request,
        "reset_password.html",
        {"access_token": access_token, "csrf_token": get_csrf_token(request) or ""},
    )


@router.post("/reset-password", response_class=HTMLResponse)
async def reset_password_submit(
    request: Request,
    access_token: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    csrf_token: str = Form("", alias=CSRF_FIELD),
):
    if not csrf_matches(request, csrf_token):
        return render(
            request,
            "reset_password.html",
            {"error": "El formulario expiró. Inténtalo de nuevo.", "access_token": access_token, "csrf_token": get_csrf_token(request) or ""},
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if password != password_confirm:
        return render(
            request,
            "reset_password.html",
            {"error": "Las contraseñas no coinciden.", "access_token": access_token, "csrf_token": get_csrf_token(request) or ""},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if len(password) < 8:
        return render(
            request,
            "reset_password.html",
            {"error": "La contraseña debe tener al menos 8 caracteres.", "access_token": access_token, "csrf_token": get_csrf_token(request) or ""},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        await update_password(access_token, password)
    except DomainError as exc:
        return render(
            request,
            "reset_password.html",
            {"error": exc.message, "access_token": access_token, "csrf_token": get_csrf_token(request) or ""},
            status_code=http_status(exc),
        )

    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
