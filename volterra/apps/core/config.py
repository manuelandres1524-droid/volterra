import json
from typing import Annotated, Any, Literal

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_PRODUCTION_ENVS = frozenset({"prod", "production", "staging"})


def _parse_string_list(value: Any, field_name: str) -> list[str]:
    """Acepta lista JSON, valores separados por comas o una lista de Python."""
    if value is None:
        return []

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{field_name} debe ser una lista JSON o valores separados por comas"
                ) from exc
            if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
                raise ValueError(f"{field_name} debe contener solo cadenas")
            value = parsed
        else:
            value = raw.split(",")

    if isinstance(value, (list, tuple, set)):
        items: list[str] = []
        for item in value:
            text = str(item).strip()
            if text and text not in items:
                items.append(text)
        return items

    raise ValueError(f"{field_name} debe ser una lista o una cadena")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "volterra-mvp"
    APP_ENV: str = "dev"
    API_V1_PREFIX: str = "/api/v1"

    # Acepta lista JSON o valores separados por comas, sin decodificación automática.
    CORS_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    # Hosts aceptados por TrustedHostMiddleware. "*" solo se permite fuera de
    # producción; el arranque falla cerrado si queda abierto en prod/staging.
    TRUSTED_HOSTS: Annotated[list[str], NoDecode] = ["*"]
    # None = derivar de APP_ENV: documentación solo fuera de producción.
    ENABLE_DOCS: bool | None = None
    SECURE_HEADERS: bool = True
    # HSTS: max-age en segundos. Solo se emite en producción (ver main.py).
    HSTS_MAX_AGE_SECONDS: int = 31536000  # 1 año

    SUPABASE_URL: str = ""
    SUPABASE_PUBLISHABLE_KEY: str = ""
    SUPABASE_AUTH_TIMEOUT_SECONDS: float = 10.0
    SUPABASE_POSTGREST_TIMEOUT_SECONDS: float = Field(default=15.0, gt=0)

    # Sesión del frontend Jinja2. Las cookies de token son HttpOnly; la de CSRF
    # debe ser legible por el navegador para el patrón double-submit.
    COOKIE_SECURE: bool = True
    SESSION_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    REFRESH_COOKIE_MAX_AGE_SECONDS: int = 60 * 60 * 24 * 30
    CSRF_COOKIE_MAX_AGE_SECONDS: int = 60 * 60 * 8

    # Límite de peticiones: ventana fija en memoria por proceso (DEC-22).
    # Perfil estricto: login 5/5 min, refresh 15/5 min, escrituras 15/min,
    # lecturas 120/min. Los umbrales son configurables, no constantes ocultas.
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_TRUST_FORWARDED_FOR: bool = False
    RATE_LIMIT_LOGIN_ATTEMPTS: int = Field(default=5, gt=0)
    RATE_LIMIT_LOGIN_WINDOW_SECONDS: int = Field(default=300, gt=0)
    RATE_LIMIT_REFRESH_ATTEMPTS: int = Field(default=15, gt=0)
    RATE_LIMIT_REFRESH_WINDOW_SECONDS: int = Field(default=300, gt=0)
    RATE_LIMIT_LOGOUT_ATTEMPTS: int = Field(default=15, gt=0)
    RATE_LIMIT_LOGOUT_WINDOW_SECONDS: int = Field(default=300, gt=0)
    RATE_LIMIT_ANON_WRITE_REQUESTS: int = Field(default=15, gt=0)
    RATE_LIMIT_WRITE_REQUESTS: int = Field(default=15, gt=0)
    RATE_LIMIT_WRITE_WINDOW_SECONDS: int = Field(default=60, gt=0)
    RATE_LIMIT_READ_REQUESTS: int = Field(default=120, gt=0)
    RATE_LIMIT_READ_WINDOW_SECONDS: int = Field(default=60, gt=0)

    # Logging estructurado en una línea JSON por evento, sin datos personales.
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"

    # JWT strict validation
    SUPABASE_JWT_SECRET: str | None = None
    SUPABASE_JWT_ISSUER: str | None = None
    SUPABASE_JWT_AUDIENCE: str | list[str] = "authenticated"
    SUPABASE_JWT_ALGORITHMS: list[str] = ["ES256", "RS256", "HS256"]
    JWKS_CACHE_TTL_SECONDS: int = 300

    @field_validator("CORS_ORIGINS", "TRUSTED_HOSTS", mode="before")
    @classmethod
    def _parse_list_fields(cls, value: Any, info: ValidationInfo) -> list[str]:
        return _parse_string_list(value, info.field_name)

    @field_validator("CORS_ORIGINS")
    @classmethod
    def _reject_wildcard(cls, value: list[str]) -> list[str]:
        if "*" in value:
            raise ValueError("CORS_ORIGINS no admite '*' cuando se envían credenciales")
        return value


settings = Settings()


def is_production(config: Settings | None = None) -> bool:
    config = config or settings
    return config.APP_ENV.strip().lower() in _PRODUCTION_ENVS


def _is_https(value: str) -> bool:
    """Comprueba el esquema sin interpretar credenciales ni rutas."""
    return value.strip().lower().startswith("https://")


def essential_config_problems(config: Settings | None = None) -> list[str]:
    """Campos sin los que el BFF no puede atender ninguna petición autenticada.

    Devuelve nombres de campo, nunca valores: es seguro registrarlo o exponerlo
    en un readiness genérico.
    """
    config = config or settings
    problems: list[str] = []
    if not config.SUPABASE_URL.strip():
        problems.append("SUPABASE_URL")
    if not config.SUPABASE_PUBLISHABLE_KEY.strip():
        problems.append("SUPABASE_PUBLISHABLE_KEY")
    return problems


def runtime_config_problems(config: Settings | None = None) -> list[str]:
    """Comprueba la configuración crítica y las condiciones de producción."""
    config = config or settings
    problems = essential_config_problems(config)
    if not is_production(config):
        return problems

    if not config.COOKIE_SECURE:
        problems.append("COOKIE_SECURE")
    if "*" in config.TRUSTED_HOSTS:
        problems.append("TRUSTED_HOSTS")
    if config.SUPABASE_URL and not _is_https(config.SUPABASE_URL):
        problems.append("SUPABASE_URL_HTTPS")
    if config.SUPABASE_JWT_ISSUER and not _is_https(config.SUPABASE_JWT_ISSUER):
        problems.append("SUPABASE_JWT_ISSUER_HTTPS")
    algorithms = set(config.SUPABASE_JWT_ALGORITHMS)
    asymmetric = algorithms & {"RS256", "ES256"}
    if "HS256" in algorithms and not config.SUPABASE_JWT_SECRET and not asymmetric:
        problems.append("SUPABASE_JWT_SECRET")
    return problems


def validate_runtime_config(config: Settings | None = None) -> list[str]:
    """Falla cerrado al arrancar en producción si la configuración no es válida.

    En desarrollo devuelve la lista de problemas para registrarla como aviso,
    sin impedir el arranque local con datos ficticios.
    """
    config = config or settings
    problems = runtime_config_problems(config)
    if problems and is_production(config):
        raise RuntimeError(
            "Configuración incompleta para producción: " + ", ".join(problems)
        )
    return problems


def docs_enabled(config: Settings | None = None) -> bool:
    """OpenAPI y Swagger solo se publican fuera de producción, salvo override."""
    config = config or settings
    if config.ENABLE_DOCS is not None:
        return config.ENABLE_DOCS
    return not is_production(config)
