export default function Loader({ rows = 4 }) {
    return (
        <div aria-busy="true" aria-label="Загрузка">
            {Array.from({ length: rows }, (_, i) => (
                <div key={i} className="sk" style={{ opacity: 1 - i * 0.15 }} />
            ))}
        </div>
    )
}
