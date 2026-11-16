import { useEffect, useRef } from 'react'
import Icon from './Icon'

export default function SidePanel({ onClose, children, footer }) {
    const panel = useRef(null)
    const close = useRef(onClose)
    useEffect(() => {
        close.current = onClose
    }, [onClose])
    useEffect(() => {
        const previous = document.activeElement
        const overflow = document.body.style.overflow
        document.body.style.overflow = 'hidden'
        panel.current.querySelector('button')?.focus()
        function handleKey(event) {
            if (event.key === 'Escape') close.current()
            if (event.key !== 'Tab') return
            const focusable = [
                ...panel.current.querySelectorAll('button, a[href], input, select, [tabindex="0"]'),
            ].filter((element) => !element.disabled)
            const first = focusable[0],
                last = focusable.at(-1)
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault()
                last?.focus()
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault()
                first?.focus()
            }
        }
        window.addEventListener('keydown', handleKey)
        return () => {
            document.body.style.overflow = overflow
            window.removeEventListener('keydown', handleKey)
            previous?.focus()
        }
    }, [])
    return (
        <>
            <div className="overlay" onClick={onClose} />
            <aside
                ref={panel}
                className="panel"
                role="dialog"
                aria-modal="true"
                aria-label="Карточка объекта"
            >
                <button
                    className="icon-btn"
                    onClick={onClose}
                    aria-label="Закрыть"
                    style={{ position: 'absolute', right: 24, top: 24 }}
                >
                    <Icon name="close" />
                </button>
                <div className="panel-body">{children}</div>
                {footer && <div className="panel-foot">{footer}</div>}
            </aside>
        </>
    )
}
