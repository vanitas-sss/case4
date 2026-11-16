import { defineConfig } from '@playwright/test'

export default defineConfig({
    testDir: './e2e',
    timeout: 60000,
    expect: { timeout: 10000 },
    fullyParallel: false,
    workers: 1,
    retries: 0,
    reporter: [['list'], ['html', { open: 'never' }]],
    use: {
        baseURL: process.env.E2E_BASE_URL ?? 'http://127.0.0.1:8080',
        viewport: { width: 1440, height: 1000 },
        screenshot: 'only-on-failure',
        trace: 'retain-on-failure',
    },
})
