import boto3
import os
import random
from decimal import Decimal

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=REGION,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

def seed_categories(preferred_vendor_ids_map=None):
    table = dynamodb.Table('Categories')
    categories = [
        {
            "category": "GAS",
            "sub_categories": ["Leaking Nozzle", "Pump Display", "Tank Monitor"]
        },
        {
            "category": "HVAC",
            "sub_categories": ["AC Not Cooling", "Walk-in Cooler", "Ice Machine"]
        },
        {
            "category": "ELECTRICITY",
            "sub_categories": ["Parking Lot Lights", "Breaker Tripped", "Signage"]
        },
        {
            "category": "BEER_DEN",
            "sub_categories": ["Keg Cooler", "Tap Handle", "CO2 Leak"]
        },
        {
            "category": "INVENTORY",
            "sub_categories": ["Shelving", "POS Scanner"]
        }
    ]
    for cat in categories:
        if preferred_vendor_ids_map:
            cat["preferred_vendor_ids"] = preferred_vendor_ids_map.get(cat["category"], [])
        table.put_item(Item=cat)
    print("Seeded Categories")

def get_categories_from_db():
    table = dynamodb.Table('Categories')
    response = table.scan()
    categories = {}
    for item in response.get('Items', []):
        categories[item['category']] = item['sub_categories']
    return categories

def seed_vendors():
    table = dynamodb.Table('Vendors')
    categories_map = get_categories_from_db()
    categories = list(categories_map.keys())
    names = [
        "Mario Bros Plumbing", "Pipe Masters", "Leak Busters",
        "Sparky Electric", "Volts & Watts", "Current Solutions",
        "Cool Breeze HVAC", "Arctic Air", "HeatWave Solutions",
        "All-Around Fixers"
    ]
    preferred_vendor_ids_map = {}
    # Seed one preferred vendor per category
    for i, cat in enumerate(categories):
        vendor_id = f"preferred-{cat.lower()}"
        item = {
            "vendorId": vendor_id,
            "category": cat,
            "sub_categories": list(categories_map[cat]),
            "name": f"Preferred {cat.capitalize()} Vendor",
            "contactEmail": f"preferred_{cat.lower()}@example.com",
            "phone": f"555-100{i}",
            "rating": Decimal(str(round(random.uniform(4.5, 5.0), 1))),
            "hourly_rate": Decimal(str(round(random.uniform(80, 150), 2))),
            "preferred": True
        }
        table.put_item(Item=item)
        preferred_vendor_ids_map.setdefault(cat, []).append(vendor_id)
    # Seed additional non-preferred vendors
    for i in range(1, 6):
        cat = random.choice(categories)
        item = {
            "vendorId": f"v{i}",
            "category": cat,
            "sub_categories": list(categories_map[cat]),
            "name": names[i-1],
            "contactEmail": f"vendor{i}@example.com",
            "phone": f"555-010{i}",
            "rating": Decimal(str(round(random.uniform(4.0, 4.9), 1))),
            "hourly_rate": Decimal(str(round(random.uniform(50, 120), 2))),
            "preferred": False
        }
        table.put_item(Item=item)
    print("Seeded preferred and regular vendors for all categories")
    return preferred_vendor_ids_map

def seed_users():
    table = dynamodb.Table('Users')
    users = [
        {
            "username": "admin", 
            "password": "admin", 
            "role": "SUPER_USER", 
            "permissions": ["all"]
        },
        {
            "username": "manager", 
            "password": "manager", 
            "role": "MANAGER", 
            "permissions": ["create_ticket", "verify_repair"],
            "store_id": "ST-101",
            "store_name": "Sunrise Mart #101"
        },
        {
            "username": "owner", 
            "password": "owner", 
            "role": "OWNER", 
            "permissions": ["approve_bid", "dispatch_payment"],
            "managed_stores": ["ST-101", "ST-102"]
        },
        {
            "username": "vendor_gas", 
            "password": "vendor_gas", 
            "role": "VENDOR", 
            "permissions": ["view_assigned", "upload_fix", "submit_invoice"],
            "category": "GAS",
            "vendor_id": "preferred-gas"
        },
        {
            "username": "vendor_hvac", 
            "password": "vendor_hvac", 
            "role": "VENDOR", 
            "permissions": ["view_assigned", "upload_fix", "submit_invoice"],
            "category": "HVAC",
            "vendor_id": "preferred-hvac"
        },
        {
            "username": "vendor_electric", 
            "password": "vendor_electric", 
            "role": "VENDOR", 
            "permissions": ["view_assigned", "upload_fix", "submit_invoice"],
            "category": "ELECTRICITY",
            "vendor_id": "preferred-electricity"
        },
        {
            "username": "vendor_beer", 
            "password": "vendor_beer", 
            "role": "VENDOR", 
            "permissions": ["view_assigned", "upload_fix", "submit_invoice"],
            "category": "BEER_DEN",
            "vendor_id": "preferred-beer_den"
        },
        {
            "username": "vendor_inv", 
            "password": "vendor_inv", 
            "role": "VENDOR", 
            "permissions": ["view_assigned", "upload_fix", "submit_invoice"],
            "category": "INVENTORY",
            "vendor_id": "preferred-inventory"
        }
    ]
    for u in users:
        table.put_item(Item=u)
    print("Seeded Users")

def seed_initial_ticket():
    table = dynamodb.Table('Tickets')
    ticket = {
        "ticketId": "T-001",
        "store_id": "ST-101",
        "category": "GAS",
        "sub_category": "Leaking Nozzle",
        "status": "OPEN",
        "media_url": "http://dummy.com/video.mp4",
        "audit_log": []
    }
    table.put_item(Item=ticket)
    print("Seeded Initial Ticket T-002")

def seed_stores():
    table = dynamodb.Table('Stores')
    stores = [
        {"storeId": "ST-101", "free_vision_credits": 10, "tier": "STANDARD"},
        {"storeId": "ST-102", "free_vision_credits": 0, "tier": "PREMIUM"},
    ]
    print("Seeding Stores...")
    for store in stores:
        table.put_item(Item=store)
    print("Seeded Stores")

if __name__ == "__main__":
    try:
        # Step 1: Seed categories without preferred_vendor_ids
        seed_categories()
        # Step 2: Seed vendors and get preferred vendor ids per category
        preferred_vendor_ids_map = seed_vendors()
        # Step 3: Update categories with preferred_vendor_ids
        seed_categories(preferred_vendor_ids_map)
        # Step 4: Seed other entities
        seed_users()
        seed_initial_ticket()
        seed_stores()
        print("Database seeding complete!")
    except Exception as e:
        print(f"Error during seeding: {e}")