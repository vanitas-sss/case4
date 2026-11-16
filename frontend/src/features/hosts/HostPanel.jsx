import { Link } from 'react-router-dom'
import { useEvents, useHost, useMetrics } from '../../api'
import SidePanel from '../../components/SidePanel'
import Query from '../../components/Query'
import StatusBadge from '../../components/StatusBadge'
import MetricsChart from '../../components/MetricsChart'
import { hostView, pct } from '../../utils/format'
import { agoIso } from '../../utils/time'
import { EventsTable } from '../dashboard/DashboardPage'

export default function HostPanel({ id, onClose }) {
    const host = useHost(id),
        metrics = useMetrics(id),
        events = useEvents({ host_id: id, limit: 50 })
    return (
        <SidePanel
            onClose={onClose}
            footer={
                <Link className="btn primary" to={`/metrics?host=${id}`}>
                    Открыть метрики
                </Link>
            }
        >
            <Query q={host}>
                {(data) => (
                    <>
                        <h2>{data.name}</h2>
                        <StatusBadge {...hostView(data)} />
                        {[
                            ['IP', data.ip ?? '—'],
                            ['Источник', data.source_id],
                            ['Последний сигнал', agoIso(data.last_seen)],
                            [
                                'Измерение',
                                data.metric_timestamp
                                    ? new Date(data.metric_timestamp).toLocaleString('ru-RU')
                                    : '—',
                            ],
                            ['CPU', pct(data.cpu_percent)],
                            ['RAM', pct(data.memory_percent)],
                            ['Диск', pct(data.disk_percent)],
                            [
                                'Контейнеры работают / всего',
                                `${data.containers_running} / ${data.containers_total}`,
                            ],
                        ].map(([label, value]) => (
                            <div className="kv" key={label}>
                                <span>{label}</span>
                                <span>{value}</span>
                            </div>
                        ))}
                        <p className="sub">
                            Значения относятся к последнему измерению. При потере связи новых данных
                            нет.
                        </p>
                    </>
                )}
            </Query>
            <h3>Нагрузка за час</h3>
            <Query q={metrics}>{(rows) => <MetricsChart data={rows} height={180} />}</Query>
            <h3>Последние события сервера</h3>
            <Query q={events}>{(rows) => <EventsTable events={rows} />}</Query>
        </SidePanel>
    )
}
