from typing import Optional

from fastapi import APIRouter, Query

from app import stubs

router = APIRouter(tags=["alerts"])


@router.get("/alerts")
def list_alerts(status: Optional[str] = Query(None, pattern="^(active|resolved)$")):
    # TODO: заменить на данные из БД
    if status:
        return [a for a in stubs.ALERTS if a["status"] == status]
    return stubs.ALERTS
