import { useState } from 'react'
import { useEvents } from '../../api'
import PageHeader from '../../components/PageHeader'
import Query from '../../components/Query'
import { EVENT_META } from '../../utils/format'
import { EventsTable } from '../dashboard/DashboardPage'

export default function EventsPage() {
    const [period, setPeriod] = useState('24h'),
        [type, setType] = useState(''),
        [search, setSearch] = useState('')
    const query = useEvents({ period, type, limit: 500 })
    return (
        <>
            <PageHeader title="Журнал событий" subtitle="История изменений и тревог" />
            <div className="card filters row">
                <label>
                    Тип
                    <select
                        className="input"
                        aria-label="Тип события"
                        value={type}
                        onChange={(e) => setType(e.target.value)}
                    >
                        <option value="">Все события</option>
                        {Object.entries(EVENT_META).map(([key, value]) => (
                            <option key={key} value={key}>
                                {value.label}
                            </option>
                        ))}
                    </select>
                </label>
                <label>
                    Период
                    <select
                        className="input"
                        aria-label="Период"
                        value={period}
                        onChange={(e) => setPeriod(e.target.value)}
                    >
                        {['1h', '24h', '7d'].map((value) => (
                            <option key={value}>{value}</option>
                        ))}
                    </select>
                </label>
                <input
                    className="input"
                    aria-label="Поиск события"
                    placeholder="Сервер или сообщение"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
            </div>
            <div className="card">
                <Query q={query}>
                    {(rows) => {
                        const shown = rows.filter((row) =>
                            `${row.host} ${row.message ?? ''}`
                                .toLowerCase()
                                .includes(search.toLowerCase()),
                        )
                        return (
                            <>
                                <p className="sub">
                                    Загружено: {rows.length}. Показаны последние 500 событий
                                    выбранного типа за период; поиск выполняется среди них.
                                </p>
                                {shown.length ? (
                                    <EventsTable events={shown} />
                                ) : (
                                    <p className="nodata">Совпадений нет</p>
                                )}
                            </>
                        )
                    }}
                </Query>
            </div>
        </>
    )
}
