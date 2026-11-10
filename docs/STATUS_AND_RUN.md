# Состояние проекта и запуск

Дата: 2026-11-11. Эта версия описывает backend-изменения в ветке `feat/maria-database-backed-api`.

## Что реализовано в backend

- FastAPI API под префиксом `/api/v1`.
- `POST /api/v1/ingest`: принимает массив отчётов, проверяет Pydantic-схемой и сохраняет данные в SQLite.
- GET-маршруты серверов, метрик, контейнеров, топологии, доступности, событий, тревог и сводки теперь читают реальные таблицы SQLite, а не `app/stubs.py`.
- История метрик ограничена максимум 500 точками на ответ, чтобы не перегружать браузер.
- Состояние сервера рассчитывается по времени последнего отчёта. Пороги задаются настройками.
- Базовые тревоги: CPU >= 90% (warning) и статус offline от источника/heartbeat (critical). Повторные уведомления не создаются, пока тревога уже активна; при восстановлении тревога закрывается.
- Фоновая проверка heartbeat запускается при старте FastAPI; периодическая очистка старых записей запускается раз в час.
- Тесты расширены для GET API, жизненного цикла тревог и перехода хоста offline/online.
- Добавлен документ API-контракта и GitHub Actions workflow для запуска backend-тестов на Pull Request.

## Что пока не входит в эту доработку

- Telegram и webhook-уведомления не подключены. Тревоги доступны через `GET /api/v1/alerts` и события через `GET /api/v1/events`.
- HTTP/TCP checks произвольных учебных стендов и отдельная таблица результатов проверок пока не реализованы.
- Управление пользовательскими правилами алертинга через CRUD API пока не реализовано: текущие два правила базовые и фиксированные.
- Ручное редактирование топологии и экспорт PlantUML пока не реализованы.
- Интеграция с агентом требует проверки по фактическому JSON от Германа. Текущий контракт описан в `backend/app/schemas/ingest.py` и `backend/examples/ingest.example.json`.
- Frontend, Docker Compose и полная сборка всего проекта остаются задачами других участников.

## Настройки мониторинга

Файл: `backend/app/core/config.py`.

- `HEARTBEAT_INTERVAL=60` — рекомендуемый интервал отправки агентом.
- `WARNING_AFTER=120` — после этого времени без отчёта состояние становится warning.
- `OFFLINE_AFTER=150` — после этого времени состояние становится offline.
- `CHECK_PERIOD=30` — период фоновой проверки.
- `RETENTION_DAYS=7` — срок хранения метрик, событий и heartbeat-проверок.

Для локального генератора, который отправляет отчёт каждые 5 секунд, эти значения не мешают проверке. Для изменения параметров создай `.env` в каталоге `backend` и укажи нужные переменные. Не добавляй реальные токены в Git.

## Запуск backend на Windows PowerShell

Нужен Python 3.11 или новее.

```powershell
git checkout main
git pull origin main
git checkout feat/maria-database-backed-api
git pull origin feat/maria-database-backed-api

cd backend
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Если ветка уже локально создана, переключись на неё и обнови через `git pull`. При проверке PR лучше не сливать его в main до ревью.

Открыть:
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/v1/health

При старте FastAPI выполняются миграции и запускаются два фоновых цикла: heartbeat (каждые 30 секунд) и очистка (каждый час).

## Проверка POST и реального чтения

Оставь backend запущенным. Во втором PowerShell из корня репозитория:

```powershell
cd mock-data
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python generator.py --url http://127.0.0.1:8000/api/v1/ingest --interval 5
```

Затем открой Swagger:
1. Отправь JSON-массив из `backend/examples/ingest.example.json` в `POST /api/v1/ingest`.
2. Ожидаемый результат: `accepted: 1`, `rejected: 0`.
3. Открой `GET /api/v1/hosts`: должен появиться отправленный хост.
4. Открой `GET /api/v1/hosts/1/metrics?period=1h`: появятся реальные точки метрик.
5. Проверь `GET /api/v1/containers`, `/api/v1/topology?host_id=1`, `/api/v1/availability`, `/api/v1/events`, `/api/v1/alerts`, `/api/v1/summary`.

ID хоста может быть не 1, если в локальной базе уже есть записи. Сначала возьми ID из `GET /hosts`.

Чтобы проверить CPU alert, отправь отчёт с `host.cpu_percent = 95`. В `GET /alerts?status=active` появится `cpu_high`. Отправь следующий отчёт с CPU ниже 90 — тревога должна стать resolved.

Чтобы проверить offline:
1. Останови генератор Ctrl+C.
2. Подожди более 150 секунд плюс до 30 секунд на фоновую проверку.
3. Проверь `GET /hosts` и `GET /alerts?status=active`.
4. Снова запусти генератор. После нового отчёта сервер вернётся в online, а offline alert закроется.

## Тесты backend

В отдельном терминале:

```powershell
cd backend
.venv\Scripts\Activate.ps1
python -m pytest -q
```

GitHub Actions также запускает эту команду автоматически для Pull Request. Если CI упал, Pull Request нельзя считать проверенным, пока причина не исправлена.

## API-контракт для frontend

Полное описание полей и параметров находится в `docs/API_V1.md`. Ключевые адреса:
- `GET /api/v1/hosts`
- `GET /api/v1/hosts/{id}`
- `GET /api/v1/hosts/{id}/metrics?period=1h|6h|24h`
- `GET /api/v1/containers`
- `GET /api/v1/topology?host_id={id}`
- `GET /api/v1/availability?period=24h`
- `GET /api/v1/events?limit=50`
- `GET /api/v1/alerts?status=active`
- `GET /api/v1/summary`

Время в ответах — ISO 8601 UTC с `Z`. Проценты — числа 0–100. Frontend не должен подключаться к SQLite напрямую. Для Vite можно настроить dev proxy `/api -> http://127.0.0.1:8000`.

## Кто что делает дальше

Назначения ниже соответствуют плану реализации проекта:

- **Мария (backend):** поддерживать API-контракт; после интеграции проверить JSON агента; дальше отдельными задачами реализовать HTTP/TCP checks, Telegram/webhook, CRUD alert rules, ручное редактирование/экспорт топологии и защиту ingest токеном. Не переписывать готовые GET-маршруты без согласования с frontend.
- **Герман (agent):** файлы `agent/agent/main.py`, `agent/agent/config.py`, `agent/agent/sender.py`, `agent/agent/collectors/host.py`, `containers.py`, `events.py`, `connections.py`; `agent/requirements.txt`, `agent/config.example.yaml`, `agent/install_agent.sh`. Отправлять отчёт на `POST /api/v1/ingest` и сверить JSON с `backend/examples/ingest.example.json`.
- **Артём (frontend/API):** `frontend/src/api/client.js`, `frontend/src/api/hooks.js`, `frontend/src/pages/`, `frontend/src/layout/`, `frontend/src/App.jsx`, `frontend/src/main.jsx`, `frontend/package.json`, `frontend/vite.config.js`. Использовать только маршруты из `docs/API_V1.md`.
- **Али (компоненты):** `frontend/src/components/StatusBadge.jsx`, `HostCard.jsx`, `ContainerTable.jsx`, `MetricChart.jsx`, `EventList.jsx`, `AlertTable.jsx`, `UptimeBar.jsx`, `Loader.jsx`, `EmptyState.jsx`, `ErrorBox.jsx`; компонентам передавать данные через props, не делать отдельные запросы внутри каждой карточки.
- **Сергей (дизайн):** макеты страниц Dashboard, Hosts, Containers, Events, Alerts, Availability и Topology; передать frontend единые цвета, размеры, состояния и адаптивные правила. Его макеты должны соответствовать полям API-контракта.

## Правила совместной работы

- JSON входа агента задаётся Pydantic-моделью `ReportIn` и примером `backend/examples/ingest.example.json`.
- JSON ответов сайта описан в `docs/API_V1.md`. Изменение названий полей согласовывать с Артёмом до изменения кода.
- Backend/frontend общаются только по HTTP и JSON. Не передавать Python-модели SQLAlchemy во frontend.
- Время отправлять в ISO 8601 с часовым поясом; предпочтительно UTC.
- Не коммитить `.env`, `.venv`, `metrics.db`, `node_modules` и реальные токены.
