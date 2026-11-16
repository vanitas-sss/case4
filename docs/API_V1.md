# API v1

Все маршруты начинаются с `/api/v1`. Полные схемы доступны по `/docs` после запуска backend.

| Метод | Путь | Назначение |
| --- | --- | --- |
| GET | `/health` | Состояние API |
| POST | `/ingest` | Массив JSON-отчётов |
| POST | `/import` | Загрузка JSON-файла того же формата |
| GET | `/summary` | Числа для обзора |
| GET | `/hosts`, `/hosts/{id}` | Серверы и детали |
| GET | `/hosts/{id}/metrics` | История узла |
| GET | `/metrics/infra` | Средние по инфраструктуре |
| GET | `/containers` | Контейнеры |
| GET | `/topology` | Граф узлов и связей |
| GET | `/availability` | Доступность за период |
| GET | `/events` | События |
| GET | `/alerts` | Активные и закрытые тревоги |
| GET | `/sources` | Источники данных |

Образцы: [contracts/api-examples.json](../contracts/api-examples.json). Поддерживаемые периоды для истории: `1h`, `6h`, `24h`, `7d`. Ошибки передаются HTTP-кодами 400, 404, 413, 422.
