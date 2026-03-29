"use client";

import { useAuth } from '@/hooks/useAuth';
import { fetchTickets, transitionTicket } from "@/app/actions";
import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle, ShieldCheck } from "lucide-react";

export default function OwnerPortal() {
  const { user, loading } = useAuth();
  const [tickets, setTickets] = useState<any[]>([]);

  useEffect(() => {
    loadTickets();
  }, []);

  const loadTickets = async () => {
    try {
      setTickets(await fetchTickets());
    } catch (e) {
      console.error(e);
    }
  };

  const handleApprove = async (ticketId: string) => {
    await transitionTicket(ticketId, { action: "APPROVE" });
    await loadTickets();
  };

  const handlePay = async (ticketId: string) => {
    await transitionTicket(ticketId, { action: "DISPATCH_PAYMENT" });
    await loadTickets();
  };

  if (loading) return null;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Owner Dashboard</h1>
        <p className="text-gray-500 mt-2">Approve pending estimates and manage final payouts.</p>
      </div>

      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Decision Dashboard</h2>
        {tickets.filter(j => j.status === 'PENDING_APPROVAL').length === 0 && <p className="text-gray-400">No decisions pending.</p>}
        {tickets.filter(j => j.status === 'PENDING_APPROVAL').map(job => (
          <div key={job.ticketId} className={`rounded-xl shadow-sm border p-6 ${job.auditFlag === 'HIGH_RISK_REASONING_REQUIRED' ? 'bg-red-50 border-red-200' : 'bg-white border-gray-200'}`}>
            <div className="flex justify-between items-start mb-4">
              <h3 className="font-bold text-lg">{job.ticketId}: {job.managerNote}</h3>
              {job.auditFlag === 'HIGH_RISK_REASONING_REQUIRED' ? (
                <span className="flex items-center gap-1 text-red-600 bg-red-100 px-3 py-1 rounded-full text-sm font-bold">
                  <AlertTriangle className="w-4 h-4" /> HIGH RISK (Manual Override)
                </span>
              ) : (
                <span className="flex items-center gap-1 text-green-600 bg-green-100 px-3 py-1 rounded-full text-sm font-bold">
                  <ShieldCheck className="w-4 h-4" /> AI Audited (Cost Aligned)
                </span>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500 uppercase tracking-wider font-bold">AI Estimate</p>
                <p className="text-3xl font-light">${job.aiEstimatedCost}</p>
                <p className="text-xs text-gray-400 mt-1">{job.aiDiagnosis}</p>
              </div>
              <div className="p-4 bg-blue-50 border border-blue-100 rounded-lg">
                <p className="text-sm text-blue-600 uppercase tracking-wider font-bold">Vendor Bid</p>
                <p className="text-3xl text-blue-900 font-bold">${job.vendorBid || "Pending..."}</p>
                <p className="text-xs text-blue-500 mt-1">Vendor ID: Pending Mapping</p>
              </div>
            </div>

            <div className="flex justify-end gap-3 border-t pt-4">
              <button className="px-4 py-2 border rounded font-medium hover:bg-gray-50">Reject</button>
              <button 
                onClick={() => handleApprove(job.ticketId)}
                className="bg-blue-600 text-white px-6 py-2 rounded font-bold shadow hover:bg-blue-700"
              >
                Approve & Dispatch
              </button>
            </div>
          </div>
        ))}

        <h2 className="text-2xl font-bold pt-8">Awaiting Payment</h2>
        {tickets.filter(j => j.status === 'AWAITING_PAYMENT').length === 0 && <p className="text-gray-400">No invoices pending.</p>}
        {tickets.filter(j => j.status === 'AWAITING_PAYMENT').map(job => (
          <div key={job.ticketId} className="bg-green-50 rounded-xl shadow-sm border border-green-200 p-6 flex flex-col md:flex-row justify-between items-center">
            <div>
              <p className="font-bold text-lg text-green-900 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" /> {job.ticketId} - Fix Validated
              </p>
              <p className="text-sm text-green-700 mt-1">Manager visually confirmed completion.</p>
            </div>
            <button 
              onClick={() => handlePay(job.ticketId)}
              className="bg-green-600 text-white px-6 py-3 rounded-lg font-bold shadow hover:bg-green-700"
            >
              Dispatch Payment
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
