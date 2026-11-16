from supabase import Client, ClientOptions, create_client

from apps.core.config import settings


def _client_options() -> ClientOptions:
    """Opciones del cliente por petición.

    El timeout acota la espera a PostgREST. Los reintentos de supabase-py solo
    aplican a GET/HEAD, así que no pueden duplicar escrituras.
    """
    return ClientOptions(
        postgrest_client_timeout=settings.SUPABASE_POSTGREST_TIMEOUT_SECONDS,
    )


def get_supabase_for_user(access_token: str) -> Client:
    if not access_token:
        raise RuntimeError("access_token requerido para cliente por-request")
    if not settings.SUPABASE_URL or not settings.SUPABASE_PUBLISHABLE_KEY:
        raise RuntimeError("Faltan SUPABASE_URL o SUPABASE_PUBLISHABLE_KEY")
    client: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_PUBLISHABLE_KEY,
        options=_client_options(),
    )
    try:
        client.postgrest.auth(access_token)
    except Exception as e:
        raise RuntimeError("No se pudo propagar el token al cliente PostgREST") from e
    return client
