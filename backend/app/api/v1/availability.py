from fastapi import APIRouter, Query

from app import stubs

router = APIRouter(tags=["availability"])


@router.get("/availability")
def get_availability(period: str = Query("24h", pattern="^(1h|6h|24h|7d)$")):
    # TODO: заменить на availability_service (uptime за период)
    return stubs.AVAILABILITY
