import { level, pct } from '../utils/format'
export default function MetricBar({ value, wide, showValue = true }) {
    const l = level(value)
    if (value == null && showValue) return <span className="dash">—</span>
    return (
        <div className="bar-wrap">
            <div className={`bar${wide ? ' w' : ''}${l === 'off' ? ' off' : ''}`}>
                <i className={l} style={{ width: `${value ?? 0}%` }} />
            </div>
            {showValue && <span className={l === 'crit' ? 'v-crit' : ''}>{pct(value)}</span>}
        </div>
    )
}
