# Проверки

## Автоматические

```bash
cd backend && python -m pytest
cd frontend && npm ci && npm run lint && npm run format:check && npm test && npm run build
```

Интеграционные тесты Playwright запускаются через GitHub Actions
