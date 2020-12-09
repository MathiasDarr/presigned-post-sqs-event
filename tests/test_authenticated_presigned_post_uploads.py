"""
API tests for uplading files to S3 using presigned post urls received from lambda.  Setup code uses cloud
formation describe stacks for finding the user pool, user pool client IDs, as well as the s3 bucket & other outputs
of the cloudformation stacks.

"""

import boto3
import requests
import json
import time
from test_utilities import authenticate_user, verify_object_exists, get_user_upload


cf_client = boto3.client('cloudformation')

userpool_stack = 'upload-user-stack'
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

upload_api_stack = 'upload-api-stack'
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

print(USER_POOL_CLIENT)
print(USER_POOL)
print(GATEWAY_PROD_URL)

cidp = boto3.client('cognito-idp')

dynamodb = boto3.resource('dynamodb', region_name="us-west-2")
user_upload_table = dynamodb.Table('UserUploadTable')

s3_client = boto3.client('s3')


def test_unauthenticated_upload_file():
    """
    Verify that requests without the Authorization header will return 403
    :return:
    """
    user = 'dakobedbard'
    userID = "dakobedbard@gmail.com"
    fileName = 'jazz3_solo.wav'
    key = '{}/{}'.format(user, fileName)

    # Assert that object does not exist initially
    s3_client.delete_object(Bucket=S3__UPLOAD_BUCKET, Key=key)
    assert not verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)

    # Make a request for presigned post URL without providing Authorization header
    body = {"filename": fileName, "userID": userID}
    lambda_presigned_post = requests.post(GATEWAY_PROD_URL, json=body)
    get_item_response = get_user_upload(user_upload_table, userID, fileName)

    # Assert 403 and that item does not exist in S3
    assert lambda_presigned_post.status_code == 403
    assert not verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)
    assert 'item' not in get_item_response


def test_authenticated_user_upload():
    """
    Authenticated user uploads file
    """
    # Authenticate User
    userID = "dakobedbard@gmail.com"
    password = '1!ZionTF'
    id_token = authenticate_user(cidp, USER_POOL_CLIENT, userID, password)

    fileName = 'jazz3_solo.wav'
    directory = 'dakobedbard_gmail'
    key = '{}/{}'.format(directory, fileName)

    # Assert that file does not exist initially
    # s3.Object(S3__UPLOAD_BUCKET, key).delete()
    s3_client.delete_object(Bucket=S3__UPLOAD_BUCKET, Key=key)
    assert not verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)

    # Make request to receive a presigned post url, assert that response is 200
    body = {"filename": fileName, "userID": userID}
    headers = {'Authorization': id_token}
    presigned_url = '{}/signedURL'.format(GATEWAY_PROD_URL)
    lambda_presigned_post = requests.post(presigned_url, json=body, headers=headers)
    assert lambda_presigned_post.status_code == 200

    # Assert item does not initially exist in database
    get_item_response = get_user_upload(user_upload_table, userID, fileName)
    assert 'item' not in get_item_response

    # Make a post request using the presigned URL
    response_body = json.loads(lambda_presigned_post.json()['body'])
    presigned = response_body['presigned']
    fields = presigned['fields']
    response = {'url': presigned['url'], 'fields': fields}

    with open(fileName, 'rb') as f:
        files = {'file': (fileName, f)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)

    assert http_response.status_code == 204
    assert verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)

    # Time for changes to propagate
    time.sleep(3)

    get_item_response = get_user_upload(user_upload_table, userID, fileName)
    # Assert 'item' not in get_item_response
    item = get_item_response['Item']
    assert item['filename'] == fileName
    assert item['user'] == userID


def test_authenticated_user_upload_and_deletes():
    """
    Authenticated user uploads file and then deletes it]
    """
    # Authenticate User
    userID = "dakobedbard@gmail.com"
    password = '1!ZionTF'
    id_token = authenticate_user(cidp, USER_POOL_CLIENT, userID, password)

    fileName = 'jazz3_solo.wav'
    directory = 'dakobedbard_gmail'
    key = '{}/{}'.format(directory, fileName)

    # Assert that file does not exist initially
    # s3.Object(S3__UPLOAD_BUCKET, key).delete()
    s3_client.delete_object(Bucket=S3__UPLOAD_BUCKET, Key=key)
    assert not verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)

    # Make request to receive a presigned post url, assert that response is 200
    body = {"filename": fileName, "userID": userID}
    headers = {'Authorization': id_token}
    presigned_url = '{}/signedURL'.format(GATEWAY_PROD_URL)
    lambda_presigned_post = requests.post(presigned_url, json=body, headers=headers)
    assert lambda_presigned_post.status_code == 200

    # Assert item does not initially exist in database
    get_item_response = get_user_upload(user_upload_table, userID, fileName)
    assert 'item' not in get_item_response

    # Make a post request using the presigned URL
    response_body = json.loads(lambda_presigned_post.json()['body'])
    presigned = response_body['presigned']
    fields = presigned['fields']
    response = {'url': presigned['url'], 'fields': fields}

    with open(fileName, 'rb') as f:
        files = {'file': (fileName, f)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)

    assert http_response.status_code == 204
    assert verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)

    # Time for changes to propagate
    time.sleep(3)

    get_item_response = get_user_upload(user_upload_table, userID, fileName)
    # Assert 'item' not in get_item_response
    item = get_item_response['Item']
    assert item['filename'] == fileName
    assert item['user'] == userID

    # Make request to delete route
    key = '{}/{}'.format(directory, fileName)
    headers = {'Authorization': id_token}
    delete_url = '{}/upload/{}'.format(GATEWAY_PROD_URL, fileName)
    requests.delete(delete_url, headers=headers)
    time.sleep(3)

    # Assert that the item no longer exists in s3 or as an entry in dynamoDB
    get_item_response = get_user_upload(user_upload_table, userID, fileName)
    assert 'item' not in get_item_response
    assert not verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)
