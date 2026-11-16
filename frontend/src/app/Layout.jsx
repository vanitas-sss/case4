import { NavLink, Outlet } from 'react-router-dom'
import { useSummary } from '../api'
import Icon from '../components/Icon'

const NAV = [
    [
        'Мониторинг',
        [
            ['/', 'Обзор', 'overview'],
            ['/hosts', 'Серверы', 'servers', 'attn'],
            ['/containers', 'Контейнеры', 'containers'],
            ['/metrics', 'Метрики', 'metrics'],
            ['/topology', 'Топология', 'servers'],
            ['/events', 'События', 'clock', 'crit'],
        ],
    ],
    [
        'Система',
        [
            ['/sources', 'Источники', 'db'],
            ['/docs', 'Документация', 'book'],
        ],
    ],
]

export default function Layout() {
    const { data: s } = useSummary()
    const badge = (k) =>
        k === 'attn' && (s?.hosts_warning || s?.hosts_offline)
            ? { n: s.hosts_warning + s.hosts_offline, c: 'warn' }
            : k === 'crit' && s?.active_alerts
              ? { n: s.active_alerts, c: 'crit' }
              : null
    return (
        <div className="shell">
            <aside className="side">
                <div className="brand">
                    <div className="brand-logo">
                        <svg width="24" height="14" viewBox="0 0 24 14">
                            <path
                                d="M6 0l6 11.5L6 8 0 11.5 6 0zM18 0l6 11.5L18 8l-6 3.5L18 0z"
                                fill="#0B0F14"
                            />
                        </svg>
                    </div>
                    <div>
                        <b>MOTY</b>
                        <small>INFRASTRUCTURE CONSOLE</small>
                    </div>
                </div>
                {NAV.map(([group, items]) => (
                    <div key={group}>
                        <div className="group">{group}</div>
                        {items.map(([to, label, icon, bk]) => {
                            const b = badge(bk)
                            return (
                                <NavLink
                                    key={to}
                                    to={to}
                                    end={to === '/'}
                                    className={({ isActive }) => `nav${isActive ? ' active' : ''}`}
                                >
                                    <Icon name={icon} /> {label}
                                    {b && (
                                        <span className="count" style={{ color: `var(--${b.c})` }}>
                                            <i className={`dot ${b.c}`} />
                                            {b.n}
                                        </span>
                                    )}
                                </NavLink>
                            )
                        })}
                    </div>
                ))}
                <div className="user">
                    <div className="avatar">A</div>
                    <div>
                        <b style={{ fontWeight: 600 }}>Наблюдатель</b>
                        <small>Локальный стенд</small>
                    </div>
                </div>
            </aside>
            <main className="main">
                <Outlet />
            </main>
        </div>
    )
}
