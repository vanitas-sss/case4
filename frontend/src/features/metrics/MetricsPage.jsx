import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useHosts } from '../../api'
import { request } from '../../api/client'
import PageHeader from '../../components/PageHeader'
import Query from '../../components/Query'
import MetricsChart from '../../components/MetricsChart'
import { fmt1, metricStats } from '../../utils/format'

const METRICS = { cpu_percent: 'CPU', memory_percent: 'RAM', disk_percent: 'Диск' }

export default function MetricsPage() {
    const [params] = useSearchParams()
    const [host, setHost] = useState(params.get('host') ?? ''),
        [period, setPeriod] = useState('6h'),
        [field, setField] = useState('cpu_percent')
    const hosts = useHosts()
    const query = useQuery({
        queryKey: ['series', host, period],
        queryFn: ({ signal }) =>
            request(host ? `/hosts/${host}/metrics` : '/metrics/infra', { period }, { signal }),
        refetchInterval: 15000,
    })
    return (
        <>
            <PageHeader title="Метрики" subtitle="История измерений" />
            <div className="stack">
                <div className="card filters row">
                    <label>
                        Источник
                        <select
                            className="input"
                            value={host}
                            onChange={(e) => setHost(e.target.value)}
                        >
                            <option value="">Все узлы</option>
                            {(hosts.data ?? []).map((row) => (
                                <option key={row.id} value={row.id}>
                                    {row.name}
                                </option>
                            ))}
                        </select>
                    </label>
                    <label>
                        Метрика
                        <select
                            className="input"
                            value={field}
                            onChange={(e) => setField(e.target.value)}
                        >
                            {Object.entries(METRICS).map(([key, name]) => (
                                <option key={key} value={key}>
                                    {name}
                                </option>
                            ))}
                        </select>
                    </label>
                    <label>
                        Период
                        <select
                            className="input"
                            value={period}
                            onChange={(e) => setPeriod(e.target.value)}
                        >
                            {['1h', '6h', '24h', '7d'].map((value) => (
                                <option key={value}>{value}</option>
                            ))}
                        </select>
                    </label>
                </div>
                {hosts.isError && <p role="alert">Не удалось загрузить список серверов.</p>}
                <div className="card">
                    <h2>Загрузка: {METRICS[field]}</h2>
                    <Query q={query}>
                        {(rows) => (
                            <>
                                <MetricsChart
                                    data={rows}
                                    series={[{ key: field, name: METRICS[field] }]}
                                />
                                <div className="sum3">
                                    {Object.entries({
                                        Среднее: metricStats(rows, field).average,
                                        Максимум: metricStats(rows, field).max,
                                        Минимум: metricStats(rows, field).min,
                                    }).map(([label, value]) => (
                                        <div key={label}>
                                            <div className="label">{label}</div>
                                            <div className="big">{fmt1(value)}</div>
                                        </div>
                                    ))}
                                </div>
                                <p className="sub">
                                    Статистика по показанным точкам, без отсутствующих измерений. До
                                    500 точек за период. Для всех узлов используются средние по
                                    временным интервалам, для одного — выборка измерений.
                                </p>
                            </>
                        )}
                    </Query>
                </div>
            </div>
        </>
    )
}
