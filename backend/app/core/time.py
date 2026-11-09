"""Небольшие helpers для работы с датами в UTC.

SQLite не сохраняет информацию о часовом поясе, поэтому в БД храним
время как naive datetime, но всегда предварительно приводим его к UTC.
"""
from datetime import datetime, timezone


def utc_now_naive() -> datetime:
    """Текущее время UTC без tzinfo — формат, используемый SQLite."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_utc_naive(value: datetime | None) -> datetime | None:
    """Приводит datetime к UTC и убирает tzinfo для сохранения в SQLite."""
    if value is None or value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)
