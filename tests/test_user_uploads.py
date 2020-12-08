import boto3
from botocore.exceptions import ClientError
import requests
import json
import time

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
table = dynamodb.Table('UserUploadTable')


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


def test_dynamo_user_table():
    fileName = 'small.jpg'
    user = 'dakobedbard_gmail'
    userID = "dakobedbard@gmail.com"

    password = '1!ZionTF'

    id_token = authenticate_user(userID, password)

    key = '{}/{}'.format(user, fileName)

    s3 = boto3.resource('s3')
    s3.Object(S3__UPLOAD_BUCKET, key).delete()

    s3_client = boto3.client('s3')
    # assert not verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)

    body = {"filename": fileName, "userID": userID}

    headers = {'Authorization': id_token}


    lambda_presigned_post = requests.post('{}/signedURL'.format(GATEWAY_PROD_URL), json=body, headers=headers)
    assert lambda_presigned_post.status_code == 200

    response = table.get_item(
        Key={
            'user': userID,
            'filename': fileName
        }
    )
    assert 'item' not in response

    response_body = json.loads(lambda_presigned_post.json()['body'])  # ['presigned']
    presigned = response_body['presigned']
    fields = presigned['fields']
    response = {'url': presigned['url'], 'fields': fields}

    with open(fileName, 'rb') as f:
        files = {'file': (fileName, f)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)

    assert http_response.status_code == 204
    assert verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)

    time.sleep(5)
    response = table.get_item(
        Key={
            'user': userID,
            'filename': fileName
        }
    )

    assert 'item' not in response
    item = response['Item']
    assert item['filename'] == fileName
    assert item['user'] == userID

#test_dynamo_user_table()



fileName = 'small.jpg'
user = 'dakobedbard_gmail'
userID = "dakobedbard@gmail.com"

password = '1!ZionTF'

id_token = authenticate_user(userID, password)

key = '{}/{}'.format(user, fileName)

s3 = boto3.resource('s3')
s3.Object(S3__UPLOAD_BUCKET, key).delete()

s3_client = boto3.client('s3')
# assert not verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)

body = {"filename": fileName, "userID": userID}

headers = {'Authorization': id_token}

lambda_presigned_post = requests.post(GATEWAY_PROD_URL, json=body, headers=headers)
assert lambda_presigned_post.status_code == 200

response = table.get_item(
    Key={
        'user': userID,
        'filename': fileName
    }
)
assert 'item' not in response

response_body = json.loads(lambda_presigned_post.json()['body'])  # ['presigned']
presigned = response_body['presigned']
fields = presigned['fields']
response = {'url': presigned['url'], 'fields': fields}

with open(fileName, 'rb') as f:
    files = {'file': (fileName, f)}
    http_response = requests.post(response['url'], data=response['fields'], files=files)

assert http_response.status_code == 204
assert verify_object_exists(s3_client, S3__UPLOAD_BUCKET, key)

time.sleep(5)
response = table.get_item(
    Key={
        'user': userID,
        'filename': fileName
    }
)

assert 'item' not in response
item = response['Item']
assert item['filename'] == fileName
assert item['user'] == userID



id_token = authenticate_user(userID, password)
print(id_token)

key = '{}/{}'.format(user, fileName)


body = {"filename": fileName, "userID": userID}
headers = {'Authorization': id_token}
delete_url = '{}/upload/{}'.format(GATEWAY_PROD_URL,fileName)
print(delete_url)


delete_request_response = requests.delete(delete_url, headers=headers)
print(delete_request_response)