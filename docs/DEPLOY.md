# Развёртывание

Требуется Docker с Compose.

```bash
docker compose up --build -d --wait
```

Сайт: http://localhost:8080. Swagger: http://localhost:8000/docs.

Для демонстрации с генератором:

```bash
docker compose --profile demo up --build -d --wait
```

Проверка: `docker compose ps`, `docker compose logs backend`. Остановка без удаления данных: `docker compose --profile demo down`. Удаление базы **только при намеренном сбросе**: `docker compose --profile demo down -v`.

Параметры heartbeat и хранения меняются в корневом `.env` по примеру `.env.example`. SQLite размещён в volume `monitoring-data`; конфигурация Docker не открывает внешних портов, кроме локальных 8000 и 8080.
