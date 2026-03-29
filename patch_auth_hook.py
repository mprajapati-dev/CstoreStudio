import os
import re

hook_pattern = """
import { useAuth } from '@/hooks/useAuth';
"""

for root, dirs, files in os.walk("services/ui-app/src/app/portal"):
    for file in files:
        if file == "page.tsx":
            path = os.path.join(root, file)
            with open(path, "r") as f:
                content = f.read()

            if "useAuth" in content:
                continue

            # Identify the component start
            match = re.search(r'export default function (\w+)\(\) {', content)
            if match:
                comp_name = match.group(1)
                
                # add import
                lines = content.split('\n')
                lines.insert(2, "import { useAuth } from '@/hooks/useAuth';")
                new_content = '\n'.join(lines)
                
                # inject hook
                hook_code = """
  const { user, loading: authLoading } = useAuth();
  if (authLoading) return <div className="p-8 text-center text-gray-500">Loading Auth...</div>;
  if (!user) return null;
"""
                new_content = new_content.replace(f"export default function {comp_name}() {{", 
                                                  f"export default function {comp_name}() {{{hook_code}")
                
                # Check for existing loading states to avoid duplicate variable names or conflicts
                # Since vendor and owner already have their own `loading`, let's rename `authLoading`
                # actually I already renamed to `authLoading` above!

                with open(path, 'w') as f:
                    f.write(new_content)
                print(f"Patched {path}")
