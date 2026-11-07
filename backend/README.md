# netmon backend (FastAPI)

Серверная часть кейса 4: принимает отчёты от источника данных (агент кейса 1 или заглушка), обрабатывает, хранит и отдаёт сайту.

## Быстрый старт

```bash
cd backend
python -m venv .venv
# Windows:   .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
uvicorn app.main:app --reload
```

Документация и кнопка «попробовать» для каждого адреса: http://localhost:8000/docs

Проверка приёма: на `/docs` откройте `POST /api/v1/ingest`, вставьте содержимое `examples/ingest.example.json`.
Ожидаемый ответ: `accepted: 1`, `rejected: 0`.

Тесты: `pytest`

## Структура

```
backend/
├─ app/
│  ├─ main.py            создание приложения, подключение роутера /api/v1
│  ├─ core/config.py     настройки из .env
│  ├─ schemas/ingest.py  формат входящего JSON (контракт)
│  ├─ stubs.py           готовые примеры ответов (пока нет БД)
│  └─ api/v1/            адреса API: ingest, hosts, containers, topology,
│                        availability, events, alerts, summary, health
├─ examples/             пример отчёта для проверки
└─ tests/                автоматические проверки
```

Правило слоёв (когда появится БД): `api → services → repositories → models`. Адреса не пишут SQL сами.

## Статус адресов

| Адрес | Статус |
| --- | --- |
| `GET /api/v1/health` | готов |
| `POST /api/v1/ingest` | проверяет формат; в БД пока не пишет |
| `GET /hosts`, `/hosts/{id}`, `/hosts/{id}/metrics` | заглушка |
| `GET /containers`, `/topology`, `/availability`, `/events`, `/alerts`, `/summary` | заглушка |

Заглушки возвращают пример нужного формата из `app/stubs.py`. Сайт уже может с ними работать. Когда Марина отдаст `repositories/`, каждый адрес переписывается на данные из БД (в коде помечено `# TODO`).

## Что дальше

1. Марина: `db/`, `models/`, `repositories/` (сначала `hosts` и `host_metrics`).
2. Мария: `services/ingest_service.py`, замена заглушек на данные из БД.
3. Мария: `availability_service.py`, `alert_service.py`, `workers/checker.py`.
