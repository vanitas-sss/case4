import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.workers.monitor import cleanup_worker, monitor_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    monitor_task = asyncio.create_task(monitor_worker())
    cleanup_task = asyncio.create_task(cleanup_worker())
    try:
        yield
    finally:
        for task in (monitor_task, cleanup_task):
            task.cancel()
        await asyncio.gather(monitor_task, cleanup_task, return_exceptions=True)


app = FastAPI(
    title="netmon",
    description="Сервис мониторинга и визуализации состояния ИТ-инфраструктуры (кейс 4)",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(api_router, prefix="/api/v1")
