from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ingest import ReportIn
from app.services.ingest_service import process

router = APIRouter(tags=["ingest"])


@router.post("/ingest")
def ingest(payload: list[dict], db: Session = Depends(get_db)):
    accepted = 0
    errors = []

    for index, raw in enumerate(payload):
        try:
            report = ReportIn.model_validate(raw)
        except ValidationError as exc:
            errors.append(
                {
                    "index": index,
                    "errors": [{"loc": e["loc"], "msg": e["msg"]} for e in exc.errors()],
                }
            )
            continue

        try:
            process(db, report)
        except Exception:
            errors.append(
                {
                    "index": index,
                    "errors": [
                        {
                            "loc": [],
                            "msg": "Не удалось сохранить отчёт в базе данных",
                        }
                    ],
                }
            )
            continue

        accepted += 1

    return {
        "accepted": accepted,
        "rejected": len(errors),
        "received_at": datetime.now(timezone.utc).isoformat(),
        "errors": errors,
    }
