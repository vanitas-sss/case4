import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAlerts, useHealth } from '../api'
import Query from './Query'
import { agoIso } from '../utils/time'

function Notifications() {
    const [open, setOpen] = useState(false),
        [read, setRead] = useState([])
    const query = useAlerts({ status: 'active' })
    const rows = query.data ?? []
    const unread = rows.filter((row) => !read.includes(row.id)).length
    return (
        <div className="notification-wrap">
            <button className="btn" aria-expanded={open} onClick={() => setOpen(!open)}>
                Тревоги{unread ? `: ${unread}` : ''}
            </button>
            {open && (
                <div className="notif">
                    <header className="row spread">
                        <b>Активные тревоги</b>
                        <button className="link-btn" onClick={() => setOpen(false)}>
                            Закрыть
                        </button>
                    </header>
                    <Query q={query} emptyTitle="Активных тревог нет">
                        {(alerts) => (
                            <>
                                <Link className="link-btn" to="/alerts" onClick={() => setOpen(false)}>
                                    Все оповещения
                                </Link>
                                {' · '}
                                <button
                                    className="link-btn"
                                    onClick={() => setRead(alerts.map((row) => row.id))}
                                >
                                    Прочитать текущие
                                </button>
                                {alerts.map((row) => (
                                    <div className="notif-item" key={row.id}>
                                        <i
                                            className={`dot ${row.severity === 'critical' ? 'crit' : 'warn'}`}
                                        />
                                        <div>
                                            <b>{row.message}</b>
                                            <small>{row.host ?? row.target}</small>
                                        </div>
                                        <time>{agoIso(row.started_at)}</time>
                                    </div>
                                ))}
                                <p className="sub">
                                    Отметки прочтения действуют до перезагрузки страницы. Тревоги
                                    закрываются backend после восстановления.
                                </p>
                            </>
                        )}
                    </Query>
                </div>
            )}
        </div>
    )
}

export default function PageHeader({ title, subtitle }) {
    const health = useHealth()
    const connected = health.isSuccess && !health.isError
    return (
        <div className="ph">
            <div>
                <h1>{title}</h1>
                {subtitle && <p>{subtitle}</p>}
            </div>
            <div className="ph-right">
                <div className="live" role="status">
                    <i className={`dot ${connected ? 'ok' : 'crit'}`} />
                    <b>
                        {health.isPending
                            ? 'Подключение…'
                            : connected
                              ? 'API доступен'
                              : 'Нет связи с API'}
                    </b>
                </div>
                <Notifications />
            </div>
        </div>
    )
}
