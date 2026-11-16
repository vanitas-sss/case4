export function Dot({ tone = 'off' }) {
    return <i className={`dot ${tone}`} />
}
export default function StatusBadge({ tone, label }) {
    return (
        <span className={`badge ${tone}`}>
            <Dot tone={tone} />
            {label}
        </span>
    )
}
