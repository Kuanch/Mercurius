import { Routes, Route, NavLink } from 'react-router-dom'
import { Home, List, PieChart, MessageCircle } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import Analysis from './pages/Analysis'
import Chat from './pages/Chat'

function NavItem({ to, icon: Icon, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
          isActive
            ? 'bg-blue-600 text-white'
            : 'text-gray-600 hover:bg-gray-100'
        }`
      }
    >
      <Icon size={20} />
      <span>{children}</span>
    </NavLink>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-xl font-bold text-gray-900">Mercurius</h1>
            <div className="flex gap-2">
              <NavItem to="/" icon={Home}>Dashboard</NavItem>
              <NavItem to="/transactions" icon={List}>Transactions</NavItem>
              <NavItem to="/analysis" icon={PieChart}>Analysis</NavItem>
              <NavItem to="/chat" icon={MessageCircle}>Chat</NavItem>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </main>
    </div>
  )
}
