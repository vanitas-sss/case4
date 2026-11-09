# mock-data — заглушка агента

Скрипт ведёт себя как настоящий агент (кейс 1): шлёт массив отчётов на `/api/v1/ingest`.
Формат — `../contracts/api-examples.json`.

```bash
pip install -r requirements.txt
python generator.py --url http://localhost:8000/api/v1/ingest --interval 5   # обычная работа
python generator.py --scenario scenario_full_demo.json                        # автосценарий (~6 мин)
python seed.py --minutes 60                                                   # история за час
python generator.py --dry-run --once                                          # посмотреть JSON
```

## Ручное управление (state.json)
Файл перечитывается каждый шаг, правьте его во время показа:
- `"servers": {"server-02": "offline"}` — сервер перестаёт слать данные (как упавший агент);
- `"containers": {"backend": "stopped"}` — контейнер уходит в stopped (`restarting` тоже можно);
- `"cpu_override": {"server-03": 95}` — держит CPU около 95%.

## Сценарий full_demo
| t | Событие |
|---|---|
| 1:00 | server-02 замолчал |
| 2:00 | server-02 вернулся |
| 2:30 | контейнер backend stopped |
| 3:00 | backend running |
| 3:30 | CPU server-03 = 95% |
| 5:30 | CPU server-03 в норму |

## Типы связей в network.links
`host` (сервер→контейнер), `network` (контейнер→Docker-сеть), `traffic` (контейнер→контейнер).
Тип `traffic` добавлен сверх плана — нужно согласовать с Марией и Сергеем (стиль линии на графе).
