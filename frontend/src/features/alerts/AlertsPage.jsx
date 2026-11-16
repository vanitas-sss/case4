import { useState } from 'react'
import { useAlerts } from '../../api'
import PageHeader from '../../components/PageHeader'
import Query from '../../components/Query'
import StatusBadge from '../../components/StatusBadge'
import { agoIso } from '../../utils/time'

export default function AlertsPage() {
    const [status, setStatus] = useState('active')
    const query = useAlerts({ status })
    return (
        <>
            <PageHeader title="Оповещения" subtitle="Проблемы и история восстановления" />
            <div className="card">
                <div className="tabs" role="group" aria-label="Состояние оповещений">
                    {[
                        ['active', 'Активные'],
                        ['resolved', 'Завершённые'],
                    ].map(([value, label]) => (
                        <button
                            key={value}
                            type="button"
                            className={`tab ${status === value ? 'on' : ''}`}
                            aria-pressed={status === value}
                            onClick={() => setStatus(value)}
                        >
                            {label}
                        </button>
                    ))}
                </div>
                <Query
                    q={query}
                    emptyTitle={
                        status === 'active'
                            ? 'Активных оповещений нет'
                            : 'Истории оповещений пока нет'
                    }
                >
                    {(rows) => (
                        <div className="table-scroll">
                            <table className="tbl">
                                <thead>
                                    <tr>
                                        <th>Узел</th>
                                        <th>Сообщение</th>
                                        <th>Важность</th>
                                        <th>{status === 'active' ? 'Возникло' : 'Закрыто'}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows.map((item) => (
                                        <tr key={item.id}>
                                            <td>{item.host ?? item.target}</td>
                                            <td>{item.message}</td>
                                            <td>
                                                <StatusBadge
                                                    label={
                                                        item.severity === 'critical'
                                                            ? 'Критично'
                                                            : 'Предупреждение'
                                                    }
                                                    tone={
                                                        item.severity === 'critical'
                                                            ? 'crit'
                                                            : 'warn'
                                                    }
                                                />
                                            </td>
                                            <td>
                                                {agoIso(
                                                    status === 'active'
                                                        ? item.started_at
                                                        : item.resolved_at,
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </Query>
                <p className="sub">
                    Оповещения создаются и закрываются автоматически. Доставка в мессенджеры не
                    используется.
                </p>
            </div>
        </>
    )
}
