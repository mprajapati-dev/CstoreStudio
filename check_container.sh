#!/bin/bash
docker exec cstorestudio-ui-app-1 cat /app/src/hooks/useAuth.ts > /Users/mprajapati/CstoreStudio/useauth_in_container.txt
docker exec cstorestudio-ui-app-1 cat /app/src/app/page.tsx > /Users/mprajapati/CstoreStudio/page_in_container.txt
