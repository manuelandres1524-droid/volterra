import time
from typing import Any

import httpx

from apps.core.config import settings


class JWKSCache:
    def __init__(self) -> None:
        self._keys: dict[str, Any] = {}
        self._fetched_at: float = 0.0

    def _jwks_url(self) -> str:
        base = settings.SUPABASE_URL.rstrip("/")
        return f"{base}/auth/v1/.well-known/jwks.json"

    async def get_key(self, kid: str) -> dict[str, Any] | None:
        now = time.time()
        if not self._keys or now - self._fetched_at > settings.JWKS_CACHE_TTL_SECONDS:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(self._jwks_url())
                resp.raise_for_status()
                data = resp.json()
            self._keys = {k["kid"]: k for k in data.get("keys", []) if k.get("kid")}
            self._fetched_at = now
        return self._keys.get(kid)

    def clear(self) -> None:
        """Vacía la caché; se usa al apagar la aplicación."""
        self._keys.clear()
        self._fetched_at = 0.0


jwks_cache = JWKSCache()
