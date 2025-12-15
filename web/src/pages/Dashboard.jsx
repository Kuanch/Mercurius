import React from 'react';
import { Mail, CheckCircle, Trash2, Archive } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, color }) => (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex items-center">
        <div className={`p-3 rounded-full ${color} bg-opacity-10 mr-4`}>
            <Icon className={`w-6 h-6 ${color.replace('bg-', 'text-')}`} />
        </div>
        <div>
            <p className="text-sm text-gray-500 font-medium">{title}</p>
            <p className="text-2xl font-bold text-gray-800">{value}</p>
        </div>
    </div>
);

const Dashboard = () => {
    // Mock data
    const stats = [
        { title: 'Emails Scanned', value: '1,240', icon: Mail, color: 'bg-blue-500' },
        { title: 'Newsletters Found', value: '85', icon: CheckCircle, color: 'bg-green-500' },
        { title: 'Archived', value: '42', icon: Archive, color: 'bg-yellow-500' },
        { title: 'Deleted', value: '12', icon: Trash2, color: 'bg-red-500' },
    ];

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat) => (
                    <StatCard key={stat.title} {...stat} />
                ))}
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h3>
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="flex items-center justify-between py-3 border-b last:border-0">
                            <div className="flex items-center">
                                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                                <div>
                                    <p className="font-medium text-gray-800">Archived "Weekly Newsletter"</p>
                                    <p className="text-xs text-gray-500">2 hours ago</p>
                                </div>
                            </div>
                            <span className="text-sm text-gray-500">Auto-Plan #1</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
