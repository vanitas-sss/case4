from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import dashboard_service

router = APIRouter(tags=["containers"])


@router.get("/containers")
def list_containers(
    host_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return dashboard_service.list_container_rows(db, host_id, status)
