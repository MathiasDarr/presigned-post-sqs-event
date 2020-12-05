import logging
import boto3
from botocore.exceptions import ClientError
import json
import os
import requests

BUCKET = 'dakobed-sqs-transform-bucket'

def create_presigned_post(bucket_name, object_name, fields=None, conditions=None, expiration=3600):
    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    s3_resource= boto3.resource('s3')
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response
fileName = 'dakobedbard/jazz3_solo.wav'
response = create_presigned_post(BUCKET, fileName)

fields = response['fields']
access_key = fields['AWSAccessKeyId']

with open(fileName, 'rb') as f:
    files = {'file': (fileName, f)}
    http_response = requests.post(response['url'], data=response['fields'], files=files)

req = http_response.request