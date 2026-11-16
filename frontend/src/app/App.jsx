import { Routes, Route, Navigate, useParams } from 'react-router-dom'
import Layout from './Layout'
import DashboardPage from '../features/dashboard/DashboardPage'
import HostsPage from '../features/hosts/HostsPage'
import ContainersPage from '../features/containers/ContainersPage'
import MetricsPage from '../features/metrics/MetricsPage'
import EventsPage from '../features/events/EventsPage'
import SourcesPage from '../features/sources/SourcesPage'
import TopologyPage from '../features/topology/TopologyPage'
import DocsPage from '../features/docs/DocsPage'
import AlertsPage from '../features/alerts/AlertsPage'
import AvailabilityPage from '../features/availability/AvailabilityPage'

const HostRedirect = () => <Navigate to={`/metrics?host=${useParams().id}`} replace />

export default function App() {
    return (
        <Routes>
            <Route element={<Layout />}>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/hosts" element={<HostsPage />} />
                <Route path="/hosts/:id" element={<HostRedirect />} />
                <Route path="/containers" element={<ContainersPage />} />
                <Route path="/metrics" element={<MetricsPage />} />
                <Route path="/events" element={<EventsPage />} />
                <Route path="/alerts" element={<AlertsPage />} />
                <Route path="/availability" element={<AvailabilityPage />} />
                <Route path="/topology" element={<TopologyPage />} />
                <Route path="/sources" element={<SourcesPage />} />
                <Route path="/docs" element={<DocsPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
        </Routes>
    )
}
