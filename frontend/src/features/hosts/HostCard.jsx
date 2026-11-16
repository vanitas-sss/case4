import MetricBar from '../../components/MetricBar'
import StatusBadge from '../../components/StatusBadge'
import { hostView } from '../../utils/format'
import { agoIso } from '../../utils/time'

const METRICS = [
    ['CPU', 'cpu_percent'],
    ['RAM', 'memory_percent'],
    ['Диск', 'disk_percent'],
]

export default function HostCard({ host, onOpen }) {
    return (
        <article className={`host-card ${host.status === 'offline' ? 'is-offline' : ''}`}>
            <div className="row spread host-card-title">
                <button className="link-btn host-name" onClick={onOpen}>
                    {host.name}
                </button>
                <StatusBadge {...hostView(host)} />
            </div>
            <p className="host-ip">{host.ip ?? 'IP не указан'}</p>
            <div className="host-metrics">
                {METRICS.map(([label, field]) => (
                    <div className="host-metric" key={field}>
                        <span>{label}</span>
                        <MetricBar value={host.status === 'online' ? host[field] : null} />
                    </div>
                ))}
            </div>
            <div className="host-card-footer">
                <span>Контейнеры: {host.containers_running} / {host.containers_total}</span>
                <span>{agoIso(host.last_seen)}</span>
            </div>
        </article>
    )
}
