export async function request(path, params = {}, options = {}) {
    const query = new URLSearchParams(
        Object.entries(params).filter(([, value]) => value != null && value !== ''),
    ).toString()
    let response
    try {
        response = await fetch(`/api/v1${path}${query ? `?${query}` : ''}`, {
            ...options,
            signal: options.signal ?? AbortSignal.timeout(15000),
        })
    } catch {
        throw new Error('Backend недоступен. Проверьте соединение и повторите запрос.')
    }
    if (!response.ok) {
        let message = `Ошибка ${response.status}`
        try {
            const body = await response.json()
            message =
                typeof body.detail === 'string'
                    ? body.detail
                    : JSON.stringify(body.detail) || message
        } catch {}
        throw new Error(message)
    }
    return response.json()
}

export function importReports(file) {
    const body = new FormData()
    body.append('file', file)
    return request('/import', {}, { method: 'POST', body })
}
