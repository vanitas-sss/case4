import { Component } from 'react'

export default class ErrorBoundary extends Component {
    state = { failed: false }

    static getDerivedStateFromError() {
        return { failed: true }
    }

    render() {
        if (this.state.failed)
            return (
                <main className="card" role="alert">
                    <h1>Не удалось отобразить страницу</h1>
                    <p>
                        Обновите страницу. Если ошибка повторяется, передайте разработчику адрес
                        страницы и сообщение из консоли браузера.
                    </p>
                    <button className="btn" onClick={() => window.location.reload()}>
                        Обновить
                    </button>
                </main>
            )
        return this.props.children
    }
}
