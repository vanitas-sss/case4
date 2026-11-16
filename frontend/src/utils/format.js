export const pct = (value) => (Number.isFinite(value) ? `${Math.round(value)}%` : '—')
export const fmt1 = (value) =>
    Number.isFinite(value) ? `${value.toFixed(1).replace('.', ',')}%` : '—'
export const fmtPct2 = (value) =>
    Number.isFinite(value) ? `${value.toFixed(2).replace('.', ',')}%` : '—'
export const level = (value) =>
    value == null ? 'off' : value >= 90 ? 'crit' : value >= 75 ? 'warn' : 'ok'

export function hostView(host) {
    const states = {
        offline: ['crit', 'Нет связи'],
        warning: ['warn', 'Задержка'],
        unknown: ['off', 'Нет данных'],
    }
    const [tone, label] = states[host.status] ?? ['ok', 'В сети']
    return { tone, label }
}

export function containerView(status) {
    const states = {
        running: ['ok', 'Работает'],
        restarting: ['warn', 'Перезапускается'],
        paused: ['warn', 'Приостановлен'],
        stopped: ['crit', 'Остановлен'],
        exited: ['crit', 'Завершён'],
        dead: ['crit', 'Ошибка'],
        created: ['off', 'Создан'],
    }
    const [tone, label] = states[status] ?? ['off', 'Нет данных']
    return { tone, label }
}

export const EVENT_META = {
    host_offline: { tone: 'crit', label: 'Потеря связи' },
    host_warning: { tone: 'warn', label: 'Задержка' },
    host_online: { tone: 'ok', label: 'Восстановление' },
    container_started: { tone: 'info', label: 'Запуск' },
    container_stopped: { tone: 'warn', label: 'Остановка' },
    alert_opened: { tone: 'warn', label: 'Открыта тревога' },
    alert_resolved: { tone: 'ok', label: 'Тревога закрыта' },
    source_registered: { tone: 'info', label: 'Регистрация' },
}
export const eventLevel = (event) => EVENT_META[event.type] ?? { tone: 'info', label: event.type }
export const matchesHost = (host, query) =>
    [host.name, host.ip, host.source_id].some((value) =>
        String(value ?? '')
            .toLowerCase()
            .includes(query.toLowerCase()),
    )

export function metricStats(rows, field) {
    const values = rows.map((row) => row[field]).filter(Number.isFinite)
    return values.length
        ? {
              average: values.reduce((sum, value) => sum + value, 0) / values.length,
              min: Math.min(...values),
              max: Math.max(...values),
              count: values.length,
          }
        : { average: null, min: null, max: null, count: 0 }
}
