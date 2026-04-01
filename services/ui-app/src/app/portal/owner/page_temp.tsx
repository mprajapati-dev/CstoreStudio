"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { logoutUser } from '@/services/auth';
import { fetchTickets, transitionTicket } from "@/app/actions";
import TicketStatusStepper from "@/components/TicketStatusStepper";
import UploadMedia from "@/components/UploadMedia";
import { Camera, Bot, Upload, AlertCircle, Wrench } from "lucide-react";

const ManagerPortal = () => {
  const { user, loading: authLoading } = useAuth();
  const [tickets, setTickets] = useState<any[]>([]);
  const [note, setNote] = useState("");
  const [mediaUrl, setMediaUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [categories, setCategories] = useState<Record<string, { sub_categories: string[], preferred_vendor_ids: string[] }>>({});
  const [category, setCategory] = useState("");
  const [subCategory, setSubCategory] = useState("");
  const [vendors, setVendors] = useState<any[]>([]);
  // Use SPECIFIC by default directly
  const [dispatchType, setDispatchType] = useState("SPECIFIC");
  const [targetVendorId, setTargetVendorId] = useState("");

  useEffect(() => {
    const fetchCats = async () => {
      try {
        const res = await fetch("http://localhost:8000/categories"); // Direct backend call
        if (res.ok) {
          const data = await res.json();
          setCategories(data);
          const firstCat = Object.keys(data)[0] || "";
          setCategory(firstCat);
          setSubCategory(data[firstCat]?.sub_categories?.[0] || "");
        } else {
          console.error("Failed to fetch categories from http://localhost:8000/categories");
        }
      } catch (err) {
        console.error("Error fetching categories:", err);
      }
    };
    fetchCats();
  }, []);

  const fetchVendorsByIds = async (ids: string[], currentCategory: string) => {
    if (!ids.length || !currentCategory) return [];
    try {
      // Direct call to your FastAPI backend, passing category for composite key
      const res = await fetch(`http://localhost:8000/vendors?ids=${ids.join(",")}&category=${currentCategory}`);
      if (res.ok) {
        return await res.json();
      }
      return [];
    } catch (e) {
      console.error("Error fetching vendors from API:", e);
      return [];
    }
  };

  useEffect(() => {
    if (user?.store_id) {
      loadTickets();
    }
  }, [user]);

  const loadTickets = async () => {
    try {
      const data = await fetchTickets();
      const allTickets = data.tickets || data; 
      setTickets(allTickets.filter((t: any) => t.storeId === user?.store_id));
    } catch (e) {
      console.error(e);
    }
  };

  const handleCategoryChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const cat = e.target.value;
    setCategory(cat);
    // Set first sub-category if available, else empty string
    const firstSub = categories[cat]?.sub_categories?.[0] || "";
    setSubCategory(firstSub);
    setTargetVendorId("");
    if (dispatchType === "SPECIFIC" && cat && categories[cat]) {
      const preferredIds = categories[cat].preferred_vendor_ids || [];
      if (preferredIds.length > 0) {
        const vendorList = await fetchVendorsByIds(preferredIds, cat);
        setVendors(vendorList);
        if (vendorList.length > 0) {
          setTargetVendorId(vendorList[0].vendorId);
        }
      } else {
        setVendors([]);
      }
    } else {
      setVendors([]);
    }
  };

  // When dispatchType changes, update vendors if needed
  useEffect(() => {
    const updatePreferredVendors = async () => {
      // Changed from "DIRECT" to "SPECIFIC"
      if (dispatchType === "SPECIFIC" && category && categories[category]) {
        const preferredIds = categories[category].preferred_vendor_ids || [];
        if (preferredIds.length > 0) {
          const fetchedVendors = await fetchVendorsByIds(preferredIds, category);
          setVendors(fetchedVendors);
          if (fetchedVendors.length > 0) {
            setTargetVendorId(fetchedVendors[0].vendorId);
          } else {
            setTargetVendorId("");
          }
        } else {
          setVendors([]);
          setTargetVendorId("");
        }
      } else {
        setVendors([]);
        setTargetVendorId("");
      }
    };

    updatePreferredVendors();
  }, [dispatchType, category, categories]);


  const handleVerify = async (ticketId: string) => {
    await transitionTicket(ticketId, { action: "VERIFY" });
    await loadTickets();
  };

  const handleSubmit = async () => {

    setSubmitting(true);
    const ticketId = "T-" + Math.random().toString(36).substring(2, 8).toUpperCase();
    // TODO: Add your ticket transition logic here, using the state variables from the top-level component
    await transitionTicket(ticketId, {
      category,
      subCategory,
      targetVendorId,
      note,
      mediaUrl,
      store_id: user?.store_id || "DEFAULT",
      action: dispatchType === "SPECIFIC" ? "DISPATCH" : "BROADCAST"
    });
    setNote("");
    setMediaUrl("");
    setSubmitting(false);
    await loadTickets();
    alert("Ticket created and is now processing!");
  };
  if (authLoading) {
    return <div className="p-8">Loading...</div>;
  }
  if (!user) {
    return <div className="p-8">You must be logged in to access this page.</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Manager Portal ({user?.store_id || user?.username})</h1>
        <button 
          onClick={logoutUser} 
          className="px-4 py-2 bg-red-100 text-red-600 rounded hover:bg-red-200"
        >
          Logout
        </button>
      </div>
      {/* Ticket Intake Form */}
      <form
        className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col gap-4"
        onSubmit={e => {
          e.preventDefault();
          handleSubmit();
        }}
      >
        <div>
          <label>Category:</label>
          <select
            value={category}
            onChange={handleCategoryChange}
            className="w-full p-2 border rounded"
          >
            <option value="">Select Category...</option>
            {Object.keys(categories).map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
        <div>
          <label>Sub-category:</label>
          <select
            value={subCategory}
            onChange={e => setSubCategory(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="">Select Sub-category...</option>
            {(categories[category]?.sub_categories || []).map(sub => (
              <option key={sub} value={sub}>{sub}</option>
            ))}
          </select>
        </div>
        <div>
          <label>Dispatch Type:</label>
          <div>
            <label className="opacity-50 cursor-not-allowed">
              <input
                type="radio"
                name="dispatchType"
                value="BROADCAST"
                checked={dispatchType === "BROADCAST"}
                disabled
              />
              Broadcast for Bids
            </label>
            <label className="ml-4">
              <input
                type="radio"
                name="dispatchType"
                value="SPECIFIC"
                checked={dispatchType === "SPECIFIC"}
                onChange={e => setDispatchType(e.target.value)}
              />
              Send to Specific Vendor
            </label>
          </div>
        </div>
        {dispatchType === "SPECIFIC" && (
          <div>
            <label className="block text-sm font-medium mb-1">Select Vendor</label>
            <select
              value={targetVendorId}
              onChange={(e) => setTargetVendorId(e.target.value)}
              className="w-full border rounded p-2"
              required
            >
              <option value="">-- Choose a Vendor --</option>
              {vendors.map((v: any) => (
                <option key={v.vendorId} value={v.vendorId}>{v.name}</option>
              ))}
            </select>
            {vendors.length === 0 && (
              <div className="text-xs text-orange-600 mt-1">
                No preferred vendors found for this category.
              </div>
            )}
          </div>
        )}
        <div>
          <label>Note:</label>
          <textarea
            value={note}
            onChange={e => setNote(e.target.value)}
            className="w-full p-2 border rounded"
            rows={2}
          />
        </div>
        <div>
          <label>Upload Media:</label>
          <UploadMedia onUploadComplete={setMediaUrl} />
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
          disabled={submitting}
        >
          {submitting ? "Submitting..." : "Create Ticket"}
        </button>
      </form>

      {/* Ticket List */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h2 className="text-xl font-semibold mb-4">My Tickets</h2>
        {tickets.length === 0 ? (
          <div>No tickets found.</div>
        ) : (
          <div className="space-y-4">
            {tickets.map(ticket => (
              <div key={ticket.ticketId || ticket.id} className="border-b pb-2">
                <div className="font-semibold">{ticket.category} - {ticket.subCategory}</div>
                <div>Status: {ticket.status}</div>
                <div>Note: {ticket.note}</div>
                {/* Add more ticket details as needed */}
                <TicketStatusStepper currentStatus={ticket.status} />
                {ticket.status === "MANUAL_VALIDATION_REQUIRED" && (
                  <button 
                    onClick={() => handleVerify(ticket.ticketId)}
                    className="mt-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                  >
                    Verify Fix
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ManagerPortal;
