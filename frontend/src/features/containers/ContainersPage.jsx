import { useState } from 'react'
import { useContainers } from '../../api'
import PageHeader from '../../components/PageHeader'
import Query from '../../components/Query'
import StatCards from '../../components/StatCards'
import StatusBadge from '../../components/StatusBadge'
import SidePanel from '../../components/SidePanel'
import { containerView } from '../../utils/format'
import { agoIso } from '../../utils/time'

export default function ContainersPage() {
    const query = useContainers(),
        [selected, setSelected] = useState(null)
    const current = (query.data ?? []).find((row) => row.id === selected)
    return (
        <>
            <PageHeader title="Контейнеры" subtitle="Состояния из отчётов источников" />
            <Query q={query}>
                {(rows) => (
                    <div className="stack">
                        <StatCards
                            items={[
                                ['Всего', rows.length, 'off', 'Известные контейнеры'],
                                [
                                    'Работают',
                                    rows.filter((c) => c.status === 'running').length,
                                    'ok',
                                    'Свежие данные',
                                ],
                                [
                                    'Остановлены',
                                    rows.filter((c) =>
                                        ['stopped', 'exited', 'dead'].includes(c.status),
                                    ).length,
                                    'crit',
                                    'По последнему отчёту',
                                ],
                                [
                                    'Нет данных',
                                    rows.filter((c) => c.status === 'unknown').length,
                                    'off',
                                    'Состояние неизвестно',
                                ],
                            ]}
                        />
                        <div className="card table-scroll">
                            <table className="tbl nd">
                                <thead>
                                    <tr>
                                        <th>Контейнер</th>
                                        <th>Образ</th>
                                        <th>Сервер</th>
                                        <th>Статус</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows.map((row) => (
                                        <tr key={row.id}>
                                            <td>
                                                <button
                                                    className="link-btn"
                                                    onClick={() => setSelected(row.id)}
                                                >
                                                    {row.name}
                                                </button>
                                            </td>
                                            <td>{row.image ?? '—'}</td>
                                            <td>{row.host_name}</td>
                                            <td>
                                                <StatusBadge {...containerView(row.status)} />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <p className="sub">
                            Сервис наблюдает за контейнерами. Удалённое управление и измерения
                            ресурсов отдельных контейнеров источником не предоставляются.
                        </p>
                    </div>
                )}
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
