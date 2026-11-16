# MOTY · мониторинг ИТ-инфраструктуры

Прототип кейса №4: приём JSON-отчётов, история CPU/RAM/диска, состояния серверов и контейнеров, топология, события и оповещения в веб-интерфейсе.

## Запуск

Нужны Docker и Docker Compose.

```bash
docker compose up --build -d --wait
```

- Сайт: http://localhost:8080

Демонстрационные данные запускаются отдельно:

```bash
docker compose --profile demo up --build -d --wait
```

Остановка: `docker compose --profile demo down`. Данные SQLite сохраняются в Docker volume.

## Структура

- `backend/` — FastAPI, SQLAlchemy, SQLite, heartbeat, оповещения.
- `frontend/` — React, страницы мониторинга.
- `mock-data/` — генератор тестовых отчётов и сценарий отказов. **Не агент.**
- `contracts/` — формат входного JSON и примеры API.
- `docs/` — краткие инструкции.

## Проверки

```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest
```

```bash
cd frontend
npm ci
npm run lint
npm run format:check
npm test
npm run build
```

Дополнительно: [развёртывание](docs/DEPLOY.md), [подключение источников](docs/CONNECT_SOURCES.md), [демонстрация](docs/DEMO.md), [API](docs/API_V1.md).

Настоящий агент относится к кейсу №1 и здесь не разрабатывается. Его JSON-отчёт пока не получен: адаптер под неизвестный формат не заявляется готовым. Оповещения работают **только на сайте**, без Telegram.
