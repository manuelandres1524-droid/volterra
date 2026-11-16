from fastapi import APIRouter, Depends

from apps.api.v1.schemas import PlatformOverviewOut
from apps.auth.deps import AuthContext, require_platform_admin

router = APIRouter()


@router.get("/overview", response_model=PlatformOverviewOut)
def platform_overview(ctx: AuthContext = Depends(require_platform_admin)):
    return {"ok": True, "actor": ctx.user_id}
