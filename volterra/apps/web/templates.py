"""Plantillas y utilidades de presentación del frontend Jinja2."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import Request
from starlette.templating import Jinja2Templates

from apps.auth.session import get_csrf_token, new_csrf_token, set_csrf_cookie

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Las fechas se guardan en UTC; se muestran en la zona del club (Colombia).
DISPLAY_TZ = ZoneInfo("America/Bogota")

ROLE_LABELS = {
    "club_admin": "Administrador de club",
    "coach": "Entrenador",
}

STATUS_LABELS = {
    "active": "Activo",
    "suspended": "Suspendido",
    "closed": "Cerrado",
}

GENDER_LABELS = {
    "male": "Hombre",
    "female": "Mujer",
    "unspecified": "Sin especificar",
}

ATHLETE_STATUS_LABELS = {
    "active": "Activo",
    "inactive": "Inactivo",
}


def _fecha(value: Any) -> str:
    if not value:
        return "—"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    try:
        if value.tzinfo is not None:
            value = value.astimezone(DISPLAY_TZ)
        return value.strftime("%d/%m/%Y")
    except AttributeError:
        return str(value)


def _role_label(value: str | None) -> str:
    return ROLE_LABELS.get(value or "", value or "Sin rol")


def _status_label(value: str | None) -> str:
    return STATUS_LABELS.get(value or "", value or "Sin estado")


def _gender_label(value: str | None) -> str:
    return GENDER_LABELS.get(value or "", value or "Sin especificar")


def _athlete_status_label(value: str | None) -> str:
    return ATHLETE_STATUS_LABELS.get(value or "", value or "Sin estado")


templates.env.filters["fecha"] = _fecha
templates.env.globals["role_label"] = _role_label
templates.env.globals["status_label"] = _status_label
templates.env.globals["gender_label"] = _gender_label
templates.env.globals["athlete_status_label"] = _athlete_status_label


def render(
    request: Request,
    name: str,
    context: dict[str, Any] | None = None,
    *,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
) -> Any:
    """Renderiza una plantilla y garantiza que exista cookie de CSRF."""
    token = get_csrf_token(request) or new_csrf_token()
    payload: dict[str, Any] = {
        "request": request,
        "auth": getattr(request.state, "auth", None),
        "csrf_token": token,
    }
    if context:
        payload.update(context)

    response = templates.TemplateResponse(
        request,
        name,
        payload,
        status_code=status_code,
        headers=headers,
    )
    if get_csrf_token(request) != token:
        set_csrf_cookie(response, token)
    return response
