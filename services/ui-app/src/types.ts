/**
 * UserRoles define the access level and permissions within the CstoreStudio system.
 */
export type UserRole = 'MANAGER' | 'OWNER' | 'VENDOR' | 'ADMIN';

/**
 * Represents a user in the multi-tenant system.
 */
export interface User {
  username: string;
  role: UserRole;
  store_id: string; // The primary store they are associated with
  store_name: string;
  managed_stores: string[]; // List of store IDs they have access to
}

/**
 * The Categorized Domain for C-Store operations.
 */
export const STORE_CATEGORIES = {
  GAS: ['Leaking Nozzle', 'Pump Display', 'Tank Monitor'],
  HVAC: ['AC Not Cooling', 'Walk-in Cooler', 'Ice Machine'],
  ELECTRICITY: ['Parking Lot Lights', 'Breaker Tripped', 'Signage'],
  BEER_DEN: ['Keg Cooler', 'Tap Handle', 'CO2 Leak'],
  INVENTORY: ['Shelving', 'POS Scanner'],
} as const;

/**
 * Main categories derived from the STORE_CATEGORIES keys.
 */
export type MainCategory = keyof typeof STORE_CATEGORIES;

/**
 * Represents the lifecycle stages of a ticket in the repair journey state machine.
 */
export type TicketStatus = 
  | 'OPEN' 
  | 'AWAITING_BIDS' 
  | 'PENDING_APPROVAL' 
  | 'IN_PROGRESS' 
  | 'PENDING_VALIDATION' 
  | 'AWAITING_PAYMENT' 
  | 'CLOSED';

/**
 * The priority level of a ticket.
 */
export type TicketPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'EMERGENCY';

/**
 * Represents a structured historical action taken on a ticket.
 */
export interface AuditEntry {
  timestamp: string;
  actor: string;
  action: string;
  message: string;
}

/**
 * The core ticket representation encompassing metadata, state, and auditing.
 */
export interface Ticket {
  id: string; // uuid
  store_id: string; // Partition Key for isolation
  store_name: string;
  category: MainCategory;
  sub_category: string;
  status: TicketStatus;
  priority: TicketPriority;
  manager_notes: string;
  media_url?: string; // Original problem (Photo/Video)
  fix_media_url?: string; // Vendor's proof of fix
  ai_estimated_value?: number;
  selected_vendor_id?: string;
  audit_log: AuditEntry[]; // Structured history
}

/**
 * Represents a bid submitted by a vendor for a specific ticket.
 */
export interface VendorBid {
  bid_id: string;
  ticket_id: string;
  vendor_id: string;
  vendor_name: string;
  amount: number;
  eta_days: number;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
}

/**
 * The AI Auditor's assessment report on a ticket or vendor bid/fix.
 */
export interface AuditorReport {
  is_verified: boolean;
  confidence: number;
  reasoning: string;
  suggested_action?: string;
}

/**
 * Represents a vendor profile in the procurement system.
 */
export interface Vendor {
  id: string;
  name: string;
  category: MainCategory;
  rating: number;
  hourly_rate: number;
}
