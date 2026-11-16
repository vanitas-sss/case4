from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.dashboard_service import list_sources

router = APIRouter(tags=["sources"])


@router.get("/sources")
def sources(db: Session = Depends(get_db)):
    return list_sources(db)
