"""Rutas HTML del frontend de F1, divididas por área.

La UI oculta acciones según el rol, pero no autoriza: cada lectura vuelve a
pasar por el BFF, el JWT del usuario y RLS + RPC.

El orden de inclusión importa: ``/clubs/new`` debe registrarse antes que
``/clubs/{club_id}``, y por eso ``clubs`` se incluye con sus rutas ya ordenadas.
"""

from __future__ import annotations

from fastapi import APIRouter

from apps.web.routes import athletes, auth, clubs, me, members, platform
from apps.web.routes.common import safe_next as _safe_next

router = APIRouter(include_in_schema=False)
router.include_router(auth.router)
router.include_router(me.router)
router.include_router(clubs.router)
router.include_router(athletes.router)
router.include_router(members.router)
router.include_router(platform.router)

__all__ = ["router", "_safe_next"]
