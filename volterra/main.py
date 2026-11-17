from contextlib import asynccontextmanager
from time import perf_counter, time
from urllib.parse import quote
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from apps.api.v1.router import api_router
from apps.core.config import (
    docs_enabled,
    essential_config_problems,
    settings,
    validate_runtime_config,
)
from apps.core.errors import (
    DomainError,
    RateLimitedError,
    TITLE_BY_CODE,
    code_for_status,
    headers as error_headers,
    http_status,
    title as error_title,
)
from apps.core.jwks import jwks_cache
from apps.core.logging import configure_logging, get_logger, sanitize_request_id
from apps.core.ratelimit import anonymous_scope, client_ip, evaluate
from apps.web.routes import router as web_router
from apps.web.templates import BASE_DIR, render

configure_logging()
log = get_logger("http")


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Valida la configuración al arrancar y libera estado al apagar.

    En producción, una configuración incompleta impide arrancar (fallo cerrado).
    En desarrollo solo se registra como aviso para no bloquear la demo local.
    """
    problems = validate_runtime_config()
    application.state.ready = True
    application.state.started_at = time()
    if problems:
        log.warning(
            "config_incompleta",
            extra={"event": "config_incompleta", "problems": problems},
        )
    log.info(
        "startup",
        extra={"event": "startup", "env": settings.APP_ENV, "docs": docs_enabled()},
    )
    try:
        yield
    finally:
        application.state.ready = False
        jwks_cache.clear()
        log.info("shutdown", extra={"event": "shutdown"})


async def rate_limit_middleware(request: Request, call_next):
    """Frena fuerza bruta y ráfagas antes de llegar a Supabase.

    Solo aplica ámbitos anónimos (login, refresh, logout y escrituras sin
    sesión). Los límites por usuario se aplican al resolver la autenticación.
    Devuelve la respuesta en lugar de lanzar: un ``HTTPException`` en un
    middleware quedaría fuera del manejador de excepciones de FastAPI.
    """
    scope = anonymous_scope(request)
    result = evaluate(scope, client_ip(request))
    if result is not None and not result.allowed:
        return await _rate_limited_response(request, result.retry_after)
    return await call_next(request)


async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    if settings.SECURE_HEADERS:
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; form-action 'self'; frame-ancestors 'none'; "
            "base-uri 'self'",
        )
        if not request.url.path.startswith("/static"):
            response.headers.setdefault("Cache-Control", "no-store")
        # HSTS solo cuando SECURE_HEADERS está activo y el entorno es de
        # producción (HTTPS extremo a extremo confirmado). En desarrollo no
        # se emite para no romper el trabajo local sin TLS.
        if settings.APP_ENV.strip().lower() in ("prod", "production", "staging"):
            response.headers.setdefault(
                "Strict-Transport-Security",
                f"max-age={settings.HSTS_MAX_AGE_SECONDS}; includeSubDomains",
            )
    return response


async def request_logging_middleware(request: Request, call_next):
    """Añade un identificador de petición y registra una línea JSON por petición.

    No se registran consultas, cabeceras, cookies ni cuerpos: solo método, ruta,
    estado y duración. El identificador sirve para correlacionar con los errores.
    """
    request_id = sanitize_request_id(request.headers.get("x-request-id")) or uuid4().hex
    request.state.request_id = request_id
    started = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        log.exception(
            "request_error",
            extra={
                "event": "request_error",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": 500,
                "duration_ms": round((perf_counter() - started) * 1000, 2),
            },
        )
        raise

    duration_ms = round((perf_counter() - started) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    log.info(
        "request",
        extra={
            "event": "request",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


def _is_api_request(request: Request) -> bool:
    path = request.url.path
    return path.startswith(settings.API_V1_PREFIX) or path.startswith("/auth/")


def _login_redirect(request: Request) -> RedirectResponse:
    target = request.url.path
    if request.url.query:
        target = f"{target}?{request.url.query}"
    return RedirectResponse(
        f"/login?next_url={quote(target, safe='/')}",
        status_code=303,
    )


def _rate_limited_error(retry_after: int) -> RateLimitedError:
    return RateLimitedError(
        retry_after,
        f"Demasiadas peticiones. Inténtalo de nuevo en {retry_after} segundos.",
    )


async def _rate_limited_response(request: Request, retry_after: int):
    """Mismo traductor que el resto de errores; evita un segundo contrato."""
    return await domain_error_handler(request, _rate_limited_error(retry_after))


async def domain_error_handler(request: Request, exc: DomainError):
    """Única traducción de errores de dominio a JSON o a página HTML.

    La API y las rutas ``/auth/`` reciben JSON con ``detail`` y ``code``. Las
    páginas HTML redirigen al login si falta autenticación y, en el resto de
    casos, muestran ``error.html`` con el título del catálogo.
    """
    status_code = http_status(exc)
    response_headers = error_headers(exc)

    if _is_api_request(request):
        return JSONResponse(
            {"detail": exc.message, "code": exc.code},
            status_code=status_code,
            headers=response_headers,
        )

    if status_code == 401:
        return _login_redirect(request)

    return render(
        request,
        "error.html",
        {"title": error_title(exc), "message": exc.message},
        status_code=status_code,
        headers=response_headers,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Fallos del framework (404 de ruta, 405, host no permitido)."""
    code = code_for_status(exc.status_code)
    if _is_api_request(request):
        return JSONResponse(
            {"detail": exc.detail, "code": code},
            status_code=exc.status_code,
            headers=exc.headers,
        )

    if exc.status_code == 401:
        return _login_redirect(request)

    title = TITLE_BY_CODE.get(code, TITLE_BY_CODE["error"])
    message = exc.detail if isinstance(exc.detail, str) else title
    return render(
        request,
        "error.html",
        {"title": title, "message": message},
        status_code=exc.status_code,
        headers=exc.headers,
    )


def _safe_validation_details(exc: RequestValidationError) -> list[dict]:
    """Errores de validación sin el valor enviado (``input``).

    El detalle sirve para corregir el formulario, no para devolver el cuerpo
    recibido. Se conservan tipo, ubicación y mensaje.
    """
    allowed = ("type", "loc", "msg")
    return [
        {key: value for key, value in error.items() if key in allowed}
        for error in exc.errors()
    ]


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if _is_api_request(request):
        return JSONResponse(
            {"detail": _safe_validation_details(exc), "code": code_for_status(422)},
            status_code=422,
        )
    return render(
        request,
        "error.html",
        {
            "title": "Solicitud inválida",
            "message": "Revisa los datos del formulario e inténtalo de nuevo.",
        },
        status_code=422,
    )


def _register_health_routes(application: FastAPI) -> None:
    @application.get("/health")
    def health():
        return {"status": "ok"}

    @application.get("/health/live", include_in_schema=False)
    def health_live():
        """Liveness: el proceso responde. No comprueba dependencias externas."""
        return {"status": "ok"}

    @application.get("/health/ready", include_in_schema=False)
    def health_ready(request: Request):
        """Readiness: configuración esencial presente y aplicación en marcha.

        No consulta Supabase a propósito: un readiness que depende de un
        servicio externo puede amplificar caídas o generar tráfico innecesario.
        """
        ready = getattr(request.app.state, "ready", True)
        if not ready or essential_config_problems():
            return JSONResponse({"status": "unavailable"}, status_code=503)
        return {"status": "ready"}


def _register_exception_handlers(application: FastAPI) -> None:
    application.add_exception_handler(DomainError, domain_error_handler)
    application.add_exception_handler(StarletteHTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)


def create_app() -> FastAPI:
    """Construye la aplicación; permite instanciarla en pruebas y en el servidor."""
    show_docs = docs_enabled()
    application = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/docs" if show_docs else None,
        redoc_url="/redoc" if show_docs else None,
        openapi_url="/openapi.json" if show_docs else None,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix=settings.API_V1_PREFIX)
    application.include_router(web_router)
    application.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    # El último middleware registrado es el más externo. Orden efectivo:
    # TrustedHost -> GZip -> logging -> cabeceras -> límite -> aplicación.
    # GZip comprime respuestas de más de 1024 bytes (gzip únicamente).
    application.add_middleware(GZipMiddleware, minimum_size=1024)
    application.middleware("http")(rate_limit_middleware)
    application.middleware("http")(add_security_headers)
    application.middleware("http")(request_logging_middleware)
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.TRUSTED_HOSTS,
    )

    _register_exception_handlers(application)
    _register_health_routes(application)
    return application


app = create_app()
