from datetime import datetime, timedelta, timezone

from app.core.time import to_utc_naive, utc_now_naive


def test_to_utc_naive_converts_aware_datetime():
    value = datetime(
        2026,
        11,
        9,
        15,
        30,
        tzinfo=timezone(timedelta(hours=3)),
    )

    assert to_utc_naive(value) == datetime(2026, 11, 9, 12, 30)


def test_to_utc_naive_keeps_naive_datetime():
    value = datetime(2026, 11, 9, 12, 30)

    assert to_utc_naive(value) == value


def test_utc_now_naive_returns_datetime_without_timezone():
    value = utc_now_naive()

    assert value.tzinfo is None
