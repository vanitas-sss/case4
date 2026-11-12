import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ingest import ReportIn
from app.services.ingest_service import process

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ingest"])


@router.post("/ingest")
def ingest(payload: list[dict], db: Session = Depends(get_db)):
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


@router.post("/import")
def import_reports(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Load our JSON contract; arbitrary case-1 formats require an agreed adapter."""
    content = file.file.read(2 * 1024 * 1024 + 1)
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(413, "Файл превышает 2 МиБ")
    try:
        payload = json.loads(content.decode("utf-8-sig"))
    except (ValueError, UnicodeError):
        raise HTTPException(400, "Нужен корректный JSON в UTF-8")
    if not isinstance(payload, list) or any(not isinstance(r, dict) for r in payload):
        raise HTTPException(422, "Ожидается массив JSON-отчётов по контракту /ingest")
    return ingest(payload, db)
