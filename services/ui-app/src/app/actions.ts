"use server";

import { revalidatePath } from "next/cache";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function transitionTicket(ticketId: string, payload: any = {}) {
    const res = await fetch(`${API_URL}/tickets/${ticketId}/transition`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    
    if (!res.ok) {
        console.error("Transition failed", await res.text());
        throw new Error("Failed to transition ticket state");
    }
    
    revalidatePath("/portal/manager");
    revalidatePath("/portal/owner");
    revalidatePath("/portal/vendor");
    
    return await res.json();
}

export async function fetchTickets() {
    const res = await fetch(`${API_URL}/tickets`, { cache: 'no-store' });
    if (!res.ok) return [];
    const data = await res.json();
    return data.tickets || [];
}
