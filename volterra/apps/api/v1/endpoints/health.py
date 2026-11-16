from fastapi import APIRouter

from apps.api.v1.schemas import HealthOut

router = APIRouter()


@router.get("/", response_model=HealthOut)
def health_check():
    return {"status": "ok"}
