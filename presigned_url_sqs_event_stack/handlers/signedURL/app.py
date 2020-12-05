import logging
import boto3
from botocore.exceptions import ClientError
import json
import os

BUCKET = os.getenv('UploadBucket')


def create_presigned_post(bucket_name, object_name, fields=None, conditions=None, expiration=3600):
    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3', region_name='us-west-2')
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


def lambda_handler(event, context):
    body = json.loads(event['body'])
    user = body['userID']
    filename = body['filename']
    user = user.split('@')[0]
    presigned = create_presigned_post(BUCKET, '{}/{}'.format(user, filename))
    presigned['fields']['bucket'] = BUCKET
    response = {"statusCode": 200, "body": json.dumps({
        "presigned": presigned
    }), 'headers': {"Access-Control-Allow-Origin": "*"}}
    return response

