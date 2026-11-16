from fastapi import Depends, Header, Request

from apps.auth.session import ACCESS_COOKIE, CSRF_HEADER, csrf_matches
from apps.core.errors import (
    ForbiddenError,
    RateLimitedError,
    UnauthenticatedError,
    UnavailableError,
)
from apps.core.ratelimit import evaluate, user_scope
from apps.core.security import (
    verify_supabase_jwt_strict,
    JWTValidationError,
    JWTUnavailableError,
)
from apps.integrations.supabase.per_request import get_supabase_for_user


def _as_bool(value: object) -> bool:
    """Normaliza la respuesta escalar de PostgREST a booleano."""
    if isinstance(value, list):
        value = value[0] if value else False
    if isinstance(value, dict):
        value = next(iter(value.values()), False)
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


class AuthContext:
    def __init__(
        self,
        user_id: str,
        email: str | None = None,
        is_platform_admin: bool = False,
        memberships: list[dict] | None = None,
        token: str = "",
    ):
        self.user_id = user_id
        self.email = email
        self.is_platform_admin = is_platform_admin
        self.memberships = memberships or []
        self.token = token


async def get_auth_context(request: Request, authorization: str | None = Header(default=None)) -> AuthContext:
    """Obtiene el contexto de autenticación desde ``Bearer`` o cookie de sesión.

    La cabecera ``Authorization`` tiene prioridad. Si está presente pero no es
    un ``Bearer`` válido, se rechaza aunque exista una cookie: no se mezclan
    dos identidades en la misma petición.
    """
    token: str | None = None
    if authorization is not None:
        if not authorization.startswith("Bearer "):
            raise UnauthenticatedError()
        token = authorization.removeprefix("Bearer ").strip()
        if not token:
            raise UnauthenticatedError("Token vacío")
    else:
        cookies = getattr(request, "cookies", {}) or {}
        cookie_token = cookies.get(ACCESS_COOKIE)
        token = cookie_token.strip() if cookie_token and cookie_token.strip() else None

    if not token:
        raise UnauthenticatedError()

    try:
        payload = await verify_supabase_jwt_strict(token)
    except JWTUnavailableError as exc:
        raise UnavailableError("No se pudo verificar el token") from exc
    except JWTValidationError as exc:
        raise UnauthenticatedError("Token inválido") from exc

    uid = payload.get("sub")
    email = payload.get("email")
    if not uid:
        raise UnauthenticatedError("Token inválido")

    # Límite por usuario antes de consultar Supabase: la identidad ya está
    # verificada y una ráfaga no debe amplificar consultas a la base de datos.
    limit = evaluate(user_scope(request), uid)
    if limit is not None and not limit.allowed:
        raise RateLimitedError(
            limit.retry_after,
            f"Demasiadas peticiones. Inténtalo de nuevo en {limit.retry_after} segundos.",
        )

    try:
        client = get_supabase_for_user(token)
    except Exception as exc:
        raise UnavailableError("Error al inicializar el cliente de datos") from exc
    # Un solo cliente por petición: las rutas lo reutilizan vía
    # ``apps.integrations.supabase.deps.get_data_client``.
    request.state.data_client = client

    is_pa = False
    try:
        r = client.rpc("fn_is_platform_admin").execute()
        is_pa = _as_bool(r.data)
    except Exception as exc:
        # No ocultar como "sin permisos": si la RPC falla, el contexto no es fiable.
        raise UnavailableError("Error al verificar permisos") from exc

    memberships: list[dict] = []
    try:
        r = (
            client.table("club_memberships")
            .select("club_id, role, started_at, ended_at, user_id")
            .eq("user_id", uid)
            .is_("ended_at", "null")
            .execute()
        )
        memberships = r.data or []
    except Exception as exc:
        raise UnavailableError("Error al verificar membresías") from exc

    ctx = AuthContext(user_id=uid, email=email, is_platform_admin=is_pa, memberships=memberships, token=token)
    request.state.auth = ctx
    return ctx


def require_auth(ctx: AuthContext = Depends(get_auth_context)) -> AuthContext:
    return ctx


async def require_csrf_if_cookie(request: Request) -> None:
    """Exige CSRF en escrituras autenticadas por cookie.

    Un cliente con ``Authorization: Bearer`` no envía cookies y no puede sufrir
    CSRF. Si la identidad viene de la cookie de sesión, la escritura exige la
    cabecera ``X-CSRF-Token`` con el patrón double-submit.
    """
    if request.headers.get("authorization"):
        return
    if not csrf_matches(request, request.headers.get(CSRF_HEADER)):
        raise ForbiddenError("CSRF inválido")


def require_platform_admin(ctx: AuthContext = Depends(get_auth_context)) -> AuthContext:
    if not ctx.is_platform_admin:
        raise ForbiddenError("Se requiere platform_admin")
    return ctx


def require_club_role(allowed: list[str]):
    async def _dep(club_id: str, ctx: AuthContext = Depends(get_auth_context)):
        if ctx.is_platform_admin:
            return ctx
        for m in ctx.memberships:
            if m.get("ended_at") is not None:
                continue
            if str(m.get("club_id")) == str(club_id) and m.get("role") in allowed:
                return ctx
        raise ForbiddenError("Sin permisos para este club")
    return _dep


def require_same_club_or_pa():
    async def _dep(club_id: str, ctx: AuthContext = Depends(get_auth_context)):
        if ctx.is_platform_admin:
            return ctx
        for m in ctx.memberships:
            if m.get("ended_at") is not None:
                continue
            if str(m.get("club_id")) == str(club_id):
                return ctx
        raise ForbiddenError("Acceso denegado a este club")
    return _dep
