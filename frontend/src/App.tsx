import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import HomePage from './pages/HomePage'
import SearchPage from './pages/SearchPage'
import AgentsPage from './pages/AgentsPage'
import AlertsPage from './pages/AlertsPage'

export default function App() {
  return (
    <div className="flex h-screen bg-zinc-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto h-screen fade-in">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
        </Routes>
      </main>
    </div>
  )
}
