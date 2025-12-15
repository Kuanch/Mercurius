import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { LayoutDashboard, ListTodo, Settings, Filter } from 'lucide-react';

const Layout = () => {
    const location = useLocation();

    const navItems = [
        { path: '/', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/filter', label: 'Filter', icon: Filter },
        { path: '/planner', label: 'Planner', icon: ListTodo },
        { path: '/settings', label: 'Settings', icon: Settings },
    ];

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <div className="w-64 bg-white shadow-md">
                <div className="p-6">
                    <h1 className="text-2xl font-bold text-blue-600">Mercurius</h1>
                    <p className="text-sm text-gray-500">Gmail Sandbox</p>
                </div>
                <nav className="mt-6">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center px-6 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 ${isActive ? 'bg-blue-50 text-blue-600 border-r-4 border-blue-600' : ''
                                    }`}
                            >
                                <Icon className="w-5 h-5 mr-3" />
                                <span className="font-medium">{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-auto">
                <header className="bg-white shadow-sm">
                    <div className="px-8 py-4">
                        <h2 className="text-xl font-semibold text-gray-800">
                            {navItems.find((i) => i.path === location.pathname)?.label || 'Mercurius'}
                        </h2>
                    </div>
                </header>
                <main className="p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default Layout;
