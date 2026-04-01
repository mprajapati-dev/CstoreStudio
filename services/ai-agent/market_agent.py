import os
import boto3

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=REGION,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

def check_bids(ticket_id: str):
    table = dynamodb.Table("Bids")
    # Quick scan or query for testing
    res = table.scan()
    bids = [b for b in res.get('Items', []) if b.get('ticketId') == ticket_id]
    return len(bids)
