"use client";

import { useAuth } from '@/hooks/useAuth';
import { logoutUser } from '@/services/auth';
import { useEffect, useState } from "react";
import { Hammer, CircleDollarSign } from 'lucide-react';
import { fetchTickets, transitionTicket } from "@/app/actions";

export default function VendorPortal() {
  const { user, loading } = useAuth();
  const [tickets, setTickets] = useState<any[]>([]);
  const [bidAmount, setBidAmount] = useState<string>("");

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

  const handleBid = async (ticketId: string) => {
    await transitionTicket(ticketId, { vendor_bid: parseFloat(bidAmount) });
    setBidAmount("");
    await loadTickets();
  };

  const handleFix = async (ticketId: string) => {
    await transitionTicket(ticketId, { action: "SUBMIT_FIX" });
    await loadTickets();
  };

  if (loading) return null;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Job Marketplace</h1>
          <p className="text-gray-500 mt-2">Welcome Vendor ({user?.username}). Bid on open jobs and manage your repairs.</p>
          {user?.category && <p className="text-blue-600 font-medium">Your Category: {user?.category}</p>}
        </div>
        <button onClick={logoutUser} className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold px-4 py-2 rounded-lg shadow-sm">Logout</button>
      </div>

      <div className="space-y-6">
        <h2 className="text-xl font-semibold border-b pb-2">Open for Bidding</h2>
        {tickets.filter(j => j.status === 'AWAITING_BIDS' && (!user?.category || j.category === user?.category)).length === 0 && <p className="text-gray-400 text-sm">No open jobs...</p>}
        {tickets.filter(j => j.status === 'AWAITING_BIDS' && (!user?.category || j.category === user?.category)).map(job => (
          <div key={job.ticketId} className="bg-white rounded-xl shadow-sm border p-6 flex flex-col md:flex-row justify-between gap-4">
            <div>
              <p className="font-bold text-lg">{job.ticketId}</p>
              <p className="text-sm text-gray-600 mt-2">{job.managerNote || "No notes"}</p>
              <p className="text-xs font-semibold text-gray-500 mt-1 uppercase">Category: {job.category || 'General'}</p>
              {job.aiDiagnosis && (
                 <p className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded inline-block mt-2">
                   AI Identified: {job.aiDiagnosis}
                 </p>
              )}
            </div>
            <div className="flex gap-2 items-center">
              <input 
                type="number" 
                placeholder="$ USD amount" 
                className="border p-2 rounded"
                value={bidAmount}
                onChange={(e) => setBidAmount(e.target.value)}
              />
              <button 
                onClick={() => handleBid(job.ticketId)}
                className="bg-blue-600 text-white px-4 py-2 font-bold rounded hover:bg-blue-700 flex items-center gap-2"
              >
                <CircleDollarSign className="w-4 h-4" /> Submit Bid
              </button>
            </div>
          </div>
        ))}

        <h2 className="text-xl font-semibold border-b pb-2 pt-8">Assigned To You (In Progress)</h2>
        {tickets.filter(j => j.status === 'IN_PROGRESS' && (j.targetVendorId === user?.username || j.targetVendorId === user?.username)).length === 0 && <p className="text-gray-400 text-sm">No assigned jobs...</p>}
        {tickets.filter(j => j.status === 'IN_PROGRESS' && (j.targetVendorId === user?.username || j.targetVendorId === user?.username)).map(job => (
          <div key={job.ticketId} className="bg-orange-50 rounded-xl border border-orange-200 p-6 flex flex-col md:flex-row justify-between items-center">
             <div>
                <p className="font-bold text-lg">{job.ticketId}</p>
                <p className="text-sm mt-1">{job.managerNote}</p>
                <p className="text-xs font-semibold text-gray-500 mt-1 uppercase">Category: {job.category || 'General'}</p>
             </div>
             <button 
                onClick={() => handleFix(job.ticketId)}
                className="bg-orange-500 text-white px-6 py-2 rounded font-bold hover:bg-orange-600 flex items-center gap-2"
             >
                <Hammer className="w-4 h-4" /> Upload Fix & Invoice
             </button>
          </div>
        ))}
      </div>
    </div>
  );
}
