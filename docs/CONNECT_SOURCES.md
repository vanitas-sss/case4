# Подключение источников

Сервис принимает **массив отчётов**, один объект описывает один сервер. Формат и примеры: [contracts/api-examples.json](../contracts/api-examples.json).

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  --data-binary @backend/examples/ingest.example.json
```

Через сайт можно загрузить JSON на странице «Источники» (не более 2 МиБ). Неверные объекты отклоняются отдельно, с описанием ошибки.

Для проверки потока используйте `mock-data/generator.py`. Это заглушка, не настоящий агент.
