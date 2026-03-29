with open("services/ui-app/src/app/portal/admin/page.tsx", "r") as f:
    content = f.read()

new_content = content.replace("const [users, setUsers] = useState([]);", 
"""interface PortalUser {
  username: string;
  role: string;
  permissions: string[];
}

  const [users, setUsers] = useState<PortalUser[]>([]);""")

with open("services/ui-app/src/app/portal/admin/page.tsx", "w") as f:
    f.write(new_content)
