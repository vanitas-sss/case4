# API v1: ответы для frontend

Base URL локально: `http://127.0.0.1:8000/api/v1`.

Все ответы — JSON. Время возвращается в UTC в ISO 8601 с суффиксом `Z`. Проценты CPU/RAM/Disk и нагрузки связи — числа 0–100 или `null`, если значения ещё не поступали.

## Источники данных

Все GET-маршруты ниже читают SQLite через SQLAlchemy. Демонстрационные данные из `app/stubs.py` больше не используются этими маршрутами. Если база пуста, API возвращает пустые массивы и нулевые счётчики.

## Маршруты

| Метод и путь | Параметры | Ответ |
|---|---|---|
| `GET /health` | — | `{ "status": "ok" }` |
| `GET /hosts` | `status` optional | Массив серверов |
| `GET /hosts/{host_id}` | ID сервера | Сервер и его контейнеры; 404 если нет |
| `GET /hosts/{host_id}/metrics` | `period=1h\|6h\|24h` | Массив метрик по времени, максимум 500 точек |
| `GET /containers` | `host_id`, `status` optional | Массив контейнеров |
| `GET /topology` | `host_id`, `type` optional | `nodes`, `links`, `generated_at` |
| `GET /availability` | `period=1h\|6h\|24h\|7d` | Массив серверов с доступностью |
| `GET /events` | `limit=1..500`, `type`, `host_id` optional | Последние события |
| `GET /alerts` | `status=active\|resolved` optional | Список тревог |
| `GET /summary` | — | Сводные счётчики |



Для `GET /topology?host_id=ID` поле `id` узла остаётся исходным внешним ID из отчёта агента. Для общей топологии без `host_id` ID формируется как `host_id:external_id`, чтобы одинаковые ID узлов разных серверов не конфликтовали. У узла дополнительно есть `external_id` и `host_id`; у связи — `host_id`.

## Объект сервера

```json
{
  "id": 1,
  "name": "server-01",
  "ip": "192.168.1.10",
  "status": "online",
  "last_seen": "2026-11-11T10:00:00Z",
  "seconds_since_seen": 2,
  "cpu_percent": 42.5,
  "memory_percent": 61.2,
  "disk_percent": 48.1,
  "containers_total": 2,
  "containers_running": 2,
  "active_alerts": 0
}
```

Состояние пересчитывается по возрасту последнего отчёта: меньше `WARNING_AFTER` — исходный статус; начиная с `WARNING_AFTER` — `warning`; начиная с `OFFLINE_AFTER` — `offline`. Пороговые значения находятся в `backend/app/core/config.py`.

## Объект метрики

```json
{
  "timestamp": "2026-11-11T10:00:00Z",
  "cpu_percent": 42.5,
  "memory_percent": 61.2,
  "disk_percent": 48.1,
  "net_rx_bytes": 1000,
  "net_tx_bytes": 2000
}
```

## Объект контейнера

Поля: `id` (внутренний ID БД), `host_id`, `host_name`, `docker_id` (идентификатор источника), `name`, `image`, `status`, `ip`, `networks`.

## Тревоги

Базовые правила создаются при обработке входящего отчёта:

- `cpu_high`: CPU >= 90%, severity `warning`.
- `host_offline`: источник передал статус `offline`, severity `critical`.

Тревога открывается один раз, пока условие активно. При следующем отчёте, в котором условие перестало выполняться, она закрывается и создаётся событие. Это базовый учебный алертинг; автоматическое создание тревоги только из-за пропущенного heartbeat пока не реализовано.

## Доступность

`uptime_percent` — доля успешных проверок (`is_online=true`) среди проверок за выбранный период, а не точный time-weighted uptime. Если проверок нет, возвращается `null`.

## Подключение frontend

Создайте общий модуль, например `frontend/src/api/client.js`, с base URL `http://127.0.0.1:8000/api/v1`. Компоненты React должны получать данные через этот модуль, а не обращаться к SQLite и не импортировать Python-файлы. Для изменения API сначала обновите этот документ и согласуйте JSON-поля с frontend-командой.
