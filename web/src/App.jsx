import { Routes, Route, NavLink } from 'react-router-dom'
import { LayoutDashboard, Receipt, PieChart, MessageCircle, Settings } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import Analysis from './pages/Analysis'
import Chat from './pages/Chat'

function NavItem({ to, icon: Icon, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors group ${
          isActive
            ? 'bg-primary/10 text-primary'
            : 'text-gray-400 hover:bg-surface-dark hover:text-gray-200'
        }`
      }
    >
      <Icon size={20} className="shrink-0" />
      <span className="text-sm font-medium">{children}</span>
    </NavLink>
  )
}

export default function App() {
  return (
    <div className="bg-background-dark text-gray-100 h-screen flex overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-surface-dark border-r border-border-dark flex-col h-full hidden md:flex">
        <div className="p-6 flex flex-col h-full justify-between">
          <div className="flex flex-col gap-8">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">M</span>
              </div>
              <span className="text-xl font-bold text-white">Mercurius</span>
            </div>

            {/* Navigation */}
            <nav className="flex flex-col gap-2">
              <NavItem to="/" icon={LayoutDashboard}>Dashboard</NavItem>
              <NavItem to="/transactions" icon={Receipt}>Transactions</NavItem>
              <NavItem to="/analysis" icon={PieChart}>Analysis</NavItem>
              <NavItem to="/chat" icon={MessageCircle}>AI Chat</NavItem>
            </nav>
          </div>

          {/* Bottom section */}
          <nav className="flex flex-col gap-2">
            <NavItem to="/settings" icon={Settings}>Settings</NavItem>
          </nav>
        </div>
      </aside>

      {/* Mobile header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-50 bg-surface-dark border-b border-border-dark px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xs">M</span>
            </div>
            <span className="text-lg font-bold text-white">Mercurius</span>
          </div>
        </div>
        {/* Mobile nav */}
        <nav className="flex gap-1 mt-3 overflow-x-auto pb-1">
          <NavLink to="/" className={({ isActive }) =>
            `px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap ${
              isActive ? 'bg-primary text-white' : 'bg-surface-dark text-gray-400'
            }`
          }>Dashboard</NavLink>
          <NavLink to="/transactions" className={({ isActive }) =>
            `px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap ${
              isActive ? 'bg-primary text-white' : 'bg-surface-dark text-gray-400'
            }`
          }>Transactions</NavLink>
          <NavLink to="/analysis" className={({ isActive }) =>
            `px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap ${
              isActive ? 'bg-primary text-white' : 'bg-surface-dark text-gray-400'
            }`
          }>Analysis</NavLink>
          <NavLink to="/chat" className={({ isActive }) =>
            `px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap ${
              isActive ? 'bg-primary text-white' : 'bg-surface-dark text-gray-400'
            }`
          }>Chat</NavLink>
        </nav>
      </div>

      {/* Main content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-background-dark">
        <div className="flex-1 overflow-y-auto p-4 md:p-8 lg:px-12 pt-28 md:pt-8">
          <div className="max-w-5xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/analysis" element={<Analysis />} />
              <Route path="/chat" element={<Chat />} />
            </Routes>
          </div>
        </div>
      </main>
    </div>
  )
}
