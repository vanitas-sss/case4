export default function StatCards({ items }) {
    return (
        <div className="card kpis">
            {items.map(([l, v, tone, note]) => (
                <div className="kpi" key={l}>
                    <div className="label">{l}</div>
                    <div className="v">{v}</div>
                    <div className="n">
                        <i className={`dot ${tone}`} />
                        {note}
                    </div>
                </div>
            ))}
        </div>
    )
}
