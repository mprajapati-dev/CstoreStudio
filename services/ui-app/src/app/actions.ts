"use server";

import { revalidatePath } from "next/cache";

const API_URL = typeof window === "undefined"
  ? (process.env.INTERNAL_API_URL || "http://ai-agent:8000")
  : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

export async function transitionTicket(ticketId: string, payload: any = {}) {
    console.log("Starting fetch to API...");
    const startFetch = Date.now();
    const res = await fetch(`${API_URL}/tickets/${ticketId}/transition`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    
    if (!res.ok) {
        console.error("Transition failed", await res.text());
        throw new Error("Failed to transition ticket state");
    }
    console.log("Fetch done in", Date.now() - startFetch, "ms");
    
    
    
    return await res.json();
}

export async function fetchTickets() {
    const res = await fetch(`${API_URL}/tickets`, { cache: 'no-store' });
    if (!res.ok) return [];
    const data = await res.json();
    return data.tickets || [];
}

export async function fetchVendorsByCategory(category: string) {
    if (!category) return [];
    const res = await fetch(`${API_URL}/vendors?category=${encodeURIComponent(category)}`, { cache: 'no-store' });
    if (!res.ok) return [];
    const data = await res.json();
    return data.vendors || [];
}
