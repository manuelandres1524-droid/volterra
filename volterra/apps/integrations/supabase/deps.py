"""Composición del cliente de datos por petición.

Un único punto crea el cliente Supabase con el JWT del usuario. La autenticación
ya lo creó para comprobar el contexto, así que aquí se reutiliza el de
``request.state`` y se evita una segunda instancia por petición.

No se usa ``service_role`` ni un cliente global: el invariante 6 de ADR-013
sigue vigente.
"""

from __future__ import annotations

from fastapi import Depends, Request
from supabase import Client

from apps.auth.deps import AuthContext, get_auth_context
from apps.core.errors import UnavailableError
from apps.integrations.supabase.per_request import get_supabase_for_user


def get_data_client(
    request: Request,
    ctx: AuthContext = Depends(get_auth_context),
) -> Client:
    """Cliente PostgREST con la identidad del usuario de esta petición."""
    client = getattr(request.state, "data_client", None)
    if client is not None:
        return client

    try:
        client = get_supabase_for_user(ctx.token)
    except Exception as exc:
        raise UnavailableError("No se pudo inicializar el cliente de datos") from exc

    request.state.data_client = client
    return client
