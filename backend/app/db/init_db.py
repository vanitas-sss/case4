from pathlib import Path

from alembic import command
from alembic.config import Config


def init_db() -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    alembic_config = Config(str(backend_dir / "alembic.ini"))
    command.upgrade(alembic_config, "head")
