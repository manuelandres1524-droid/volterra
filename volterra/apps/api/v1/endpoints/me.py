from fastapi import APIRouter, Depends
from supabase import Client

from apps.api.v1.schemas import MeOut
from apps.auth.deps import AuthContext, get_auth_context
from apps.integrations.supabase.deps import get_data_client
from apps.services.f1_reads import get_profile

router = APIRouter()


@router.get("/", response_model=MeOut)
def me(
    ctx: AuthContext = Depends(get_auth_context),
    client: Client = Depends(get_data_client),
):
    profile = get_profile(client, ctx.user_id)

    return {
        "user_id": ctx.user_id,
        "email": ctx.email,
        "display_name": profile.get("display_name") if profile else None,
        "is_platform_admin": ctx.is_platform_admin,
        "memberships": ctx.memberships,
    }
