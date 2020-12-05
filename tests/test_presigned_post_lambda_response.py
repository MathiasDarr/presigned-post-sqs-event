"""
This file contains tests of the presigned post url.
"""
import logging
import boto3
from botocore.exceptions import ClientError
import requests

LAMBDA_PRESIGNED_POST_URL = 'https://cr5nlv4c58.execute-api.us-west-2.amazonaws.com/Prod/signedURL'
BUCKET = 'dakobed-sqs-transform-bucket'


def create_presigned_post(bucket_name, object_name, fields=None, conditions=None, expiration=3600):
    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
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


def upload_file_with_presigned_url(filename, key, bucket):
    """
    This function uses the presigned url returned and uploads to s3.
    :return: requests.response
    """

    response = create_presigned_post(bucket, key)

    with open(filename, 'rb') as f:
        files = {'file': (key, f)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)
    return http_response


def verify_object_exists(client, bucket, key):
    """

    :param client: boto3 s3 client
    :param bucket: s3 bucket
    :param key:
    :return: boolean, true if the object 'key' is found in the bucket false other wise
    """
    found = False
    try:
        client.head_object(Bucket=bucket, Key=key)
        found = True
    except ClientError:
        pass
    return found


def test_upload_presigned_post():
    fileName = 'jazz3_solo.wav'
    user = 'dakobedbard'

    key = '{}/{}'.format(user, fileName)

    s3 = boto3.resource('s3')
    s3.Object(BUCKET, key).delete()

    s3_client = boto3.client('s3')
    assert not verify_object_exists(s3_client, BUCKET, key)

    http_response = upload_file_with_presigned_url(fileName, key, BUCKET)
    assert http_response.status_code == 204

    assert verify_object_exists(s3_client, BUCKET, key)


def test_upload_file_with_presigned_url_received_from_lambda():
    """
    This function uses the presigned url returned and uploads to s3.
    :return: requests.response
    """
    fileName = 'jazz3_solo.wav'
    user = 'dakobedbard'
    userID = "dakobedbard@gmail.com"
    key = '{}/{}'.format(user, fileName)

    s3 = boto3.resource('s3')
    s3.Object(BUCKET, key).delete()

    s3_client = boto3.client('s3')
    assert not verify_object_exists(s3_client, BUCKET, key)

    body = {"filename": fileName, "userID": userID}

    lambda_presigned_post = requests.post(LAMBDA_PRESIGNED_POST_URL, json=body)
    assert lambda_presigned_post.status_code == 200

    response_body = lambda_presigned_post.json()['presigned']
    fields = response_body['fields']
    response = {'url': response_body['url'], 'fields': fields}

    with open(fileName, 'rb') as f:
        files = {'file': (fileName, f)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)

    assert http_response.status_code == 204

    assert verify_object_exists(s3_client, BUCKET, key)

