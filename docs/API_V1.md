# API v1

Base URL: `http://localhost:8000/api/v1`, через Docker nginx — `http://localhost:8080/api/v1`.
Все GET-маршруты читают реальную SQLite. Пустая база возвращает пустые массивы и нулевые счётчики. Время — ISO 8601 UTC (`Z` или `+00:00`), отсутствующие измерения — `null`.

## Маршруты

| Метод и путь | Параметры | Ответ |
|---|---|---|
| GET /health | — | `{"status":"ok"}` |
| POST /ingest | Массив отчётов JSON | accepted, rejected, received_at, errors |
| POST /import | multipart поле file, UTF-8 JSON до 2 МиБ | Результат ingest |
| GET /hosts | status: online, warning, offline, unknown | Массив серверов |
| GET /hosts/{id} | Числовой id | Сервер с массивом containers; 404, если отсутствует |
| GET /hosts/{id}/metrics | period: 1h, 6h, 24h, 7d | До 500 точек измерений |
| GET /metrics/infra | period: 1h, 6h, 24h, 7d | До 500 усреднённых точек инфраструктуры |
| GET /containers | host_id, status | Массив контейнеров |
| GET /topology | host_id, type | nodes, links, generated_at |
| GET /availability | period: 1h, 6h, 24h, 7d | Доля успешных проверок хостов |
| GET /events | limit: 1–500, type, host_id, period: 1h/6h/24h/7d | Последние события после фильтрации |
| GET /alerts | status: active, resolved | Тревоги |
| GET /summary | — | Сводные счётчики |
| GET /sources | — | Источники по source_id известных хостов |

Параметры фильтрации необязательны. Период метрик по умолчанию 1h, доступности — 24h; события без period не ограничены периодом, но ограничены limit (по умолчанию 50).

## Поля ответов

Сервер: `id`, `name`, `source_id`, `ip`, `status`, `last_seen`, `metric_timestamp`, `seconds_since_seen`, `cpu_percent`, `memory_percent`, `disk_percent`, `containers_total`, `containers_running`, `active_alerts`.

`last_seen` — время получения нового отчёта, `metric_timestamp` — время измерения в отчёте. Последние значения могут быть историческими; их время обязательно учитывать. Подробный маршрут также возвращает `containers`.

Контейнер: `id`, `host_id`, `host_name`, `docker_id`, `name`, `image`, `status`, `ip`, `networks`, `last_seen`. При устаревшем отчёте или недоступном хосте вычисляемый статус — unknown. CPU/RAM контейнера и число перезапусков не входят в контракт.

Метрика хоста: `timestamp`, `cpu_percent`, `memory_percent`, `disk_percent`, `net_rx_bytes`, `net_tx_bytes`. Сетевые поля — накопительные счётчики байтов. При большом количестве измерений выбираются равномерные по индексам точки, поэтому краткие пики могут быть пропущены.

Метрика инфраструктуры: `timestamp`, `cpu_percent`, `memory_percent`, `disk_percent`, `hosts_count`. timestamp обозначает начало интервала. Сначала вычисляется среднее внутри каждого хоста за интервал, затем среднее между хостами. null не превращается в ноль; пропущенные интервалы не заполняются выдуманными измерениями. Источники с частой отправкой не получают дополнительный вес. hosts_count — число хостов с отчётами в интервале, включая отчёты без отдельных метрик.

Событие: `id`, `timestamp`, `type`, `host`, `host_id`, `container`, `message`. Полей new/in_progress/closed нет: события — журнал, а состояния active/resolved относятся к тревогам.

Тревога: `id`, `rule`, `target`, `host`, `severity`, `status`, `message`, `started_at`, `resolved_at`. CPU >= 90% открывает cpu_high, подтверждённая остановка контейнера на доступном хосте — container_stopped. Фоновый мониторинг открывает host_offline после таймаута. При восстановлении тревога закрывается. Длительность высокой CPU-нагрузки отдельно не учитывается.

Доступность: `host_id`, `host`, `status`, `last_seen`, `uptime_percent`, `checks_total`. Если проверок нет, процент null. Это доля успешных наблюдений, не аптайм ОС и не точный SLA.

Источник: `source_id`, `hosts_total`, `hosts_online`, `last_seen`. Это группировка известных хостов, а не список настроенных внешних интеграций.

Сводка: `hosts_total`, `hosts_online`, `hosts_warning`, `hosts_offline`, `containers_total`, `containers_running`, `containers_stopped`, `active_alerts`.

Топология: узлы содержат id, external_id, host_id, label, type, status, ip; связи — source, target, type, load, host_id. В общей топологии id равен `host_id:external_id`. При фильтре host_id возвращается исходный external_id. Не смешивайте идентификаторы из этих двух ответов. Если label отсутствует, используется external_id.

## Импорт и ошибки

HTTP 200 на ingest/import не гарантирует принятие всех элементов: проверяйте rejected и errors. В errors указан индекс элемента массива с нуля и список loc/msg. Неверный внешний формат — 422, неразбираемый файл — 400, файл больше лимита — 413. Повтор и старый отчёт могут считаться принятыми без создания новой метрики и без продления heartbeat.

Точный входной контракт: `backend/app/schemas/ingest.py`; пример: `backend/examples/ingest.example.json`. Swagger: `/docs` backend.

Маршрутов управления серверами, контейнерами, настройками интеграций или авторизацией нет. `/services` не используется: доступность показана по хостам через `/availability`.
