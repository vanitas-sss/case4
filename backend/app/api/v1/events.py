from typing import Optional

from fastapi import APIRouter, Query

from app import stubs

router = APIRouter(tags=["events"])


@router.get("/events")
def list_events(limit: int = Query(50, ge=1, le=500), type: Optional[str] = None):
    # TODO: заменить на данные из БД, новые события сверху
    result = stubs.EVENTS
    if type:
        result = [e for e in result if e["type"] == type]
    return result[:limit]
