"use client";
import { logoutUser } from '@/services/auth';
import { useEffect, useState } from "react";
import { fetchTickets } from "../../actions";
import { Copy, Terminal, Activity, ArrowRightLeft } from "lucide-react";

export default function AdminDashboard() {
  const [tickets, setTickets] = useState<any[]>([]);

  useEffect(() => {
    async function load() {
      const res = await fetchTickets();
      if (res.tickets) setTickets(res.tickets);
    }
    load();
  }, []);

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 bg-gray-50 min-h-screen">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight flex items-center gap-3">
            <Terminal className="w-8 h-8 text-indigo-600" />
            Super User Dashboard
          </h1>
          <p className="mt-2 text-sm text-gray-500">Live inspection of all ticket states & JSON payloads</p>
        </div>
        <div className="flex gap-4 items-center">
          <button onClick={logoutUser} className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold px-4 py-2 rounded-lg shadow-sm">Logout</button>
          <a href="http://localhost:8000/metrics" target="_blank" className="flex items-center gap-2 bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors">
            <Activity className="w-4 h-4" />
            Prometheus Metrics
          </a>
          <a href="http://localhost:3000/api/langfuse" target="_blank" className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors">
            <ArrowRightLeft className="w-4 h-4" />
            Langfuse Traces
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {tickets.map((t) => (
          <div key={t.ticketId} className="bg-slate-900 rounded-xl shadow-lg overflow-hidden border border-slate-700">
            <div className="px-6 py-4 border-b border-slate-700 flex justify-between items-center bg-slate-800">
              <h2 className="text-lg font-mono font-medium text-slate-200">
                Ticket ID: {t.ticketId}
              </h2>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-slate-700 text-indigo-300 border border-slate-600">
                STATE: {t.status}
              </span>
            </div>
            <div className="p-6">
              <div className="relative">
                <button 
                  onClick={() => navigator.clipboard.writeText(JSON.stringify(t, null, 2))}
                  className="absolute top-2 right-2 p-2 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-md transition-colors"
                  title="Copy JSON"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <pre className="bg-black/50 p-4 rounded-lg overflow-x-auto text-sm text-green-400 font-mono border border-slate-800">
                  <code>{JSON.stringify(t, null, 2)}</code>
                </pre>
              </div>
            </div>
          </div>
        ))}
        {tickets.length === 0 && (
          <div className="text-center py-12 bg-white rounded-xl border border-gray-200 shadow-sm">
            <Terminal className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-semibold text-gray-900">No tickets found</h3>
            <p className="mt-1 text-sm text-gray-500">System state is empty. Create a ticket in the Manager portal.</p>
          </div>
        )}
      </div>
    </div>
  );
}
