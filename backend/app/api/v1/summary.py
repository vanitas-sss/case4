from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import dashboard_service

router = APIRouter(tags=["summary"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return dashboard_service.get_summary(db)
