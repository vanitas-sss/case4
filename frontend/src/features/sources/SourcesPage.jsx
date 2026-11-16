import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useSources } from '../../api'
import { importReports } from '../../api/client'
import PageHeader from '../../components/PageHeader'
import Query from '../../components/Query'
import { agoIso } from '../../utils/time'

export default function SourcesPage() {
    const query = useSources(),
        cache = useQueryClient()
    const [file, setFile] = useState(null),
        [busy, setBusy] = useState(false),
        [error, setError] = useState(''),
        [result, setResult] = useState(null)
    async function submit(event) {
        event.preventDefault()
        setError('')
        setResult(null)
        if (!file) {
            setError('Выберите JSON-файл')
            return
        }
        if (file.size > 2 * 1024 * 1024) {
            setError('Файл превышает 2 МиБ')
            return
        }
        setBusy(true)
        try {
            setResult(await importReports(file))
            await cache.invalidateQueries()
        } catch (cause) {
            setError(cause.message)
        } finally {
            setBusy(false)
        }
    }
    return (
        <>
            <PageHeader title="Источники данных" subtitle="Подключение источников и импорт JSON" />
            <div className="stack">
                <div className="card">
                    <h2>Известные источники</h2>
                    <p className="sub">
                        Источник появляется после первого принятого отчёта. Список включает
                        источники, от которых давно нет данных.
                    </p>
                    <Query q={query}>
                        {(rows) => (
                            <div className="table-scroll">
                                <table className="tbl">
                                    <thead>
                                        <tr>
                                            <th>Source ID</th>
                                            <th>Серверов</th>
                                            <th>В сети</th>
                                            <th>Последний сигнал</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {rows.map((row) => (
                                            <tr key={row.source_id}>
                                                <td>{row.source_id}</td>
                                                <td>{row.hosts_total}</td>
                                                <td>{row.hosts_online}</td>
                                                <td>{agoIso(row.last_seen)}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </Query>
                </div>
                <div className="card">
                    <h2>Импорт JSON</h2>
                    <p className="sub">
                        Массив отчётов по контракту ingest, UTF-8, до 2 МиБ. Ошибки одного отчёта не
                        отменяют остальные.
                    </p>
                    <form className="row filters" onSubmit={submit}>
                        <input
                            aria-label="JSON-файл"
                            type="file"
                            accept=".json,application/json"
                            onChange={(e) => {
                                setFile(e.target.files[0] ?? null)
                                setResult(null)
                                setError('')
                            }}
                        />
                        <button className="btn primary" disabled={busy || !file}>
                            {busy ? 'Загрузка…' : 'Загрузить отчёты'}
                        </button>
                    </form>
                    {error && <p role="alert">{error}</p>}
                    {result && (
                        <div role="status">
                            <p>
                                Принято: {result.accepted}. Отклонено: {result.rejected}.
                            </p>
                            {result.errors.map((item) => (
                                <div key={item.index}>
                                    <b>Отчёт №{item.index + 1}</b>
                                    <ul>
                                        {item.errors.map((issue, index) => (
                                            <li key={index}>
                                                {issue.loc.join('.')}: {issue.msg}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                            <p className="sub">
                                Повторные и устаревшие отчёты могут быть приняты без добавления
                                новой метрики.
                            </p>
                        </div>
                    )}
                </div>
                <div className="card">
                    <h2>Отправка данных</h2>
                    <p>
                        Агент отправляет массив JSON на <code>POST /api/v1/ingest</code>. В
                        Docker-сети адрес для генератора:{' '}
                        <code>http://backend:8000/api/v1/ingest</code>. С компьютера:{' '}
                        <code>http://localhost:8080/api/v1/ingest</code>.
                    </p>
                    <p>
                        Генератор из профиля demo отправляет синтетические измерения. Реальный
                        сборщик метрик разрабатывается отдельно и в этот проект не входит.
                    </p>
                    <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
                        Swagger при локальном Docker-запуске
                    </a>
                </div>
            </div>
        </>
    )
}
