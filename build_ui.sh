#!/bin/bash
cd /Users/mprajapati/CstoreStudio
docker-compose up -d --build ui-app
docker-compose ps > ps_output.txt
