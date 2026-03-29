import boto3

dynamodb = boto3.client(
    'dynamodb',
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

vendors = [
    {"vendorId": "P1", "category": "Plumbing", "name": "Mario Bros Plumbing", "hourlyRate": 85, "averageRating": 4.8},
    {"vendorId": "P2", "category": "Plumbing", "name": "Pipe Masters", "hourlyRate": 95, "averageRating": 4.5},
    {"vendorId": "P3", "category": "Plumbing", "name": "Leak Busters", "hourlyRate": 75, "averageRating": 3.9},
    {"vendorId": "E1", "category": "Electrical", "name": "Sparky Electric", "hourlyRate": 100, "averageRating": 4.9},
    {"vendorId": "E2", "category": "Electrical", "name": "Volts & Watts", "hourlyRate": 110, "averageRating": 4.7},
    {"vendorId": "E3", "category": "Electrical", "name": "Current Solutions", "hourlyRate": 90, "averageRating": 4.1},
    {"vendorId": "H1", "category": "HVAC", "name": "Cool Breeze HVAC", "hourlyRate": 120, "averageRating": 4.8},
    {"vendorId": "H2", "category": "HVAC", "name": "Arctic Air", "hourlyRate": 130, "averageRating": 4.6},
    {"vendorId": "H3", "category": "HVAC", "name": "HeatWave Solutions", "hourlyRate": 105, "averageRating": 4.2},
    {"vendorId": "G1", "category": "General", "name": "Handy Dan", "hourlyRate": 65, "averageRating": 4.5}
]

for v in vendors:
    dynamodb.put_item(
        TableName="Vendors",
        Item={
            'vendorId': {'S': v['vendorId']},
            'category': {'S': v['category']},
            'name': {'S': v['name']},
            'hourlyRate': {'N': str(v['hourlyRate'])},
            'averageRating': {'N': str(v['averageRating'])}
        }
    )
print("Seeded Vendors")
