# Демонстрационные данные

Это **генератор JSON**, не агент сбора реальных метрик.

```bash
python -m pip install -r requirements.txt
python generator.py
python seed.py --minutes 60
```

Сценарий отказов: `python generator.py --scenario scenario_full_demo.json`. Для разового просмотра: `python generator.py --once --dry-run`.

Во время обычной работы можно редактировать `state.json`: `servers` управляет пропуском отчётов, `containers` — статусами контейнеров, `cpu_override` — CPU. Формат: [контракт](../contracts/api-examples.json).
