from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import ValidationError

from app.schemas.ingest import ReportIn

router = APIRouter(tags=["ingest"])


@router.post("/ingest")
def ingest(payload: list[dict]):
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

        # TODO (после готовности БД Марины): ingest_service.process(db, report)
        _ = report
        accepted += 1

    return {
        "accepted": accepted,
        "rejected": len(errors),
        "received_at": datetime.now(timezone.utc).isoformat(),
        "errors": errors,
    }
