import { useQuery } from '@tanstack/react-query'
import { request } from './client'

function useApi(path, params = {}, interval = 5000, enabled = true) {
    return useQuery({
        queryKey: [path, params],
        queryFn: ({ signal }) => request(path, params, { signal }),
        refetchInterval: interval,
        enabled,
    })
}

export const useHealth = () => useApi('/health')
export const useSummary = () => useApi('/summary')
export const useHosts = (params = {}) => useApi('/hosts', params)
export const useHost = (id) => useApi(`/hosts/${id}`, {}, 5000, id != null)
export const useMetrics = (id, period = '1h') =>
    useApi(`/hosts/${id}/metrics`, { period }, 15000, id != null)
export const useContainers = (params = {}) => useApi('/containers', params)
export const useTopology = (params = {}) => useApi('/topology', params, 10000)
export const useAvailability = (period = '24h') => useApi('/availability', { period })
export const useEvents = (params = {}) => useApi('/events', params)
export const useAlerts = (params = {}) => useApi('/alerts', params)
export const useInfraLoad = (period) => useApi('/metrics/infra', { period }, 15000)
export const useSources = () => useApi('/sources')
