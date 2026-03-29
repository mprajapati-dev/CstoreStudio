import re

with open('services/ui-app/src/components/UploadMedia.tsx', 'r') as f:
    text = f.read()

text = text.replace('Clerk Intake', 'Manager Intake')
text = text.replace('clerk_note', 'manager_note')
text = text.replace('clerkNote', 'managerNote')
text = text.replace('Clerk Note', 'Manager Note')
text = text.replace('setClerkNote', 'setManagerNote')

with open('services/ui-app/src/components/UploadMedia.tsx', 'w') as f:
    f.write(text)

