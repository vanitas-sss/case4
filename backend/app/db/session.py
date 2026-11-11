from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _database_url() -> str:
    path = settings.DB_PATH
    if path == ":memory:":
        return "sqlite://"
    database_path = Path(path)
    if not database_path.is_absolute():
        database_path = Path(__file__).resolve().parents[2] / database_path
    database_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{database_path.as_posix()}"


engine = create_engine(
    _database_url(),
    connect_args={"check_same_thread": False},
    future=True,
)


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(connection, _record):
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
