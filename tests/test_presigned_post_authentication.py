"""
This file contains tests of the presigned URL & Authentication/Authorization

"""
import boto3
from botocore.exceptions import ClientError
import requests

cf_client = boto3.client('cloudformation')

userpool_stack = 'upload-api-userpool-stack'
response = cf_client.describe_stacks(StackName=userpool_stack)
outputs = response["Stacks"][0]["Outputs"]

USER_POOL = ''
USER_POOL_CLIENT = ''
for output in outputs:
    keyName = output["OutputKey"]
    if keyName == "UserPool":
        USER_POOL = output["OutputValue"]
    elif keyName == "UserPoolClient":
        USER_POOL_CLIENT = (output["OutputValue"])

upload_api_stack = 'serverles-transcriptions-api-stack'
response = cf_client.describe_stacks(StackName=upload_api_stack)
outputs = response["Stacks"][0]["Outputs"]

S3__UPLOAD_BUCKET = ''
GATEWAY_PROD_URL = ''
for output in outputs:
    keyName = output["OutputKey"]
    if keyName == "S3UploadBucket":
        S3__UPLOAD_BUCKET = output["OutputValue"]
    elif keyName == "UploadApi":
        GATEWAY_PROD_URL = (output["OutputValue"])

cidp = boto3.client('cognito-idp')


def authenticate_user(username, password):
    response = cidp.initiate_auth(AuthFlow='USER_PASSWORD_AUTH',
                                  AuthParameters={'USERNAME': username, 'PASSWORD': password},
                                  ClientId=USER_POOL_CLIENT)
    return response['AuthenticationResult']['IdToken']


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


def test_unauthenticated_upload_file():
    """
    Verify that requests without the Authorization header will return 403
    :return:
    """
    fileName = 'jazz3_solo.wav'
    user = 'dakobedbard'
    userID = "dakobedbard@gmail.com"

    key = '{}/{}'.format(user, fileName)

    s3 = boto3.resource('s3')
    s3.Object(S3__UPLOAD_BUCKET, key).delete()

    s3_client = boto3.client('s3')
    assert not verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)

    body = {"filename": fileName, "userID": userID}

    lambda_presigned_post = requests.post(GATEWAY_PROD_URL, json=body)
    assert lambda_presigned_post.status_code == 403
    assert not verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)


def test_authenticated_upload_file():
    """
    Test that authenticated user is able to upload to s3 with presigned post
    :return: requests.response
    """
    fileName = 'jazz3_solo.wav'
    user = 'dakobedbard'
    userID = "dakobedbard@gmail.com"

    password = '1!ZionTF'

    id_token = authenticate_user(userID, password)

    key = '{}/{}'.format(user, fileName)

    s3 = boto3.resource('s3')
    s3.Object(S3__UPLOAD_BUCKET, key).delete()

    s3_client = boto3.client('s3')
    assert not verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)

    body = {"filename": fileName, "userID": userID}

    headers = {'Authorization': id_token}

    lambda_presigned_post = requests.post(GATEWAY_PROD_URL, json=body, headers=headers)
    assert lambda_presigned_post.status_code == 200

    response_body = lambda_presigned_post.json()['presigned']
    fields = response_body['fields']
    response = {'url': response_body['url'], 'fields': fields}

    with open(fileName, 'rb') as f:
        files = {'file': (fileName, f)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)

    assert http_response.status_code == 204

    assert verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)
