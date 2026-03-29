import urllib.request
import json
import boto3

dynamodb = boto3.client(
    'dynamodb',
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

# Fetch current jobs to see if we have old docker logos
print("Checking for old Docker logos in the database...")
resp = dynamodb.scan(TableName='Jobs')
items = resp.get('Items', [])
count = 0

for item in items:
    job_id = item.get('jobId', {}).get('S', '')
    media_url = item.get('mediaUrl', {}).get('S', '')
    if 'logo.png' in media_url:
        print(f"Found old logo on Job ID: {job_id}")
        
        # Determine a new mock URL based on category
        category = item.get('category', {}).get('S', 'General')
        category_images = {
            "Gas Pump": "https://images.unsplash.com/photo-1598442084534-11884e9d5690?auto=format&fit=crop&q=80&w=600",
            "Fuel Tank": "https://images.unsplash.com/photo-1598442084534-11884e9d5690?auto=format&fit=crop&q=80&w=600",
            "HVAC": "https://images.unsplash.com/photo-1581094288338-3483df2ea124?auto=format&fit=crop&q=80&w=600",
            "Internet": "https://images.unsplash.com/photo-1551703599-6b3e8379aa8b?auto=format&fit=crop&q=80&w=600",
            "Soft-Drinks Vendor": "https://images.unsplash.com/photo-1601598851547-4302969d0614?auto=format&fit=crop&q=80&w=600",
            "Beers": "https://images.unsplash.com/photo-1601598851547-4302969d0614?auto=format&fit=crop&q=80&w=600",
            "Electrical": "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?auto=format&fit=crop&q=80&w=600",
            "Plumbing": "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?auto=format&fit=crop&q=80&w=600",
            "Inventory / Coolers": "https://images.unsplash.com/photo-1601598851547-4302969d0614?auto=format&fit=crop&q=80&w=600",
            "General": "https://images.unsplash.com/photo-1581141849291-1125c7b692b5?auto=format&fit=crop&q=80&w=600"
        }
        new_url = category_images.get(category, category_images["General"])
        
        # Update DynamoDB
        print(f"Updating {job_id} to {new_url}...")
        dynamodb.update_item(
            TableName='Jobs',
            Key={'jobId': {'S': job_id}},
            UpdateExpression='SET mediaUrl = :val',
            ExpressionAttributeValues={':val': {'S': new_url}}
        )
        count += 1
        
print(f"Updated {count} old logo references.")
