from fastapi import APIRouter

from app import stubs

router = APIRouter(tags=["summary"])


@router.get("/summary")
def get_summary():
    # TODO: заменить на summary_service (задача Али)
    return stubs.SUMMARY
