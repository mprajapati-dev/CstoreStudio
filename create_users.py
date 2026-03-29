import boto3

dynamodb = boto3.client(
    'dynamodb',
    endpoint_url='http://localhost:4566',
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

users = [
    {"username": {"S": "admin"}, "password": {"S": "password123"}, "role": {"S": "admin"}},
    {"username": {"S": "manager"}, "password": {"S": "password123"}, "role": {"S": "manager"}},
    {"username": {"S": "owner"}, "password": {"S": "password123"}, "role": {"S": "owner"}},
    {"username": {"S": "vendor1"}, "password": {"S": "password123"}, "role": {"S": "vendor"}}
]

for user in users:
    dynamodb.put_item(TableName='Users', Item=user)
    print(f"Created user: {user['username']['S']}")
