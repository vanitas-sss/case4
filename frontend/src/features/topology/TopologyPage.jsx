import { useState } from 'react'
import { useHosts, useTopology } from '../../api'
import PageHeader from '../../components/PageHeader'
import Query from '../../components/Query'
import { containerView, hostView } from '../../utils/format'

function NetworkGraph({ data }) {
    const [selected, setSelected] = useState(null)
    const columns = ['server', 'network', 'container']
    const groups = new Map(columns.map((type) => [type, []]))
    for (const node of data.nodes) {
        const type = groups.has(node.type) ? node.type : 'network'
        groups.get(type).push(node)
    }
    const positions = new Map()
    columns.forEach((type, column) =>
        groups
            .get(type)
            .forEach((node, index) =>
                positions.set(node.id, { x: 120 + column * 300, y: 70 + index * 90 }),
            ),
    )
    const height = Math.max(260, ...[...groups.values()].map((rows) => rows.length * 90 + 40))
    const active = data.nodes.find((node) => node.id === selected)
    return (
        <>
            <p className="sub">
                Нажмите на узел, чтобы увидеть его параметры. Расположение вычисляется для просмотра
                и не меняет данные источника.
            </p>
            <div className="topology-legend" aria-label="Обозначения состояний">
                {[
                    ['ok', 'В сети'],
                    ['warn', 'Задержка'],
                    ['crit', 'Проблема'],
                    ['off', 'Нет данных'],
                ].map(([tone, label]) => (
                    <span key={tone}>
                        <i className={`dot ${tone}`} />
                        {label}
                    </span>
                ))}
            </div>
            <div className="network-scroll">
                <svg
                    viewBox={`0 0 850 ${height}`}
                    style={{ minWidth: 650, width: '100%' }}
                    aria-label="Граф топологии"
                >
                    {data.links.map((link, index) => {
                        const from = positions.get(link.source),
                            to = positions.get(link.target)
                        return (
                            from &&
                            to && (
                                <line
                                    key={`${link.source}-${link.target}-${index}`}
                                    x1={from.x}
                                    y1={from.y}
                                    x2={to.x}
                                    y2={to.y}
                                    stroke={
                                        selected === link.source || selected === link.target
                                            ? '#E8B04A'
                                            : '#888'
                                    }
                                    strokeWidth={1.5 + (link.load ?? 0) / 25}
                                    opacity={0.45 + (link.load ?? 0) / 200}
                                >
                                    <title>
                                        {link.type}: {link.source} → {link.target}
                                    </title>
                                </line>
                            )
                        )
                    })}
                    {data.nodes.map((node) => {
                        const position = positions.get(node.id)
                        const view =
                            node.type === 'container' ? containerView(node.status) : hostView(node)
                        const color = {
                            ok: '#88BDA5',
                            warn: '#E8B04A',
                            crit: '#F0584B',
                            off: '#999',
                        }[view.tone]
                        return (
                            <g
                                key={node.id}
                                role="button"
                                tabIndex={0}
                                aria-label={`Узел ${node.label}`}
                                onClick={() => setSelected(node.id)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' || e.key === ' ') {
                                        e.preventDefault()
                                        setSelected(node.id)
                                    }
                                }}
                                style={{ cursor: 'pointer' }}
                            >
                                <rect
                                    x={position.x - 100}
                                    y={position.y - 26}
                                    width="200"
                                    height="52"
                                    rx="8"
                                    fill="#20201e"
                                    stroke={color}
                                    strokeWidth={selected === node.id ? 3 : 1}
                                />
                                <text
                                    x={position.x}
                                    y={position.y - 3}
                                    textAnchor="middle"
                                    fill="#eee"
                                    fontSize="13"
                                >
                                    {node.label.length > 24
                                        ? `${node.label.slice(0, 23)}…`
                                        : node.label}
                                </text>
                                <text
                                    x={position.x}
                                    y={position.y + 16}
                                    textAnchor="middle"
                                    fill={color}
                                    fontSize="11"
                                >
                                    {node.type} · {view.label}
                                </text>
                            </g>
                        )
                    })}
                </svg>
            </div>
            {active && (
                <div className="kv">
                    <span>
                        {active.label} · {active.type}
                    </span>
                    <span>
                        {active.id} · {active.ip ?? 'IP не указан'} · {active.status}
                    </span>
                </div>
            )}
            <details>
                <summary>Связи: {data.links.length}</summary>
                <div className="table-scroll">
                    <table className="tbl">
                        <thead>
                            <tr>
                                <th>Откуда</th>
                                <th>Куда</th>
                                <th>Тип</th>
                                <th>Загрузка из отчёта</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.links.map((link, index) => (
                                <tr key={index}>
                                    <td>{link.source}</td>
                                    <td>{link.target}</td>
                                    <td>{link.type}</td>
                                    <td>{link.load ?? '—'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </details>
        </>
    )
}

export default function TopologyPage() {
    const [host, setHost] = useState('')
    const [type, setType] = useState('')
    const hosts = useHosts(),
        topology = useTopology({ host_id: host, type })
    return (
        <>
            <PageHeader title="Топология" subtitle="Узлы и связи из отчётов источников" />
            <div className="card">
                <div className="topology-controls">
                    <label className="filter-field">
                        Сервер
                        <select
                            className="input"
                            aria-label="Сервер топологии"
                            value={host}
                            onChange={(e) => setHost(e.target.value)}
                        >
                            <option value="">Все серверы</option>
                            {(hosts.data ?? []).map((row) => (
                                <option key={row.id} value={row.id}>
                                    {row.name}
                                </option>
                            ))}
                        </select>
                    </label>
                    <label className="filter-field">
                        Тип узла
                        <select
                            className="input"
                            aria-label="Тип узла топологии"
                            value={type}
                            onChange={(event) => setType(event.target.value)}
                        >
                            <option value="">Все типы</option>
                            <option value="server">Серверы</option>
                            <option value="container">Контейнеры</option>
                            <option value="network">Сети</option>
                        </select>
                    </label>
                </div>
                <Query
                    q={topology}
                    empty={(data) => !data?.nodes?.length}
                    emptyTitle="Топология пока не получена"
                >
                    {(data) => <NetworkGraph key={host} data={data} />}
                </Query>
            </div>
        </>
    )
}
