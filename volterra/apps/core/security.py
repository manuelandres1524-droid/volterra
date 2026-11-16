from typing import Any

import jwt
from jwt import PyJWTError
from jwt.algorithms import RSAAlgorithm, ECAlgorithm

from apps.core.config import settings
from apps.core.jwks import jwks_cache


class JWTValidationError(Exception):
    """El token no es válido para autenticar a un usuario."""


class JWTUnavailableError(JWTValidationError):
    """El servidor no puede verificar tokens (configuración o JWKS no disponible)."""


_ALLOWED_ROLES = frozenset({"authenticated"})


def _expected_issuer() -> str:
    if settings.SUPABASE_JWT_ISSUER:
        return settings.SUPABASE_JWT_ISSUER.rstrip("/")
    if settings.SUPABASE_URL:
        base = settings.SUPABASE_URL.rstrip("/")
        return f"{base}/auth/v1"
    raise JWTUnavailableError("Emisor JWT no configurado")


async def _load_key(alg: str, kid: str | None) -> Any:
    if alg not in ("RS256", "ES256"):
        raise JWTValidationError(f"Algoritmo no soportado: {alg}")

    if not kid:
        raise JWTValidationError("Falta kid para algoritmo asimétrico")

    try:
        jwk = await jwks_cache.get_key(kid)
    except Exception as exc:
        raise JWTUnavailableError("No se pudo obtener la clave JWKS") from exc

    if not jwk:
        raise JWTValidationError("Clave JWKS no encontrada para kid")

    try:
        if alg == "RS256":
            return RSAAlgorithm.from_jwk(jwk)
        return ECAlgorithm.from_jwk(jwk)
    except Exception as exc:
        raise JWTUnavailableError("Clave JWKS inválida") from exc


async def verify_supabase_jwt_strict(token: str) -> dict[str, Any]:
    if not token or not token.strip():
        raise JWTValidationError("Token vacío")

    # El token malformado es siempre un error del cliente (401), incluso si la
    # configuración del servidor está incompleta. La configuración ausente solo
    # se trata como 503 cuando el token es estructuralmente válido.
    try:
        header = jwt.get_unverified_header(token)
    except PyJWTError as exc:
        raise JWTValidationError(f"Header inválido: {exc}") from exc

    alg = header.get("alg")
    kid = header.get("kid")

    if alg not in settings.SUPABASE_JWT_ALGORITHMS:
        raise JWTValidationError(f"Algoritmo no permitido: {alg}")

    issuer = _expected_issuer()
    audience = settings.SUPABASE_JWT_AUDIENCE
    if not audience:
        raise JWTUnavailableError("Audiencia JWT no configurada")

    if alg in ("RS256", "ES256"):
        key = await _load_key(alg, kid)
    elif alg == "HS256":
        if not settings.SUPABASE_JWT_SECRET:
            raise JWTUnavailableError("HS256 no permitido sin SUPABASE_JWT_SECRET")
        key = settings.SUPABASE_JWT_SECRET
    else:
        raise JWTValidationError(f"Algoritmo no soportado: {alg}")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[alg],
            issuer=issuer,
            audience=audience,
            options={
                "verify_exp": True,
                "verify_iat": True,
                "require": ["exp", "iat", "sub", "iss", "aud"],
            },
            leeway=10,
        )
    except PyJWTError as exc:
        raise JWTValidationError(f"Validación JWT fallida: {exc}") from exc

    if not payload.get("sub"):
        raise JWTValidationError("JWT sin sub")

    role = payload.get("role")
    if role == "service_role":
        raise JWTValidationError("service_role no permitido como token de usuario")
    if role not in _ALLOWED_ROLES:
        raise JWTValidationError("Rol no permitido")

    return payload
