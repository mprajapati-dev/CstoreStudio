"use client";

import { useAuth } from '@/hooks/useAuth';
import { logoutUser } from '@/services/auth';
import { fetchTickets, transitionTicket, fetchVendorsByCategory } from "@/app/actions";
import { useEffect, useState, useMemo } from "react";
import { AlertTriangle, CheckCircle, ShieldCheck, Info, Edit, Plus } from "lucide-react";
import UploadMedia from "@/components/UploadMedia";

export default function OwnerPortal() {
  const { user, loading } = useAuth();
  const [tickets, setTickets] = useState<any[]>([]);
  const [selectedStore, setSelectedStore] = useState<string>("ALL");
  const [vendors, setVendors] = useState<any[]>([]);

  // Ticket Form States
  const [editingTicketId, setEditingTicketId] = useState<string | null>(null);
  const [category, setCategory] = useState("MAINTENANCE");
  const [subCategory, setSubCategory] = useState("PLUMBING");
  const [dispatchType, setDispatchType] = useState("BROADCAST");
  const [targetVendorId, setTargetVendorId] = useState("");
  const [note, setNote] = useState("");
  const [mediaUrl, setMediaUrl] = useState("");
  const [ticketStoreId, setTicketStoreId] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Vendor Assignment State for Approvals
  const [selectedVendorForApproval, setSelectedVendorForApproval] = useState<Record<string, string>>({});

  useEffect(() => {
    if (user?.store_ids) {
      loadTickets();
      if (user.store_ids.length > 0) setTicketStoreId(user.store_ids[0]);
    }
  }, [user]);

  useEffect(() => {
    loadVendors();
  }, [category]);

  const loadVendors = async () => {
    try {
      const v = await fetchVendorsByCategory(category);
      setVendors(v);
    } catch (e) {
      console.error(e);
    }
  };

  const loadTickets = async () => {
    try {
      const allTickets = await fetchTickets();
      if (user?.store_ids) {
        setTickets(allTickets.filter((t: any) => user?.store_ids?.includes(t.storeId)));
      } else {
        setTickets(allTickets);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const filteredTickets = useMemo(() => {
    if (selectedStore === "ALL") return tickets;
    return tickets.filter(t => t.storeId === selectedStore);
  }, [tickets, selectedStore]);

  const handleApprove = async (ticketId: string) => {
    const vId = selectedVendorForApproval[ticketId] || "";
    // Pass the selected vendor if triage to audit manual flow
    await transitionTicket(ticketId, { action: "DISPATCH", targetVendorId: vId });
    await loadTickets();
  };

  const handlePay = async (ticketId: string) => {
    await transitionTicket(ticketId, { action: "DISPATCH_PAYMENT" });
    await loadTickets();
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setSubmitting(true);
    let tId = editingTicketId;
    if (!tId) {
      tId = "T-" + Math.random().toString(36).substring(2, 8).toUpperCase();
    }
    
    await transitionTicket(tId, {
      category,
      subCategory,
      targetVendorId,
      note,
      mediaUrl,
      store_id: ticketStoreId || "DEFAULT",
      action: dispatchType === "SPECIFIC" || targetVendorId ? "DISPATCH" : "BROADCAST"
    });
    
    // Reset Form
    setEditingTicketId(null);
    setNote("");
    setMediaUrl("");
    setTargetVendorId("");
    setSubmitting(false);
    await loadTickets();
  };

  const loadTicketForEdit = (job: any) => {
    setEditingTicketId(job.ticketId);
    setCategory(job.category || "MAINTENANCE");
    setSubCategory(job.subCategory || "");
    setNote(job.managerNote || "");
    setMediaUrl(job.mediaUrl || "");
    setTargetVendorId(job.targetVendorId || "");
    setTicketStoreId(job.storeId || (user?.store_ids?.[0] || ""));
    setDispatchType(job.targetVendorId ? "SPECIFIC" : "BROADCAST");
    window.scrollTo(0, 0); // scroll to form
  };

  if (loading) return null;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex justify-between items-center border-b pb-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Owner Dashboard</h1>
          <p className="text-gray-500 mt-2">Manage tickets across all your stores.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={logoutUser} className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold px-4 py-2 rounded-lg shadow-sm">Logout</button>
          <label className="text-sm font-semibold text-gray-700">Filter by Store:</label>
          <select 
            className="border p-2 rounded-lg text-gray-700 shadow-sm focus:ring-2 focus:ring-blue-500"
            value={selectedStore}
            onChange={(e) => setSelectedStore(e.target.value)}
          >
            <option value="ALL">All Stores</option>
            {user?.store_ids?.map((storeId: string) => (
              <option key={storeId} value={storeId}>Store #{storeId}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Ticket Creation / Edit Section */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-2xl font-bold flex items-center gap-2 mb-4">
          {editingTicketId ? <Edit className="w-6 h-6 text-blue-600" /> : <Plus className="w-6 h-6 text-green-600" />}
          {editingTicketId ? `Edit Ticket: ${editingTicketId}` : "Create New Ticket"}
        </h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Store / Location</label>
            <select className="w-full border rounded p-2" value={ticketStoreId} onChange={e => setTicketStoreId(e.target.value)}>
              {user?.store_ids?.map((sId: string) => (
                <option key={sId} value={sId}>{sId}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <select className="w-full border rounded p-2" value={category} onChange={e => setCategory(e.target.value)}>
              <option value="MAINTENANCE">Maintenance</option>
              <option value="HVAC">HVAC</option>
              <option value="PLUMBING">Plumbing</option>
              <option value="ELECTRICAL">Electrical</option>
            </select>
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea required className="w-full border rounded p-2 h-24" placeholder="What is the issue?" value={note} onChange={e => setNote(e.target.value)}></textarea>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Dispatch Type</label>
            <select className="w-full border rounded p-2" value={dispatchType} onChange={e => setDispatchType(e.target.value)}>
              <option value="BROADCAST">Broadcast (Find Auto / Triage)</option>
              <option value="SPECIFIC">Assign Specific Vendor</option>
            </select>
          </div>
          {dispatchType === "SPECIFIC" && (
            <div>
              <label className="block text-sm font-medium mb-1">Available Vendors</label>
              <select className="w-full border rounded p-2" value={targetVendorId} onChange={e => setTargetVendorId(e.target.value)} required>
                <option value="">-- Select Vendor --</option>
                {vendors?.map(v => (
                  <option key={v.id} value={v.id}>{v.name} ({v.rating} ⭐)</option>
                ))}
              </select>
            </div>
          )}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-1">Upload Problem Image</label>
            {mediaUrl && (
              <div className="mb-2"><img src={mediaUrl} alt="Uploaded" className="h-24 w-auto rounded border shadow-sm" /></div>
            )}
            <UploadMedia onUploadComplete={setMediaUrl} />
          </div>
          <div className="md:col-span-2 flex gap-4 mt-2">
            <button type="submit" disabled={submitting} className="bg-blue-600 text-white px-6 py-2 rounded-lg shadow font-medium hover:bg-blue-700 disabled:opacity-50">
              {submitting ? "Saving..." : (editingTicketId ? "Update Ticket" : "Create Ticket")}
            </button>
            {editingTicketId && (
              <button type="button" onClick={() => { setEditingTicketId(null); setNote(""); setMediaUrl(""); }} className="text-gray-600 px-4 py-2 hover:bg-gray-100 rounded-lg">
                Cancel Edit
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Decision Dashboard */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold border-b pb-2">Decisions Pending (Triage Output)</h2>
        {filteredTickets.filter(j => j.status === 'PENDING_APPROVAL').length === 0 && <p className="text-gray-400 italic">No decisions pending.</p>}
        {filteredTickets.filter(j => j.status === 'PENDING_APPROVAL').map(job => (
          <div key={job.ticketId} className={`rounded-xl shadow-md border p-6 flex flex-col gap-6 ${job.auditFlag === 'HIGH_RISK' ? 'bg-red-50 border-red-200' : 'bg-white border-gray-200'}`}>
            <div className="flex justify-between items-start border-b pb-4">
              <div>
                <h3 className="font-bold text-xl text-gray-800">{job.ticketId}: {job.managerNote}</h3>
                <p className="text-sm font-medium text-gray-500 mt-1">Store: {job.storeId} | Category: {job.category}/{job.subCategory}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-5 bg-gray-50 rounded-xl border border-gray-200 shadow-inner flex flex-col justify-between">
                <div>
                    <p className="text-sm text-gray-500 uppercase tracking-widest font-semibold mb-2">AI Estimate</p>
                    <p className="text-4xl font-light text-gray-800">${job.aiEstimatedCost || 0}</p>
                </div>
                <p className="text-sm text-gray-600 mt-3 bg-white p-3 rounded border"><strong>Diagnosis:</strong> {job.aiDiagnosis || "N/A"}</p>
              </div>
              <div className="p-5 bg-blue-50 border border-blue-200 rounded-xl shadow-inner flex flex-col justify-center">
                <label className="font-bold text-blue-900 mb-2">Assign Vendor to Fix Issue:</label>
                <select 
                    className="border p-2 rounded-lg text-gray-700 shadow-sm w-full"
                    value={selectedVendorForApproval[job.ticketId] || ""}
                    onChange={(e) => setSelectedVendorForApproval({...selectedVendorForApproval, [job.ticketId]: e.target.value})}
                >
                    <option value="">-- Select Approved Vendor --</option>
                    {(vendors || []).map(v => (
                       <option key={v.id} value={v.id}>{v.name} ({v.rating} ⭐)</option>
                    ))}
                </select>
              </div>
            </div>

            <div className="flex justify-between items-center border-t pt-4">
              <button 
                onClick={() => loadTicketForEdit(job)}
                className="flex items-center gap-2 px-4 py-2 border rounded-lg font-semibold text-gray-700 hover:bg-gray-100 transition-colors"
              >
                <Edit className="w-4 h-4" /> Edit Ticket
              </button>

              <button 
                onClick={() => handleApprove(job.ticketId)}
                disabled={!selectedVendorForApproval[job.ticketId]}
                className="bg-blue-600 text-white px-6 py-2.5 rounded-lg font-bold shadow-md hover:bg-blue-700 transition-all disabled:opacity-50 disabled:scale-100 hover:scale-[1.02]"
              >
                Approve & Dispatch
              </button>
            </div>
          </div>
        ))}

        {/* Generic Open/Active Tickets List for Editing/Tracking */}
        <h2 className="text-2xl font-bold pt-8 border-b pb-2">Active Tickets Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredTickets.filter(j => !['PENDING_APPROVAL', 'AWAITING_PAYMENT', 'CLOSED'].includes(j.status)).length === 0 && <p className="text-gray-400 italic">No active tickets.</p>}
          {filteredTickets.filter(j => !['PENDING_APPROVAL', 'AWAITING_PAYMENT', 'CLOSED'].includes(j.status)).map(job => (
             <div key={job.ticketId} className="bg-white border rounded-xl p-4 shadow-sm flex flex-col justify-between">
                <div>
                  <h4 className="font-bold">{job.ticketId}</h4>
                  <p className="text-sm text-gray-600 line-clamp-2">{job.managerNote || "No notes"}</p>
                  <p className="text-xs uppercase font-semibold text-blue-600 mt-2">STATUS: {job.status}</p>
                </div>
                <button onClick={() => loadTicketForEdit(job)} className="mt-4 text-sm font-semibold text-gray-700 border border-gray-300 rounded px-3 py-1.5 hover:bg-gray-50 self-start flex items-center gap-2">
                  <Edit className="w-4 h-4" /> Edit details
                </button>
             </div>
          ))}
        </div>

        {/* Awaiting Payment */}
        <h2 className="text-2xl font-bold pt-8 border-b pb-2">Awaiting Payment</h2>
        {filteredTickets.filter(j => j.status === 'AWAITING_PAYMENT').length === 0 && <p className="text-gray-400 italic">No invoices pending.</p>}
        {filteredTickets.filter(j => j.status === 'AWAITING_PAYMENT').map(job => (
          <div key={job.ticketId} className="bg-green-50 rounded-xl shadow-sm border border-green-200 p-6 flex flex-col md:flex-row justify-between items-center transition-all hover:shadow-md">
            <div>
              <p className="font-bold text-xl text-green-900 flex items-center gap-2 mb-1">
                <CheckCircle className="w-6 h-6 text-green-600" /> {job.ticketId} - Fix Validated
              </p>
              <p className="text-sm text-green-700">AI visually confirmed completion against original parameters.</p>
              <p className="text-xs mt-2">Total final amount: <strong>${job.vendorBid || job.aiEstimatedCost || 0}</strong></p>
            </div>
            <button 
              onClick={() => handlePay(job.ticketId)}
              className="mt-4 md:mt-0 bg-green-600 text-white px-6 py-3 rounded-lg font-bold shadow-md hover:bg-green-700 transition-colors"
            >
              Dispatch Payment
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
