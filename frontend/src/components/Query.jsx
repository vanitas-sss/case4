import Loader from './Loader'
import ErrorBox from './ErrorBox'
import EmptyState from './EmptyState'
export default function Query({
    q,
    rows,
    empty = (d) => Array.isArray(d) && d.length === 0,
    emptyTitle,
    emptyHint,
    children,
}) {
    if (q.isPending) return <Loader rows={rows} />
    if (q.isError) return <ErrorBox error={q.error} onRetry={() => q.refetch()} />
    if (empty(q.data)) return <EmptyState title={emptyTitle} hint={emptyHint} />
    return children(q.data)
}
