from typing import Optional

from fastapi import APIRouter

from app import stubs

router = APIRouter(tags=["containers"])


@router.get("/containers")
def list_containers(host_id: Optional[int] = None, status: Optional[str] = None):
    # TODO: заменить на данные из БД
    result = stubs.CONTAINERS
    if host_id is not None:
        result = [c for c in result if c["host_id"] == host_id]
    if status:
        result = [c for c in result if c["status"] == status]
    return result
