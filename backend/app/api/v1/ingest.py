import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.core.security import verify_agent_token
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ingest import ReportIn
from app.services.ingest_service import process

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ingest"])


@router.post("/ingest")
def ingest(
    payload: list[dict],
    db: Session = Depends(get_db),
    _authorized: None = Depends(verify_agent_token),
):
    accepted = 0
    errors = []

    for index, raw_report in enumerate(payload):
        try:
            report = ReportIn.model_validate(raw_report)
        except ValidationError as exc:
            errors.append(
                {
                    "index": index,
                    "errors": [
                        {"loc": error["loc"], "msg": error["msg"]}
                        for error in exc.errors()
                    ],
                }
            )
            continue

        try:
            process(db, report)
        except Exception:
            logger.exception(
                "Не удалось сохранить отчёт №%s от источника %s",
                index,
                report.source_id,
            )
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
