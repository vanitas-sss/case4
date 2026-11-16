import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useHosts } from '../../api'
import PageHeader from '../../components/PageHeader'
import Query from '../../components/Query'
import StatusBadge from '../../components/StatusBadge'
import MetricBar from '../../components/MetricBar'
import { hostView, matchesHost } from '../../utils/format'
import HostPanel from './HostPanel'
import HostCard from './HostCard'

export default function HostsPage() {
    const hosts = useHosts()
    const [search, setSearch] = useState(''),
        [status, setStatus] = useState(''),
        [selected, setSelected] = useState(null),
        [view, setView] = useState('cards')
    return (
        <>
            <PageHeader title="Серверы" subtitle="Узлы инфраструктуры" />
            <div className="row spread filters">
                <input
                    className="input"
                    aria-label="Поиск сервера"
                    placeholder="Имя, IP или источник"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
                <select
                    className="input"
                    aria-label="Статус сервера"
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                >
                    <option value="">Все статусы</option>
                    <option value="online">В сети</option>
                    <option value="warning">Задержка</option>
                    <option value="offline">Нет связи</option>
                    <option value="unknown">Нет данных</option>
                </select>
                <Link className="btn primary" to="/sources">
                    Подключить источник
                </Link>
            </div>
            <div className="card">
                <Query q={hosts}>
                    {(rows) => {
                        const shown = rows.filter(
                            (host) =>
                                (!status || host.status === status) && matchesHost(host, search),
                        )
                        return shown.length ? (
                            <>
                                <div
                                    className="tabs"
                                    role="group"
                                    aria-label="Режим отображения серверов"
                                >
                                    {[
                                        ['cards', 'Карточки'],
                                        ['table', 'Таблица'],
                                    ].map(([value, label]) => (
                                        <button
                                            key={value}
                                            className={`tab ${view === value ? 'on' : ''}`}
                                            aria-pressed={view === value}
                                            onClick={() => setView(value)}
                                        >
                                            {label}
                                        </button>
                                    ))}
                                </div>
                                {view === 'cards' ? (
                                    <div className="hosts-grid">
                                        {shown.map((host) => (
                                            <HostCard
                                                key={host.id}
                                                host={host}
                                                onOpen={() => setSelected(host.id)}
                                            />
                                        ))}
                                    </div>
                                ) : (
                                    <div className="table-scroll">
                                        <table className="tbl nd">
                                            <thead>
                                                <tr>
                                                    <th>Узел</th>
                                                    <th>IP</th>
                                                    <th>CPU</th>
                                                    <th>RAM</th>
                                                    <th>Диск</th>
                                                    <th>Статус</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {shown.map((host) => (
                                                    <tr key={host.id}>
                                                        <td>
                                                            <button
                                                                className="link-btn"
                                                                onClick={() => setSelected(host.id)}
                                                            >
                                                                {host.name}
                                                            </button>
                                                        </td>
                                                        <td>{host.ip ?? '—'}</td>
                                                        {[
                                                            'cpu_percent',
                                                            'memory_percent',
                                                            'disk_percent',
                                                        ].map((field) => (
                                                            <td key={field}>
                                                                <MetricBar
                                                                    value={
                                                                        host.status === 'online'
                                                                            ? host[field]
                                                                            : null
                                                                    }
                                                                />
                                                            </td>
                                                        ))}
                                                        <td>
                                                            <StatusBadge {...hostView(host)} />
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </>
                        ) : (
                            <p className="nodata">Серверов по этому запросу нет</p>
                        )
                    }}
                </Query>
            </div>
            {selected != null && <HostPanel id={selected} onClose={() => setSelected(null)} />}
        </>
    )
}
