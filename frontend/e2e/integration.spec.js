import { test, expect } from '@playwright/test'

function report(name = 'browser-host', cpu = 42) {
    return {
        source_id: 'browser-tests',
        timestamp: new Date().toISOString(),
        host: {
            name,
            ip: null,
            status: 'online',
            cpu_percent: cpu,
            memory_percent: null,
            disk_percent: 30,
        },
        containers: [
            { id: 'test-container', name: 'web', image: 'nginx', status: 'exited', networks: [] },
        ],
        network: {
            nodes: [
                { id: 'host', label: name, type: 'server' },
                { id: 'test-container', label: 'web', type: 'container' },
            ],
            links: [{ source: 'host', target: 'test-container', type: 'hosts', load: 0 }],
        },
    }
}

async function ingest(request, value) {
    const response = await request.post('/api/v1/ingest', { data: [value] })
    expect(response.ok()).toBeTruthy()
    expect((await response.json()).rejected).toBe(0)
}

async function hostByName(request, name) {
    return (await (await request.get('/api/v1/hosts')).json()).find((host) => host.name === name)
}

test('empty storage renders without made-up metrics', async ({ page, request }) => {
    expect(await (await request.get('/api/v1/hosts')).json()).toEqual([])
    const errors = []
    page.on('pageerror', (error) => errors.push(error.message))
    await page.goto('/')
    await expect(page.getByText('Измерений пока нет')).toBeVisible()
    await expect(page.getByText('API доступен', { exact: true })).toBeVisible()
    await expect(page.locator('body')).not.toContainText('NaN')
    await page.screenshot({ path: 'test-results/empty.png', fullPage: true })
    expect(errors).toEqual([])
})

test('real reports populate every page and host search handles missing fields', async ({
    page,
    request,
}) => {
    await ingest(request, report())
    const errors = [],
        badResponses = []
    page.on('pageerror', (error) => errors.push(error.message))
    page.on('response', (response) => {
        if (response.url().includes('/api/') && response.status() >= 400)
            badResponses.push(`${response.status()} ${response.url()}`)
    })
    await page.goto('/hosts')
    await page.getByLabel('Поиск сервера').fill('not-found')
    await expect(page.getByText('Серверов по этому запросу нет')).toBeVisible()
    await page.getByLabel('Поиск сервера').fill('browser-host')
    await page.getByRole('button', { name: 'browser-host', exact: true }).click()
    await expect(page.getByRole('dialog')).toBeVisible()
    await expect(page.getByRole('dialog')).toContainText('browser-tests')
    await expect(page.getByRole('dialog')).toContainText('Регистрация')
    await page.getByRole('button', { name: 'Закрыть', exact: true }).click()
    for (const path of [
        '/',
        '/containers',
        '/metrics',
        '/events',
        '/sources',
        '/topology',
        '/docs',
    ]) {
        await page.goto(path)
        await expect(page.locator('h1')).toBeVisible()
        await expect(page.getByText('API доступен', { exact: true })).toBeVisible()
        await expect(page.locator('body')).not.toContainText(
            /NaN|undefined|Не удалось отобразить страницу/,
        )
        if (path === '/topology') await expect(page.getByLabel('Граф топологии')).toBeVisible()
        await expect(page.locator('[aria-busy="true"]')).toHaveCount(0)
        await page.screenshot({
            path: `test-results/page-${path.replaceAll('/', '') || 'overview'}.png`,
            fullPage: true,
        })
    }
    expect(errors).toEqual([])
    expect(badResponses).toEqual([])
})

test('week period and correct metric labels', async ({ page, request }) => {
    const host = await hostByName(request, 'browser-host')
    await page.goto(`/metrics?host=${host.id}`)
    await page.getByLabel('Период', { exact: true }).selectOption('7d')
    await page.getByLabel('Метрика', { exact: true }).selectOption('disk_percent')
    await expect(page.getByRole('heading', { name: 'Загрузка: Диск' })).toBeVisible()
    await expect(page.locator('.sum3')).toContainText('30,0%')
    await page.getByLabel('Метрика', { exact: true }).selectOption('memory_percent')
    await expect(page.locator('.sum3')).not.toContainText('0,0%')
    await expect(page.locator('.sum3')).toContainText('—')
})

test('JSON import reports partial rejection and invalid files', async ({ page }) => {
    await page.goto('/sources')
    await page.getByLabel('JSON-файл').setInputFiles({
        name: 'invalid.json',
        mimeType: 'application/json',
        buffer: Buffer.from('broken'),
    })
    await page.getByRole('button', { name: 'Загрузить отчёты' }).click()
    await expect(page.getByRole('alert')).toContainText('JSON')
    const payload = [report('imported-host'), { source_id: 'invalid' }]
    await page.getByLabel('JSON-файл').setInputFiles({
        name: 'report.json',
        mimeType: 'application/json',
        buffer: Buffer.from(JSON.stringify(payload)),
    })
    await page.getByRole('button', { name: 'Загрузить отчёты' }).click()
    await expect(page.getByText('Принято: 1. Отклонено: 1.')).toBeVisible()
    await expect(page.getByText('Отчёт №2')).toBeVisible()
})

test('connection indicator reflects failed health requests', async ({ page }) => {
    await page.route('**/api/v1/health', (route) => route.abort())
    await page.goto('/hosts')
    await expect(page.getByText('Нет связи с API', { exact: true })).toBeVisible()
    await page.unroute('**/api/v1/health')
    await expect(page.getByText('API доступен', { exact: true })).toBeVisible()
})

test('heartbeat outage opens an alert and a new report resolves it', async ({ request }) => {
    const name = 'heartbeat-host'
    await ingest(request, report(name, 10))
    await expect
        .poll(async () => (await hostByName(request, name)).status, {
            timeout: 30000,
            intervals: [1000],
        })
        .toBe('offline')
    await expect
        .poll(
            async () => {
                const alerts = await (await request.get('/api/v1/alerts?status=active')).json()
                return alerts.some((alert) => alert.host === name && alert.rule === 'host_offline')
            },
            { timeout: 20000, intervals: [1000] },
        )
        .toBe(true)
    await ingest(request, report(name, 10))
    expect((await hostByName(request, name)).status).toBe('online')
    const resolved = await (await request.get('/api/v1/alerts?status=resolved')).json()
    expect(resolved.some((alert) => alert.host === name && alert.rule === 'host_offline')).toBe(
        true,
    )
})

test('mobile navigation stays available', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto('/hosts')
    await expect(page.getByRole('link', { name: 'Топология' })).toBeVisible()
    await page.getByRole('link', { name: 'Топология' }).click()
    await expect(page.getByRole('heading', { name: 'Топология', exact: true })).toBeVisible()
    await page.screenshot({ path: 'test-results/mobile.png', fullPage: true })
})
