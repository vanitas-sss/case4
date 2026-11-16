import { useId } from 'react'
import {
    Area,
    AreaChart,
    CartesianGrid,
    Legend,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts'
import { hm } from '../utils/time'
import { fmt1 } from '../utils/format'

const DEFAULT_SERIES = [
    { key: 'cpu_percent', name: 'CPU' },
    { key: 'memory_percent', name: 'RAM' },
]
const COLORS = ['#ECE8DC', '#E8B04A', '#88BDA5']

export default function MetricsChart({ data, height = 260, series = DEFAULT_SERIES }) {
    const id = useId().replaceAll(':', '')
    if (!data?.length) return <p className="nodata">Измерений нет</p>
    return (
        <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={data} margin={{ top: 12, right: 20, left: 0, bottom: 10 }}>
                <defs>
                    <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0" stopColor={COLORS[0]} stopOpacity={0.12} />
                        <stop offset="1" stopColor={COLORS[0]} stopOpacity={0} />
                    </linearGradient>
                </defs>
                <CartesianGrid stroke="#353530" vertical={false} />
                <XAxis dataKey="timestamp" tickFormatter={hm} minTickGap={40} stroke="#9A968A" />
                <YAxis domain={[0, 100]} unit="%" width={50} stroke="#9A968A" />
                <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleString('ru-RU')}
                    formatter={(value, name) => [fmt1(value), name]}
                    contentStyle={{ background: '#20201e', borderColor: '#555' }}
                />
                <Legend />
                {series.map((line, index) => (
                    <Area
                        key={line.key}
                        type="linear"
                        dataKey={line.key}
                        name={line.name}
                        stroke={COLORS[index % COLORS.length]}
                        fill={index === 0 ? `url(#${id})` : 'none'}
                        connectNulls={false}
                        isAnimationActive={false}
                        dot={data.length === 1}
                    />
                ))}
            </AreaChart>
        </ResponsiveContainer>
    )
}
