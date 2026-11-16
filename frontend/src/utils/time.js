export function ago(sec) {
    if (sec == null) return '—'
    if (sec < 60) return `${Math.round(sec)} с назад`
    if (sec < 3600) return `${Math.floor(sec / 60)} мин назад`
    if (sec < 86400) return `${Math.floor(sec / 3600)} ч назад`
    return `${Math.floor(sec / 86400)} д назад`
}
export const agoIso = (iso) => (iso ? ago((Date.now() - new Date(iso).getTime()) / 1000) : '—')
export const hms = (iso) => (iso ? new Date(iso).toLocaleTimeString('ru-RU') : '—')
export const hm = (iso) =>
    iso ? new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) : '—'
export function duration(fromIso, toIso) {
    const s = Math.max(0, ((toIso ? new Date(toIso) : Date.now()) - new Date(fromIso)) / 1000)
    if (s < 60) return `${Math.round(s)} с`
    if (s < 3600) return `${Math.floor(s / 60)} мин`
    if (s < 86400) return `${Math.floor(s / 3600)} ч ${Math.floor((s % 3600) / 60)} мин`
    return `${Math.floor(s / 86400)} д ${Math.floor((s % 86400) / 3600)} ч`
}
