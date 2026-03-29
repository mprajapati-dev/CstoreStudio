import boto3

dynamodb = boto3.client(
    'dynamodb',
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

vendors = [
    # Plumbing
    {"vendorId": "P1", "category": "Plumbing", "name": "Mario Bros Plumbing", "hourlyRate": 85, "averageRating": 4.8},
    {"vendorId": "P2", "category": "Plumbing", "name": "Pipe Masters", "hourlyRate": 95, "averageRating": 4.5},
    {"vendorId": "P3", "category": "Plumbing", "name": "Leak Busters", "hourlyRate": 75, "averageRating": 3.9},
    # Electrical
    {"vendorId": "E1", "category": "Electrical", "name": "Sparky Electric", "hourlyRate": 100, "averageRating": 4.9},
    {"vendorId": "E2", "category": "Electrical", "name": "Volts & Watts", "hourlyRate": 110, "averageRating": 4.7},
    {"vendorId": "E3", "category": "Electrical", "name": "Current Solutions", "hourlyRate": 90, "averageRating": 4.1},
    # HVAC
    {"vendorId": "H1", "category": "HVAC", import boto3

dynamodb = boto3.clienat
dynamodb =ver    'dynamodb',
    end"v    endpoint_u,     region_name="us-east-1",
    aws_acc,     aws_access_key_id='testRa    aws_secret_access_key='t: )

vendors = [
    # Plumbing
 ": "H    # Plumlu    {"vendorIly    {"vendorId": "P2", "category": "Plumbing", "name": "Pipe Masters", "hourlyRate": 95, "averageRating": 4.5},
    {em    {"vendorId": "P3", "category": "Plumbing", "name": "Leak Busters", "hourlyRate": 75, "averageRating": 3.9}me    # Electrical
    {"vendorId": "E1", "category": "Electrical", "name": "Sparky Electric", "hourlyRate": 100 s    {"vendorId"ti    {"vendorId": "E2", "category": "Electrical", "name": "Volts & Watts", "hourly exit
 EOF
 EOF
 kill -9 $$
 docker compose exec ai-agent python /app/seed_vendors.py
 python -c '
import os
import boto3

dynamodb = boto3.client(
    "dynamodb",
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

vendors = [
    {"vendorId": "P1", "category": "Plumbing", "name": "Mario Bros Plumbing", "hourlyRate": 85, "averageRating": 4.8},
    {"vendorId": "P2", "category": "Plumbing", "name": "Pipe Masters", "hourlyRate": 95, "averageRating": 4.5},
    {"vendorId": "P3", "category": "Plumbing", "name": "Leak Busters", "hourlyRate": 75, "averageRating": 3.9},
    {"vendorId": "E1", "category": "Electrical", "name": "Sparky Electric", "hourlyRate": 100, "averageRating": 4.9},
    {"vendorId": "E2", "category": "Electrical", "name": "Volts & Watts", "hourlyRate": 110, "averageRating": 4.7},
    {"vendorId": "E3", "category": "Electrical", "name": "Current Solutions", "hourlyRate": 90, "averageRating": 4.1},
    {"vendorId": "H1", "category": "HVAC", "name": "Cool Breeze HVAC", "hourlyRate": 120, "averageRatimport os
i
 import bdo
dynamodb = "c    "dynamodb",
    end":    endpoint_u "    region_name="us-east-1",
    aws_acc
     aws_access_key_id="testgo    aws_secret_access_key="tve)

vendors = [
    {"vendorId": "ave    {"vend":    {"vendorId": "P2", "category": "Plumbing", "name": "Pipe Masters", "hourlyRate": 95, "averageRating": 4.5},
    { {    {"vendorId": "P3", "category": "Plumbing", "name": "Leak Busters", "hourlyRate": 75, "averageRating": 3.9}      {"vendorId": "E1", "category": "Electrical", "name": "Sparky Electric", "hourlyRate": 100, "averageRating"      {"vendorId": "E2", "category": "El cd /Users/mprajapati/CstoreStudio && source .venv/bin/activate && pip install boto3 && python seed_vendors.py
 '
