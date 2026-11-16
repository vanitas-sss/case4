# Сценарий демонстрации

```bash
docker compose --profile demo up --build -d --wait
docker compose --profile demo run --rm generator python seed.py --minutes 60
```

Откройте http://localhost:8080. Графики истории появятся после заполнения данными.

```bash
docker compose --profile demo run --rm generator python generator.py --scenario scenario_full_demo.json
```

- 1:00 — `server-02` перестаёт отправлять отчёты; далее warning → offline → тревога.
- 2:00 — сервер возвращается, тревога закрывается.
- 2:30 — `backend` останавливается, появляется предупреждение.
- 3:00 — контейнер снова работает.
- 3:30 — высокая нагрузка `server-03`, 5:30 — восстановление.

Проверяйте страницы «Обзор», «Серверы», «Контейнеры», «Топология», «События», «Оповещения». Генератор можно остановить через `Ctrl+C` после окончания сценария.
