import re

with open("services/ui-app/src/app/portal/manager/page.tsx", "r") as f:
    text = f.read()

# Fix the transitionTicket call to include action
text = text.replace(
'''    await transitionTicket(ticketId, {
      category,
      subCategory,
      dispatchType,
      targetVendorId,
      note,
      mediaUrl,
      store_id: user?.store_id || "DEFAULT"
    });''',
'''    await transitionTicket(ticketId, {
      category,
      subCategory,
      targetVendorId,
      note,
      mediaUrl,
      store_id: user?.store_id || "DEFAULT",
      action: dispatchType === "SPECIFIC" ? "DISPATCH" : "BROADCAST"
    });''')

with open("services/ui-app/src/app/portal/manager/page.tsx", "w") as f:
    f.write(text)

print("Submit Action Patched!")
