import boto3
import os

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

dynamodb = boto3.client(
    'dynamodb',
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=REGION,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

# 1. Create Users Table
try:
    dynamodb.create_table(
        TableName='Users',
        KeySchema=[
            {'AttributeName': 'username', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'username', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    print("Users table created.")
except Exception as e:
    if 'ResourceInUseException' in str(e):
        print("Users table already exists.")
    else:
        print(f"Error creating table: {e}")

# 2. Seed Users
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
        "permissions": ["create_ticket", "verify_repair"]
    },
    {
        "username": "owner",
        "password": "owner",
        "role": "OWNER",
        "permissions": ["approve_bid", "dispatch_payment"]
    },
    {
        "username": "vendor1",
        "password": "vendor1",
        "role": "VENDOR",
        "permissions": ["view_assigned", "upload_fix", "submit_invoice"]
    },
    {
        "username": "vendor2",
        "password": "vendor2",
        "role": "VENDOR",
        "permissions": ["view_assigned", "upload_fix", "submit_invoice"]
    },
    {
        "username": "vendor3",
        "password": "vendor3",
        "role": "VENDOR",
        "permissions": ["view_assigned", "upload_fix", "submit_invoice"]
    }
]

for u in users:
    dynamodb.put_item(
        TableName='Users',
        Item={
            'username': {'S': u['username']},
            'password': {'S': u['password']},
            'role': {'S': u['role']},
            'permissions': {'SS': u['permissions']}
        }
    )

print("Seeded Users table.")
