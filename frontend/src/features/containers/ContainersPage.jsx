import { useState } from 'react'
import { useContainers } from '../../api'
import PageHeader from '../../components/PageHeader'
import Query from '../../components/Query'
import StatCards from '../../components/StatCards'
import StatusBadge from '../../components/StatusBadge'
import SidePanel from '../../components/SidePanel'
import { containerView } from '../../utils/format'
import { agoIso } from '../../utils/time'

function ContainerCard({ item, onOpen }) {
    return (
        <article className={`container-card ${item.status === 'unknown' ? 'unknown' : ''}`}>
            <div className="container-card-title">
                <button className="link-btn" onClick={onOpen}>
                    {item.name}
                </button>
                <StatusBadge {...containerView(item.status)} />
            </div>
            {[
                ['Образ', item.image ?? '—'],
                ['IP', item.ip ?? '—'],
                ['Сети', (item.networks ?? []).join(', ') || '—'],
            ].map(([label, value]) => (
                <div className="kv" key={label}>
                    <span>{label}</span>
                    <span>{value}</span>
                </div>
            ))}
        </article>
    )
}

export default function ContainersPage() {
    const query = useContainers()
    const [selected, setSelected] = useState(null)
    const [server, setServer] = useState('')
    const [status, setStatus] = useState('')
    const current = (query.data ?? []).find((row) => row.id === selected)

    return (
        <>
            <PageHeader title="Контейнеры" subtitle="Контейнеры по серверам" />
            <Query q={query}>
                {(rows) => {
                    const serverNames = [...new Set(rows.map((item) => item.host_name))].sort()
                    const shown = rows.filter(
                        (item) =>
                            (!server || item.host_name === server) &&
                            (!status || item.status === status),
                    )
                    const groups = new Map()
                    for (const item of shown) {
                        if (!groups.has(item.host_name)) groups.set(item.host_name, [])
                        groups.get(item.host_name).push(item)
                    }

                    return (
                        <div className="stack">
                            <StatCards
                                items={[
                                    ['Всего', rows.length, 'off', 'Известные контейнеры'],
                                    [
                                        'Работают',
                                        rows.filter((item) => item.status === 'running').length,
                                        'ok',
                                        'Свежие данные',
                                    ],
                                    [
                                        'Остановлены',
                                        rows.filter((item) =>
                                            ['stopped', 'exited', 'dead'].includes(item.status),
                                        ).length,
                                        'crit',
                                        'По последнему отчёту',
                                    ],
                                    [
                                        'Нет данных',
                                        rows.filter((item) => item.status === 'unknown').length,
                                        'off',
                                        'Состояние неизвестно',
                                    ],
                                ]}
                            />
                            <div className="card">
                                <div className="container-filters">
                                    <label className="filter-field">
                                        Сервер
                                        <select
                                            className="input"
                                            aria-label="Фильтр сервера контейнеров"
                                            value={server}
                                            onChange={(event) => setServer(event.target.value)}
                                        >
                                            <option value="">Все серверы</option>
                                            {serverNames.map((name) => (
                                                <option key={name} value={name}>
                                                    {name}
                                                </option>
                                            ))}
                                        </select>
                                    </label>
                                    <label className="filter-field">
                                        Статус
                                        <select
                                            className="input"
                                            aria-label="Фильтр статуса контейнеров"
                                            value={status}
                                            onChange={(event) => setStatus(event.target.value)}
                                        >
                                            <option value="">Все статусы</option>
                                            <option value="running">Работает</option>
                                            <option value="restarting">Перезапускается</option>
                                            <option value="stopped">Остановлен</option>
                                            <option value="exited">Завершён</option>
                                            <option value="dead">Ошибка</option>
                                            <option value="unknown">Нет данных</option>
                                        </select>
                                    </label>
                                </div>
                                {shown.length ? (
                                    [...groups].map(([name, items]) => (
                                        <section className="container-group" key={name}>
                                            <h2>{name} · {items.length}</h2>
                                            <div className="container-grid">
                                                {items.map((item) => (
                                                    <ContainerCard
                                                        key={item.id}
                                                        item={item}
                                                        onOpen={() => setSelected(item.id)}
                                                    />
                                                ))}
                                            </div>
                                        </section>
                                    ))
                                ) : (
                                    <p className="nodata">Контейнеров по этому запросу нет</p>
                                )}
                            </div>
                            <p className="sub">
                                Состояние контейнеров берётся из последнего отчёта. Если сервер
                                недоступен, статус его контейнеров неизвестен.
                            </p>
                        </div>
                    )
                }}
            </Query>
            {current && (
                <SidePanel onClose={() => setSelected(null)}>
                    <h2>{current.name}</h2>
                    <StatusBadge {...containerView(current.status)} />
                    {[
                        ['Docker ID', current.docker_id],
                        ['Сервер', current.host_name],
                        ['Образ', current.image ?? '—'],
                        ['IP', current.ip ?? '—'],
                        ['Сети', (current.networks ?? []).join(' · ') || '—'],
                        ['Последний сигнал', agoIso(current.last_seen)],
                    ].map(([label, value]) => (
                        <div className="kv" key={label}>
                            <span>{label}</span>
                            <span>{value}</span>
                        </div>
                    ))}
                </SidePanel>
            )}
        </>
    )
}
