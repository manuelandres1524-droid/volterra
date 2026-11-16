"""Sesión del frontend: cookies HttpOnly y CSRF double-submit.

El navegador nunca recibe el token en el HTML ni en JavaScript. El access token
y el refresh token viajan en cookies ``HttpOnly``; la cookie de CSRF es legible
por el navegador y se compara contra el valor enviado en el formulario o en la
cabecera ``X-CSRF-Token``.

Este módulo no autoriza: solo transporta la sesión. La autorización efectiva
sigue en RLS + RPC del proyecto Supabase.
"""

from __future__ import annotations

import hmac
import secrets
from dataclasses import dataclass

import httpx
from fastapi import Request, Response

from apps.core.config import settings
from apps.core.errors import (
    RateLimitedError,
    UnauthenticatedError,
    UnavailableError,
)

ACCESS_COOKIE = "volterra_access"
REFRESH_COOKIE = "volterra_refresh"
CSRF_COOKIE = "volterra_csrf"
CSRF_FIELD = "csrf_token"
CSRF_HEADER = "X-CSRF-Token"

_COOKIE_PATH = "/"


@dataclass(frozen=True)
class SessionTokens:
    access_token: str
    refresh_token: str | None
    expires_in: int


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def get_csrf_token(request: Request) -> str | None:
    return request.cookies.get(CSRF_COOKIE)


def csrf_matches(request: Request, submitted: str | None) -> bool:
    """Compara el token enviado con la cookie usando tiempo constante."""
    expected = get_csrf_token(request)
    if not expected or not submitted:
        return False
    return hmac.compare_digest(expected, submitted)


def set_csrf_cookie(response: Response, token: str | None = None) -> str:
    value = token or new_csrf_token()
    response.set_cookie(
        CSRF_COOKIE,
        value,
        max_age=settings.CSRF_COOKIE_MAX_AGE_SECONDS,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        path=_COOKIE_PATH,
    )
    return value


def _set_token_cookie(response: Response, name: str, value: str, max_age: int) -> None:
    response.set_cookie(
        name,
        value,
        max_age=max_age,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        path=_COOKIE_PATH,
    )


def set_session_cookies(response: Response, tokens: SessionTokens) -> None:
    _set_token_cookie(response, ACCESS_COOKIE, tokens.access_token, max(tokens.expires_in, 60))
    if tokens.refresh_token:
        _set_token_cookie(
            response,
            REFRESH_COOKIE,
            tokens.refresh_token,
            settings.REFRESH_COOKIE_MAX_AGE_SECONDS,
        )


def clear_session_cookies(response: Response) -> None:
    for name in (ACCESS_COOKIE, REFRESH_COOKIE):
        response.delete_cookie(
            name,
            path=_COOKIE_PATH,
            secure=settings.COOKIE_SECURE,
            httponly=True,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )


def get_access_token(request: Request) -> str | None:
    value = request.cookies.get(ACCESS_COOKIE)
    return value.strip() if value and value.strip() else None


def get_refresh_token(request: Request) -> str | None:
    value = request.cookies.get(REFRESH_COOKIE)
    return value.strip() if value and value.strip() else None


def _auth_url() -> str:
    base = settings.SUPABASE_URL.rstrip("/")
    if not base or not settings.SUPABASE_PUBLISHABLE_KEY:
        raise UnavailableError("El servicio de autenticación no está configurado.")
    return f"{base}/auth/v1/token"


async def _post_token(grant_type: str, payload: dict[str, str]) -> dict:
    url = _auth_url()
    headers = {
        "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=settings.SUPABASE_AUTH_TIMEOUT_SECONDS) as client:
            response = await client.post(
                url,
                params={"grant_type": grant_type},
                json=payload,
                headers=headers,
            )
    except httpx.HTTPError as exc:
        raise UnavailableError("No se pudo contactar el servicio de autenticación.") from exc

    if response.status_code >= 500:
        raise UnavailableError("El servicio de autenticación no está disponible.")
    if response.status_code == 429:
        raise RateLimitedError(300, "Demasiados intentos. Espera unos minutos.")
    if response.status_code >= 400:
        raise UnauthenticatedError(_auth_error_message(response))

    try:
        data = response.json()
    except ValueError as exc:
        raise UnavailableError("Respuesta de autenticación inválida.") from exc

    access_token = data.get("access_token")
    if not access_token:
        raise UnavailableError("La autenticación no devolvió una sesión válida.")

    expires_in = data.get("expires_in")
    try:
        expires_in = int(expires_in) if expires_in is not None else 3600
    except (TypeError, ValueError):
        expires_in = 3600

    return {
        "access_token": str(access_token),
        "refresh_token": data.get("refresh_token"),
        "expires_in": expires_in,
    }


def _auth_error_message(response: httpx.Response) -> str:
    """Traduce errores de Supabase sin filtrar detalles internos."""
    try:
        data = response.json()
    except ValueError:
        data = {}

    code = str(data.get("error_code") or data.get("error") or "")
    message = str(data.get("msg") or data.get("message") or "")
    joined = f"{code} {message}".lower()

    if "email_not_confirmed" in joined or "not confirmed" in joined:
        return "Debes confirmar tu correo antes de iniciar sesión."
    if "invalid login credentials" in joined or "invalid_grant" in joined:
        return "Correo o contraseña incorrectos."
    if "rate limit" in joined or "too many" in joined:
        return "Demasiados intentos. Espera unos minutos."
    return "No se pudo iniciar sesión."


async def sign_in(email: str, password: str) -> SessionTokens:
    data = await _post_token("password", {"email": email, "password": password})
    return SessionTokens(**data)


async def refresh_session(refresh_token: str) -> SessionTokens:
    try:
        data = await _post_token("refresh_token", {"refresh_token": refresh_token})
    except UnauthenticatedError as exc:
        raise UnauthenticatedError("La sesión expiró. Vuelve a iniciar sesión.") from exc
    return SessionTokens(**data)


async def revoke_session(access_token: str) -> None:
    """Cierra la sesión en Supabase; un fallo no bloquea el logout local."""
    base = settings.SUPABASE_URL.rstrip("/")
    if not base or not settings.SUPABASE_PUBLISHABLE_KEY or not access_token:
        return
    headers = {
        "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
        "Authorization": f"Bearer {access_token}",
    }
    try:
        async with httpx.AsyncClient(timeout=settings.SUPABASE_AUTH_TIMEOUT_SECONDS) as client:
            await client.post(f"{base}/auth/v1/logout", headers=headers)
    except httpx.HTTPError:
        return
