import boto3
import os
import random

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

dynamodb = boto3.client(
    'dynamodb',
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=REGION,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

def seed_users():
    users = [
        {"username": {"S": "admin"}, "password": {"S": "admin"}, "role": {"S": "SUPER_USER"}, "permissions": {"SS": ["all"]}},
        {"username": {"S": "manager"}, "password": {"S": "manager"}, "role": {"S": "MANAGER"}, "permissions": {"SS": ["create_ticket", "verify_repair"]}},
        {"username": {"S": "owner"}, "password": {"S": "owner"}, "role": {"S": "OWNER"}, "permissions": {"SS": ["approve_bid", "dispatch_payment"]}},
        {"username": {"S": "vendor1"}, "password": {"S": "vendor1"}, "role": {"S": "VENDOR"}, "permissions": {"SS": ["view_assigned", "upload_fix", "submit_invoice"]}}
    ]
    for u in users:
        dynamodb.put_item(TableName="Users", Item=u)
    print("Seeded Users")

def seed_vendors():
    categories = ['Plumbing', 'Electrical', 'HVAC']
    names = [
        "Mario Bros Plumbing", "Pipe Masters", "Leak Busters",
        "Sparky Electric", "Volts & Watts", "Current Solutions",
        "Cool Breeze HVAC", "Arctic Air", "HeatWave Solutions",
        "All-Around Fixers"
    ]
    
    for i in range(1, 11):
        cat = random.choice(categories)
        item = {
            "vendorId": {"S": f"v{i}"},
            "category": {"S": cat},
            "name": {"S": names[i-1]},
            "contactEmail": {"S": f"vendor{i}@example.com"},
            "phone": {"S": f"555-010{i}"},
            "rating": {"N": str(round(random.uniform(4.0, 5.0), 1))}
        }
        dynamodb.put_item(TableName="Vendors", Item=item)
    print("Seeded 10 Vendors")

if __name__ == "__main__":
    print(f"Connecting to DynamoDB at {AWS_ENDPOINT_URL}")
    seed_users()
    seed_vendors()
    print("Database seeding complete!")
