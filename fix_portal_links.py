import os
import re

for root, dirs, files in os.walk("services/ui-app/src/app/portal"):
    for file in files:
        if file.endswith(".tsx") or file.endswith(".ts"):
            path = os.path.join(root, file)
            with open(path, "r") as f:
                content = f.read()
            
            # Replaces href="/" with href="/" onClick={() => localStorage.removeItem('user')} if needed or similar, but the main thing is fixing any references
            new_content = content.replace('href="/"', 'href="/" onClick={() => localStorage.removeItem(\'user\')}')
            new_content = new_content.replace('Back to Home', 'Logout').replace('Back to Main', 'Logout')
            
            if new_content != content:
                with open(path, "w") as f:
                    f.write(new_content)
                print(f"Updated {path}")
