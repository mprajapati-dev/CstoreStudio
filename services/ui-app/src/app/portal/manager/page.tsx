"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { fetchTickets, transitionTicket } from "@/app/actions";
import TicketStatusStepper from "@/components/TicketStatusStepper";
import UploadMedia from "@/components/UploadMedia";
import { Camera, Bot, Upload, AlertCircle } from "lucide-react";

export default function ManagerPortal() {
  const { user, loading: authLoading } = useAuth();
  const [tickets, setTickets] = useState<any[]>([]);
  const [note, setNote] = useState("");
  const [mediaUrl, setMediaUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadTickets();
  }, []);

  const loadTickets = async () => {
    try {
      const data = await fetchTickets();
      // Assume the fetchTickets API returns the raw object array for testing
      setTickets(data.tickets || data); 
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreate = async () => {
    setSubmitting(true);
    const ticketId = "T-" + Math.random().toString(36).substring(2, 8).toUpperCase();
    await transitionTicket(ticketId, {
      media_url: mediaUrl,
      manager_note: note
    });
    setNote("");
    setMediaUrl("");
    await loadTickets();
    setSubmitting(false);
  };

  const handleValidate = async (ticketId: string) => {
    await transitionTicket(ticketId, { action: "VALIDATE" });
    await loadTickets();
  };

  if (authLoading) return null;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Manager Portal</h1>
      <p className="text-gray-500">Welcome, {user?.username}. Report issues for AI Triage.</p>

      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col gap-4">
        <h2 className="text-xl font-semibold flex items-center gap-2"><Camera className="w-5 h-5 text-gray-500" /> New Repair Ticket</h2>
        <textarea
          placeholder="Describe the issue..."
          className="w-full p-3 border rounded-lg"
          rows={3}
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
        <UploadMedia onUploadComplete={setMediaUrl} />
        {mediaUrl && (
          <div className="p-3 bg-blue-50 text-blue-800 rounded-lg flex items-center justify-between border border-blue-200">
            <span className="flex items-center gap-2 text-sm">
              <Bot className="w-4 h-4 text-blue-600" /> Ready for AI Diagnosis
            </span>
          </div>
        )}
        <button
          onClick={handleCreate}
          disabled={submitting || !note}
          className="bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? "Processing..." : mediaUrl ? "Run AI Diagnosis" : "Submit Ticket"}
        </button>
      </div>

      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Active Tickets</h2>
        {tickets && tickets.filter(t => t.status !== "CLOSED").map(t => (
          <div key={t.ticketId} className={`bg-white p-6 rounded-xl shadow-sm border ${t.status === 'VALIDATION_FAILED' ? 'border-red-400 bg-red-50' : 'border-gray-100'}`}>
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-bold text-lg">{t.ticketId}</h3>
              <span className="px-3 py-1 bg-gray-100 text-sm font-mono rounded-full border">{t.status}</span>
            </div>
            
            <TicketStatusStepper currentStatus={t.status} />

            {t.status === "VALIDATION_FAILED" && t.auditFlag === "MANAGER_NOTIFICATION_TRIGGERED" && (
              <div className="mt-4 p-4 border border-red-200 bg-white rounded-lg flex gap-3 text-red-700">
                 <AlertCircle className="w-6 h-6 flex-shrink-0" />
                 <div>
                    <h4 className="font-bold text-sm">AI Visual Verification Failed</h4>
                    <p className="text-xs mt-1">The system detected that the vendor's submitted photograph does not confidently depict a resolved repair. Please contact the vendor immediately to resolve the discrepancy.</p>
                 </div>
              </div>
            )}

            <div className="mt-4 text-sm text-gray-700 bg-white border p-4 rounded-lg">
              <p><strong>Note:</strong> {t.managerNote || "None"}</p>
              {t.aiDiagnosis && (
                <div className="mt-2 text-blue-800 flex items-start gap-2">
                  <Bot className="w-4 h-4 mt-0.5" />
                  <p><strong>AI Diagnosis:</strong> {t.aiDiagnosis} (${t.aiEstimatedCost})</p>
                </div>
              )}
            </div>

            {t.status === "PENDING_VALIDATION" && (
              <div className="mt-4 pt-4 border-t flex items-center justify-between">
                <span className="text-sm text-orange-600 font-medium">Vendor marked as Fixed!</span>
                <button
                  onClick={() => handleValidate(t.ticketId)}
                  className="bg-green-600 text-white px-4 py-2 rounded font-medium hover:bg-green-700 flex items-center gap-2"
                >
                  <Bot className="w-4 h-4" /> Use AI Visual Verification
                </button>
              </div>
            )}
          </div>
        ))}
        {(!tickets || tickets.length === 0) && <p className="text-gray-500">No active tickets.</p>}
      </div>
    </div>
  );
}
