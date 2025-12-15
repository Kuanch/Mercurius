import React, { useState } from 'react';
import { Play, Save, Plus } from 'lucide-react';

const CreatePlanModal = ({ isOpen, onClose, onSave }) => {
    const [formData, setFormData] = useState({
        name: '',
        query: 'newer_than:7d',
        topic: 'Promotion',
        urgency: 'Low',
        action: 'archive'
    });

    if (!isOpen) return null;

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave(formData);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
                <h3 className="text-lg font-semibold mb-4">Create New Plan</h3>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Plan Name</label>
                        <input
                            type="text"
                            required
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Gmail Query</label>
                        <input
                            type="text"
                            required
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                            value={formData.query}
                            onChange={(e) => setFormData({ ...formData, query: e.target.value })}
                        />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Topic</label>
                            <select
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                                value={formData.topic}
                                onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                            >
                                {['Work', 'Finance', 'Promotion', 'Social', 'Updates', 'Forum', 'Spam'].map(t => (
                                    <option key={t} value={t}>{t}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Urgency</label>
                            <select
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                                value={formData.urgency}
                                onChange={(e) => setFormData({ ...formData, urgency: e.target.value })}
                            >
                                {['High', 'Medium', 'Low'].map(u => (
                                    <option key={u} value={u}>{u}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Action</label>
                        <select
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                            value={formData.action}
                            onChange={(e) => setFormData({ ...formData, action: e.target.value })}
                        >
                            <option value="archive">Archive</option>
                            <option value="mark_read">Mark as Read</option>
                            <option value="star">Star</option>
                            <option value="delete">Delete (Trash)</option>
                        </select>
                    </div>
                    <div className="flex justify-end space-x-3 mt-6">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                        >
                            Create Plan
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

const Planner = () => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [plans, setPlans] = useState([
        {
            id: 1,
            name: 'Archive Old Newsletters',
            query: 'category:promotions older_than:30d',
            action: 'archive',
            smart_filters: { topic: 'Promotion', urgency: 'Low' },
            apiPayload: {
                goal: 'Archive Old Newsletters',
                queries: [{ q: 'category:promotions older_than:30d', max_results: 10 }],
                actions: [{ type: 'archive' }],
                smart_filters: { topic: 'Promotion', urgency: 'Low' },
                dry_run: true,
                confirm: false
            }
        },
    ]);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleCreatePlan = (data) => {
        const newPlan = {
            id: Date.now(),
            name: data.name,
            query: data.query,
            action: data.action,
            smart_filters: { topic: data.topic, urgency: data.urgency },
            apiPayload: {
                goal: data.name,
                queries: [{ q: data.query, max_results: 10 }],
                actions: [{ type: data.action }],
                smart_filters: { topic: data.topic, urgency: data.urgency },
                dry_run: true,
                confirm: false
            }
        };
        setPlans([...plans, newPlan]);
    };

    const handleRun = async (plan) => {
        setLoading(true);
        setResult(null);
        try {
            const response = await fetch('/sweeper/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(plan.apiPayload)
            });
            const data = await response.json();
            setResult(data);
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to run plan');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-800">Cleanup Plans</h3>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                    <Plus className="w-4 h-4 mr-2" />
                    New Plan
                </button>
            </div>

            <CreatePlanModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleCreatePlan}
            />

            <div className="grid gap-4">
                {plans.map((plan) => (
                    <div key={plan.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex justify-between items-center">
                        <div>
                            <h4 className="font-medium text-gray-800">{plan.name}</h4>
                            <code className="text-sm text-gray-500 bg-gray-50 px-2 py-1 rounded mt-1 inline-block">
                                {plan.query}
                            </code>
                            <div className="mt-2 flex space-x-2">
                                <span className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded">Topic: {plan.smart_filters.topic}</span>
                                <span className="text-xs bg-purple-50 text-purple-600 px-2 py-1 rounded">Urgency: {plan.smart_filters.urgency}</span>
                            </div>
                        </div>
                        <div className="flex space-x-2">
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${plan.action === 'archive' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                                }`}>
                                {plan.action.toUpperCase()}
                            </span>
                            <button
                                onClick={() => handleRun(plan)}
                                disabled={loading}
                                className="p-2 text-gray-400 hover:text-blue-600 disabled:opacity-50"
                                title="Preview Plan"
                            >
                                <Play className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Results Preview */}
            {result && (
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 mt-6">
                    <h4 className="font-semibold text-gray-800 mb-4">Preview Results</h4>
                    <div className="grid grid-cols-3 gap-4 mb-4">
                        <div className="p-4 bg-blue-50 rounded-lg">
                            <p className="text-sm text-gray-500">Total Hits</p>
                            <p className="text-xl font-bold text-blue-600">{result.total_hits}</p>
                        </div>
                        <div className="p-4 bg-green-50 rounded-lg">
                            <p className="text-sm text-gray-500">Filtered Matches</p>
                            <p className="text-xl font-bold text-green-600">{result.filtered_hits}</p>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <p className="text-sm font-medium text-gray-500">Sample Matches:</p>
                        {result.sample.map((msg) => (
                            <div key={msg.id} className="border-b py-2 last:border-0">
                                <div className="flex justify-between">
                                    <span className="font-medium text-gray-800">{msg.from}</span>
                                    <div className="flex space-x-2">
                                        <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{msg.topic}</span>
                                        <span className={`text-xs px-2 py-0.5 rounded ${msg.urgency === 'High' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-600'
                                            }`}>{msg.urgency}</span>
                                    </div>
                                </div>
                                <p className="text-sm text-gray-600 truncate">{msg.subject}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Planner;
