import os
import re

for root, dirs, files in os.walk("services"):
    for file in files:
        if file.endswith(".tsx") or file.endswith(".ts") or file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r") as f:
                content = f.read()
            
            # Replaces
            new_content = content.replace("Clerk", "Manager").replace("clerk", "manager").replace("CLERK", "MANAGER")
            
            if new_content != content:
                with open(path, "w") as f:
                    f.write(new_content)
                print(f"Updated {path}")
