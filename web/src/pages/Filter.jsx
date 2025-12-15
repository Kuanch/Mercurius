import React, { useState } from 'react';
import { Search, Filter as FilterIcon, Play, Trash2, Archive, Tag, Loader2, Calendar } from 'lucide-react';

const Filter = () => {
    const [searchParams, setSearchParams] = useState({
        from: '',
        subject: '',
        hasWords: '',
        excludes: '',
        timeRange: '7d',
        dateMode: 'relative', // 'relative' or 'custom'
        startDate: '',
        endDate: ''
    });
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [actionLoading, setActionLoading] = useState(false);
    const [selectedAction, setSelectedAction] = useState('archive');

    const buildQuery = () => {
        const parts = [];
        if (searchParams.from) parts.push(`from:(${searchParams.from})`);
        if (searchParams.subject) parts.push(`subject:(${searchParams.subject})`);
        if (searchParams.hasWords) parts.push(`${searchParams.hasWords}`);
        if (searchParams.excludes) parts.push(`-${searchParams.excludes}`);

        if (searchParams.dateMode === 'relative' && searchParams.timeRange) {
            parts.push(`newer_than:${searchParams.timeRange}`);
        } else if (searchParams.dateMode === 'custom') {
            if (searchParams.startDate) parts.push(`after:${searchParams.startDate.replace(/-/g, '/')}`);
            if (searchParams.endDate) parts.push(`before:${searchParams.endDate.replace(/-/g, '/')}`);
        }

        return parts.join(' ');
    };

    const handleSearch = async () => {
        setLoading(true);
        const query = buildQuery();
        try {
            const response = await fetch('/sweeper/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    goal: 'Filter Search',
                    queries: [{ q: query, max_results: 20 }],
                    actions: [],
                    dry_run: true
                })
            });
            const data = await response.json();
            setResults(data);
        } catch (error) {
            console.error("Search failed", error);
        } finally {
            setLoading(false);
        }
    };

    const handleApplyAction = async () => {
        if (!confirm(`Are you sure you want to ${selectedAction} these ${results.total_hits} emails?`)) return;

        setActionLoading(true);
        const query = buildQuery();
        try {
            const response = await fetch('/sweeper/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    goal: 'Manual Filter Action',
                    queries: [{ q: query, max_results: 500 }],
                    actions: [{ type: selectedAction }],
                    dry_run: false,
                    confirm: true
                })
            });
            const data = await response.json();
            alert(`Action completed! Modified: ${data.modified || 0}`);
            setResults(null);
        } catch (error) {
            alert("Action failed");
        } finally {
            setActionLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                    <FilterIcon className="w-5 h-5 mr-2" />
                    Advanced Filter
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Has the words</label>
                        <input
                            type="text"
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="e.g. invoice, receipt"
                            value={searchParams.hasWords}
                            onChange={e => setSearchParams({ ...searchParams, hasWords: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Doesn't have</label>
                        <input
                            type="text"
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="e.g. newsletter"
                            value={searchParams.excludes}
                            onChange={e => setSearchParams({ ...searchParams, excludes: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">From</label>
                        <input
                            type="text"
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="e.g. amazon.com"
                            value={searchParams.from}
                            onChange={e => setSearchParams({ ...searchParams, from: e.target.value })}
                        />
                    </div>

                    {/* Date Selection */}
                    <div className="space-y-2">
                        <div className="flex items-center space-x-4 mb-1">
                            <label className="text-sm font-medium text-gray-700">Date Range</label>
                            <div className="flex space-x-2 text-sm">
                                <button
                                    onClick={() => setSearchParams({ ...searchParams, dateMode: 'relative' })}
                                    className={`px-2 py-0.5 rounded ${searchParams.dateMode === 'relative' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:bg-gray-100'}`}
                                >
                                    Relative
                                </button>
                                <button
                                    onClick={() => setSearchParams({ ...searchParams, dateMode: 'custom' })}
                                    className={`px-2 py-0.5 rounded ${searchParams.dateMode === 'custom' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:bg-gray-100'}`}
                                >
                                    Custom
                                </button>
                            </div>
                        </div>

                        {searchParams.dateMode === 'relative' ? (
                            <select
                                className="block w-full rounded-md border-gray-300 shadow-sm border p-2 focus:ring-blue-500 focus:border-blue-500"
                                value={searchParams.timeRange}
                                onChange={e => setSearchParams({ ...searchParams, timeRange: e.target.value })}
                            >
                                <option value="1d">1 Day</option>
                                <option value="3d">3 Days</option>
                                <option value="7d">1 Week</option>
                                <option value="14d">2 Weeks</option>
                                <option value="30d">1 Month</option>
                                <option value="1y">1 Year</option>
                            </select>
                        ) : (
                            <div className="flex space-x-2">
                                <input
                                    type="date"
                                    className="block w-full rounded-md border-gray-300 shadow-sm border p-2 text-sm"
                                    value={searchParams.startDate}
                                    onChange={e => setSearchParams({ ...searchParams, startDate: e.target.value })}
                                />
                                <span className="self-center text-gray-400">-</span>
                                <input
                                    type="date"
                                    className="block w-full rounded-md border-gray-300 shadow-sm border p-2 text-sm"
                                    value={searchParams.endDate}
                                    onChange={e => setSearchParams({ ...searchParams, endDate: e.target.value })}
                                />
                            </div>
                        )}
                    </div>
                </div>

                <div className="mt-6 flex justify-between items-center bg-gray-50 p-4 rounded-lg border border-gray-100">
                    <code className="text-sm text-gray-500 font-mono bg-white px-2 py-1 rounded border">
                        {buildQuery() || "No query"}
                    </code>
                    <button
                        onClick={handleSearch}
                        disabled={loading}
                        className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center shadow-sm disabled:opacity-70 disabled:cursor-not-allowed transition-colors"
                    >
                        {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Search className="w-4 h-4 mr-2" />}
                        {loading ? 'Searching...' : 'Search'}
                    </button>
                </div>
            </div>

            {results && (
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 animate-in fade-in slide-in-from-bottom-4 duration-300">
                    <div className="flex justify-between items-center mb-6 pb-4 border-b">
                        <div>
                            <h3 className="text-lg font-semibold text-gray-800">
                                Found {results.total_hits} matches
                            </h3>
                            <p className="text-sm text-gray-500">Review the results before applying actions.</p>
                        </div>

                        <div className="flex items-center space-x-3 bg-gray-50 p-2 rounded-lg border border-gray-200">
                            <select
                                className="rounded-md border-gray-300 border p-2 text-sm focus:ring-blue-500 focus:border-blue-500 bg-white"
                                value={selectedAction}
                                onChange={e => setSelectedAction(e.target.value)}
                            >
                                <option value="archive">Archive All</option>
                                <option value="mark_read">Mark Read</option>
                                <option value="delete">Delete</option>
                                <option value="star">Star</option>
                            </select>
                            <button
                                onClick={handleApplyAction}
                                disabled={actionLoading}
                                className="px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-md hover:from-red-600 hover:to-red-700 text-sm font-medium shadow-sm flex items-center disabled:opacity-70 transition-all"
                            >
                                {actionLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                                {actionLoading ? 'Applying...' : 'Apply Action'}
                            </button>
                        </div>
                    </div>

                    <div className="space-y-2">
                        {results.sample.map((msg) => (
                            <div key={msg.id} className="group border-b py-3 last:border-0 flex justify-between items-start hover:bg-blue-50 p-3 rounded-lg transition-colors cursor-default">
                                <div className="flex-1 min-w-0 mr-4">
                                    <div className="flex items-center space-x-2 mb-1">
                                        <span className="font-medium text-gray-900 truncate">{msg.from}</span>
                                        <span className="text-xs bg-white border border-gray-200 px-2 py-0.5 rounded text-gray-600 shadow-sm">{msg.topic}</span>
                                        <span className={`text-xs px-2 py-0.5 rounded shadow-sm ${msg.urgency === 'High' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                                            }`}>{msg.urgency}</span>
                                    </div>
                                    <p className="text-sm text-gray-800 font-medium truncate group-hover:text-blue-700">{msg.subject}</p>
                                    <p className="text-xs text-gray-500 truncate">{msg.snippet}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Filter;
