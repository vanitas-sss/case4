import StatCards from '../../components/StatCards'

export default function SummaryCards({ s }) {
    return (
        <StatCards
            items={[
                ['Серверы', s.hosts_total, 'off', `В сети: ${s.hosts_online}`],
                [
                    'Нет связи',
                    s.hosts_offline,
                    s.hosts_offline ? 'crit' : 'ok',
                    `С задержкой: ${s.hosts_warning}`,
                ],
                ['Контейнеры', s.containers_total, 'off', `Работают: ${s.containers_running}`],
                [
                    'Активные тревоги',
                    s.active_alerts,
                    s.active_alerts ? 'warn' : 'ok',
                    'По правилам backend',
                ],
            ]}
        />
    )
}
