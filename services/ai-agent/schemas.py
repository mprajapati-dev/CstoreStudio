from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class Role(str, Enum):
    SUPER_USER = "SUPER_USER"
    MANAGER = "MANAGER"
    OWNER = "OWNER"
    VENDOR = "VENDOR"

class User(BaseModel):
    username: str
    password: str
    role: Role
    permissions: List[str] = Field(default_factory=list)

class TicketStatus(str, Enum):
    OPEN = "OPEN"
    AWAITING_BIDS = "AWAITING_BIDS"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_VALIDATION = "PENDING_VALIDATION"
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    CLOSED = "CLOSED"

class Ticket(BaseModel):
    ticketId: str
    mediaUrl: Optional[str] = None
    category: str = "General"
    managerNote: Optional[str] = None
    aiDiagnosis: Optional[str] = None
    aiEstimatedCost: float = 0.0
    status: TicketStatus = TicketStatus.OPEN
    storeId: Optional[str] = None
    assetId: Optional[str] = None
    assignedVendorId: Optional[str] = None
    postRepairMediaUrl: Optional[str] = None
    finalInvoiceAmount: float = 0.0

class Vendor(BaseModel):
    vendorId: str
    category: str
    name: str
    contactEmail: str
    phone: str
    rating: float = 5.0

class Bid(BaseModel):
    bidId: str
    ticketId: str
    vendorId: str
    amount: float
    availability: str
