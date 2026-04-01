#!/bin/bash
echo "Initializing LocalStack..."

awslocal s3 mb s3://cstore-media
awslocal s3api put-bucket-cors --bucket cstore-media --cors-configuration file:///etc/localstack/init/ready.d/cors.json

awslocal dynamodb create-table \
    --table-name Users \
    --attribute-definitions AttributeName=username,AttributeType=S \
    --key-schema AttributeName=username,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

awslocal dynamodb create-table \
    --table-name Tickets \
    --attribute-definitions AttributeName=ticketId,AttributeType=S \
    --key-schema AttributeName=ticketId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

awslocal dynamodb create-table \
    --table-name Vendors \
    --attribute-definitions AttributeName=vendorId,AttributeType=S AttributeName=category,AttributeType=S \
    --key-schema AttributeName=vendorId,KeyType=HASH AttributeName=category,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST

awslocal dynamodb create-table \
    --table-name Bids \
    --attribute-definitions AttributeName=bidId,AttributeType=S AttributeName=ticketId,AttributeType=S \
    --key-schema AttributeName=bidId,KeyType=HASH AttributeName=ticketId,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST

awslocal dynamodb create-table \
    --table-name Stores \
    --attribute-definitions AttributeName=storeId,AttributeType=S \
    --key-schema AttributeName=storeId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

     # Add Categories table
     awslocal dynamodb create-table \
          --table-name Categories \
          --attribute-definitions AttributeName=category,AttributeType=S \
          --key-schema AttributeName=category,KeyType=HASH \
          --billing-mode PAY_PER_REQUEST
echo "LocalStack initialization complete. Tables created."
