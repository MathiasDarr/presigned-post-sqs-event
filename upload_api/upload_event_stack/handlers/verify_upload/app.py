import boto3
import os
import json


# dynamo_endpoint = os.getenv('dynamo_endpoint')
# if dynamo_endpoint == 'cloud':
#     dynamo_resource = boto3.resource('dynamodb')
# else:
#     dynamo_resource = boto3.resource('dynamodb', endpoint_url=dynamo_endpoint)
#
# TABLE_NAME = os.getenv('user_upload_table')
# table = dynamo_resource.Table(TABLE_NAME)


def lambda_handler(event, context):
    print(event)

