# Backend

Python 3.11+, FastAPI, SQLAlchemy, SQLite, Alembic.

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API: http://localhost:8000/docs. При запуске миграции применяются автоматически.

```bash
python -m pytest
python -m alembic current
```

`DB_PATH` по умолчанию — `backend/data/metrics.db`. Время хранится в UTC. Статус сервера вычисляется по времени получения последнего нового отчёта, а не по полю `host.status`.

Контракт: [примеры](../contracts/api-examples.json), [API](../docs/API_V1.md).
