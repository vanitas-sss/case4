export default function EmptyState({ title = 'Нет данных', hint }) {
    return (
        <div className="empty">
            <b>{title}</b>
            {hint}
        </div>
    )
}
