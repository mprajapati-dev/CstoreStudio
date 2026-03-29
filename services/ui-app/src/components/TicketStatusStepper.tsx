import { CheckCircle2, Circle } from "lucide-react";

export const STATUS_ORDER = [
  "OPEN",
  "AWAITING_BIDS",
  "PENDING_APPROVAL",
  "IN_PROGRESS",
  "PENDING_VALIDATION",
  "AWAITING_PAYMENT",
  "CLOSED"
];

export const STATUS_LABELS: Record<string, string> = {
  OPEN: "Intake",
  AWAITING_BIDS: "Bidding",
  PENDING_APPROVAL: "Approval",
  IN_PROGRESS: "Repairing",
  PENDING_VALIDATION: "QA Validation",
  AWAITING_PAYMENT: "Payment",
  CLOSED: "Closed"
};

export default function TicketStatusStepper({ currentStatus }: { currentStatus: string }) {
  const currentIndex = STATUS_ORDER.indexOf(currentStatus);

  return (
    <div className="flex w-full items-center justify-between mt-4 mb-6 relative">
      <div className="absolute left-0 top-1/2 -z-10 h-1 rounded w-full bg-gray-200 -translate-y-1/2" />
      <div 
        className="absolute left-0 top-1/2 -z-10 h-1 rounded bg-blue-500 transition-all -translate-y-1/2 duration-500" 
        style={{ width: `${(Math.max(0, currentIndex) / (STATUS_ORDER.length - 1)) * 100}%` }} 
      />
      
      {STATUS_ORDER.map((step, idx) => {
        const isCompleted = idx < currentIndex;
        const isCurrent = idx === currentIndex;
        return (
          <div key={step} className="flex flex-col items-center relative gap-1">
            <div className={`flex h-8 w-8 items-center justify-center rounded-full border-4 bg-white ${
                isCompleted ? "border-blue-500 text-blue-500" : isCurrent ? "border-blue-600 border-4 text-blue-600" : "border-gray-300 text-gray-300"
              }`}
            >
              {isCompleted ? <CheckCircle2 className="h-5 w-5" /> : <Circle className="h-3 w-3 fill-current" />}
            </div>
            <span className={`text-[10px] font-medium absolute -bottom-5 w-20 text-center ${isCompleted || isCurrent ? "text-blue-900" : "text-gray-400"}`}>
              {STATUS_LABELS[step]}
            </span>
          </div>
        );
      })}
    </div>
  );
}
