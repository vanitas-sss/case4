import test from 'node:test'
import assert from 'node:assert/strict'
import { containerView, matchesHost, metricStats, fmtPct2 } from '../src/utils/format.js'

test('missing host fields do not crash search', () => {
    assert.equal(matchesHost({ name: 'one', ip: null }, 'absent'), false)
    assert.equal(matchesHost({ name: 'one', source_id: 'agent' }, 'AGENT'), true)
})
test('null metrics are not zeros', () => {
    assert.deepEqual(metricStats([{ cpu: null }, { cpu: 40 }, { cpu: 0 }], 'cpu'), {
        average: 20,
        min: 0,
        max: 40,
        count: 2,
    })
    assert.equal(metricStats([{ cpu: null }], 'cpu').average, null)
    assert.equal(fmtPct2(null), '—')
})
test('Docker stopped states are recognized', () => {
    for (const status of ['exited', 'dead', 'stopped'])
        assert.equal(containerView(status).tone, 'crit')
    assert.equal(containerView('unknown').tone, 'off')
})
