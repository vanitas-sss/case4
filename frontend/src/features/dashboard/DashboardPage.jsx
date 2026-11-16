import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAvailability, useEvents, useInfraLoad, useSummary } from '../../api'
import PageHeader from '../../components/PageHeader'
import Query from '../../components/Query'
import MetricsChart from '../../components/MetricsChart'
import StatusBadge from '../../components/StatusBadge'
import SummaryCards from './SummaryCards'
import { eventLevel, fmtPct2 } from '../../utils/format'
import { hms } from '../../utils/time'

export function EventsTable({ events }) {
    return (
        <div className="table-scroll">
            <table className="tbl">
                <thead>
                    <tr>
                        <th>Время</th>
                        <th>Сервер</th>
                        <th>Событие</th>
                        <th>Тип</th>
                    </tr>
                </thead>
                <tbody>
                    {events.map((event) => (
                        <tr key={event.id}>
                            <td>{hms(event.timestamp)}</td>
                            <td>{event.host}</td>
                            <td>{event.message}</td>
                            <td>
                                <StatusBadge {...eventLevel(event)} />
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export default function DashboardPage() {
    const [period, setPeriod] = useState('6h')
    const summary = useSummary(),
        load = useInfraLoad(period)
    const events = useEvents({ limit: 5 }),
        availability = useAvailability('24h')
    return (
        <>
            <PageHeader title="Обзор" subtitle="Состояние инфраструктуры по принятым отчётам" />
            <div className="stack">
                <Query q={summary}>{(data) => <SummaryCards s={data} />}</Query>
                <div className="card">
                    <div className="card-head">
                        <div>
                            <h2>Нагрузка инфраструктуры</h2>
                            <p className="sub">
                                Средние значения по отчитавшимся узлам; пропуски не заменяются
                                нулями
                            </p>
                        </div>
                        <div className="tabs">
                            {['1h', '6h', '24h', '7d'].map((value) => (
                                <button
                                    key={value}
                                    className={`tab ${period === value ? 'on' : ''}`}
                                    onClick={() => setPeriod(value)}
                                >
                                    {value}
                                </button>
                            ))}
                        </div>
                    </div>
                    <Query q={load} emptyTitle="Измерений пока нет">
                        {(data) => <MetricsChart data={data} />}
                    </Query>
                </div>
                <div className="card">
                    <h2>Доступность серверов за 24 часа</h2>
                    <p className="sub">
                        Доля успешных проверок во время работы backend; не время работы ОС
                    </p>
                    <Query q={availability}>
                        {(rows) =>
                            rows.map((row) => (
                                <div className="kv" key={row.host_id}>
                                    <span>{row.host}</span>
                                    <span>
                                        {fmtPct2(row.uptime_percent)} · проверок: {row.checks_total}
                                    </span>
                                </div>
                            ))
                        }
                    </Query>
                </div>
                <div className="card">
                    <div className="card-head">
                        <h2>Последние события</h2>
                        <Link to="/events">Все события →</Link>
                    </div>
                    <Query q={events}>{(rows) => <EventsTable events={rows} />}</Query>
                </div>
            </div>
        </>
    )
}
