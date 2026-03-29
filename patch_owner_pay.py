with open('services/ui-app/src/app/owner/page.tsx', 'r') as f:
    text = f.read()

import re

# Add to imports
pay_function = """
  const updateStatus = async (jobId: string, status: string) => {
"""

pay_function_new = """
  const handlePayment = async (jobId: string, amount: number) => {
    try {
      await fetch(`http://localhost:8000/jobs/${jobId}/pay`, {
        method: "POST"
      });
      alert(`Payment Complete - $${amount} sent to Vendor.`);
      fetchJobs();
    } catch (error) {
      console.error("Payment failed", error);
    }
  };

  const updateStatus = async (jobId: string, status: string) => {
"""

text = text.replace(pay_function, pay_function_new)

# Add Pay Vendor button
button_old = """
                    {job.approval_status !== "Pending Bid Selection" && (
                      <button 
                        onClick={() => updateStatus(job.job_id, "Vendor Dispatched")}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded shadow transition-colors ml-auto"
                      >
                        Mark as Dispatched
                      </button>
                    )}
"""

button_new = """
                    {job.approval_status === "Ready for Payment" && (
                      <button 
                        onClick={() => handlePayment(job.job_id, job.invoice_amount || job.estimated_cost)}
                        className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded shadow transition-colors ml-auto"
                      >
                        💸 Pay Vendor
                      </button>
                    )}
                    {job.approval_status !== "Pending Bid Selection" && job.approval_status !== "Ready for Payment" && job.approval_status !== "Payment Complete" && (
                      <button 
                        onClick={() => updateStatus(job.job_id, "Vendor Dispatched")}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded shadow transition-colors ml-auto"
                      >
                        Mark as Dispatched
                      </button>
                    )}
"""

text = text.replace(button_old, button_new)

with open('services/ui-app/src/app/owner/page.tsx', 'w') as f:
    f.write(text)

