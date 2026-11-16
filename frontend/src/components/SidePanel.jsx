import { useEffect } from 'react'
import Icon from './Icon'
export default function SidePanel({ onClose, children, footer }) {
    useEffect(() => {
        const h = (e) => e.key === 'Escape' && onClose()
        window.addEventListener('keydown', h)
        return () => window.removeEventListener('keydown', h)
    }, [onClose])
    return (
        <>
            <div className="overlay" onClick={onClose} />
            <aside className="panel" role="dialog">
                <button
                    className="icon-btn"
                    onClick={onClose}
                    aria-label="Закрыть"
                    style={{ position: 'absolute', right: 32, top: 32 }}
                >
                    <Icon name="close" />
                </button>
                <div className="panel-body">{children}</div>
                {footer && <div className="panel-foot">{footer}</div>}
            </aside>
        </>
    )
}
