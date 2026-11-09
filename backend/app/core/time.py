"""Общие функции для работы с датами в UTC.

SQLite не сохраняет информацию о часовом поясе, поэтому перед записью
в базу приводим время к UTC и убираем tzinfo.
"""
from datetime import datetime, timezone


def utc_now_naive() -> datetime:
    """Возвращает текущее время UTC в формате, который хранит SQLite."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_utc_naive(value: datetime) -> datetime:
    """Приводит дату к UTC и убирает tzinfo. Naive-даты считаются временем UTC."""
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)
