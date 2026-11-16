import { useState } from 'react'
import { useAvailability } from '../../api'
import PageHeader from '../../components/PageHeader'
import Query from '../../components/Query'
import StatusBadge from '../../components/StatusBadge'
import { hostView, fmtPct2 } from '../../utils/format'
import { agoIso } from '../../utils/time'

export default function AvailabilityPage() {
    const [period, setPeriod] = useState('24h')
    const query = useAvailability(period)

    return (
        <>
            <PageHeader title="Доступность" subtitle="История проверок состояния серверов" />
            <div className="card">
                <div className="availability-controls">
                    <label className="filter-field">
                        Период
                        <select
                            className="input"
                            value={period}
                            onChange={(event) => setPeriod(event.target.value)}
                            aria-label="Период доступности"
                        >
                            {['1h', '6h', '24h', '7d'].map((value) => (
                                <option key={value} value={value}>
                                    {value}
                                </option>
                            ))}
                        </select>
                    </label>
                </div>
                <Query q={query} emptyTitle="Данных о доступности пока нет">
                    {(rows) => (
                        <div className="table-scroll">
                            <table className="tbl">
                                <thead>
                                    <tr>
                                        <th>Сервер</th>
                                        <th>Статус</th>
                                        <th>Последний сигнал</th>
                                        <th>Проверок</th>
                                        <th>Доступность</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows.map((row) => (
                                        <tr key={row.host_id}>
                                            <td>{row.host}</td>
                                            <td>
                                                <StatusBadge {...hostView(row)} />
                                            </td>
                                            <td>{agoIso(row.last_seen)}</td>
                                            <td>{row.checks_total}</td>
                                            <td>
                                                <div className="uptime-cell">
                                                    <div className="uptime-track">
                                                        <i
                                                            style={{
                                                                width: `${row.uptime_percent ?? 0}%`,
                                                            }}
                                                        />
                                                    </div>
                                                    <span>{fmtPct2(row.uptime_percent)}</span>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </Query>
                <p className="sub">
                    Доступность рассчитывается по проверкам во время работы backend. Если проверок
                    нет, значение не определяется.
                </p>
            </div>
        </>
    )
}
