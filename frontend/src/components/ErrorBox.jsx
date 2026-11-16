export default function ErrorBox({ error, onRetry }) {
    return (
        <div className="errbox" role="alert">
            <div>
                <b>Не удалось загрузить данные</b>
                <div className="muted" style={{ marginTop: 2 }}>
                    {error?.message || 'Неизвестная ошибка'}
                </div>
            </div>
            {onRetry && (
                <button className="btn danger" onClick={onRetry}>
                    Повторить
                </button>
            )}
        </div>
    )
}
