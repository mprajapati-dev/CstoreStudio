import re

with open("services/ui-app/src/app/portal/manager/page.tsx", "r") as f:
    text = f.read()

# Add handleVerify function
func_to_add = '''
  const handleVerify = async (ticketId: string) => {
    await transitionTicket(ticketId, { action: "VERIFY" });
    await loadTickets();
  };

  const handleSubmit = async () => {
'''
text = text.replace("  const handleSubmit = async () => {", func_to_add)

# Add Verify Button
btn_to_add = '''                <TicketStatusStepper currentStatus={ticket.status} />
                {ticket.status === "MANUAL_VALIDATION_REQUIRED" && (
                  <button 
                    onClick={() => handleVerify(ticket.ticketId)}
                    className="mt-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                  >
                    Verify Fix
                  </button>
                )}'''
text = text.replace("                <TicketStatusStepper currentStatus={ticket.status} />", btn_to_add)

# Fix key={ticket.id} just in case
text = text.replace("key={ticket.id}", "key={ticket.ticketId || ticket.id}")

with open("services/ui-app/src/app/portal/manager/page.tsx", "w") as f:
    f.write(text)

print("Manager portal patched!")
