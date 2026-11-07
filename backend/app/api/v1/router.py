from fastapi import APIRouter

from app.api.v1 import (
    alerts,
    availability,
    containers,
    events,
    hosts,
    ingest,
    summary,
    topology,
)

api_router = APIRouter()

api_router.include_router(ingest.router)
api_router.include_router(hosts.router)
api_router.include_router(containers.router)
api_router.include_router(topology.router)
api_router.include_router(availability.router)
api_router.include_router(events.router)
api_router.include_router(alerts.router)
api_router.include_router(summary.router)


@api_router.get("/health", tags=["service"])
def health():
    """Проверка, что сервис жив."""
    return {"status": "ok"}
