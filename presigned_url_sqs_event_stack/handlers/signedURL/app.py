import logging
import boto3
from botocore.exceptions import ClientError
import os
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode
import json

BUCKET = os.getenv('UploadBucket')

dynamo_endpoint = os.getenv('dynamo_endpoint')
if dynamo_endpoint == 'cloud':
    dynamo_resource = boto3.resource('dynamodb')
else:
    dynamo_resource = boto3.resource('dynamodb', endpoint_url=dynamo_endpoint)

USER_TABLE_NAME = os.getenv('user_table')
user_table = dynamo_resource.Table('Users')

region = os.getenv('region')
userpool_id = os.getenv('userpool_id')
app_client_id = os.getenv('app_client_id')

print("APP CLIENT ID")
print(app_client_id)

keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)

with urllib.request.urlopen(keys_url) as f:
    response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']


def verify_identification_token(token):
    """
    This method
    :param customerID: email of customer
    :param token: token received from cognito authentication
    :return:
    """
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')

    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')

    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)

    if time.time() > claims['exp']:
        print('Token is expired')
        return False

    if claims['aud'] != app_client_id:  # or claims['email'] != customerID:
        print('Token was not issued for this audience')
        return False
    return claims['email']


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


def get_user_upload_directory(user_email):
    """
    This function returns the folder/directory that their uploads are saved.
    :param user_email:
    :return:
    """
    response = user_table.get_item(
        Key={
            'email': user_email,
        }
    )
    return response['Item']['upload_directory']


def lambda_handler(event, context):
    if 'Authorization' not in event['params']['header'] or not verify_identification_token(
            event['params']['header']['Authorization']):
        return {"statusCode": 403, "body": json.dumps({
            "errorMessage": "failure"
        }), 'headers': {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}}

    userID = verify_identification_token(event['params']['header']['Authorization'])

    user_upload_directory = get_user_upload_directory(userID)
    filename = event['body']['filename']
    presigned = create_presigned_post(BUCKET, '{}/{}'.format(user_upload_directory, filename))

    presigned['fields']['bucket'] = BUCKET

    response = {"statusCode": 200, "body": json.dumps({
        "presigned": presigned
    }), 'headers': {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}}
    return response

    # response = {"statusCode": 200, "body": json.dumps({
    #     "presigned": "hello"
    # }), 'headers': {"Access-Control-Allow-Origin": "*", "Content-Type":"application/json"}}
    #
    # return response

    # # print("header")
    # # print((event['params']['header']['Authorization'])
    # if 'Authorization' not in event['params']['header'] or not verify_identification_token(
    #         event['params']['header']['Authorization']):
    #     return {"statusCode": 403, "body": json.dumps({
    #         "errorMessage": "failure"
    #     }), 'headers': {"Access-Control-Allow-Origin": "*", "Content-Type":"application/json"}}
    #
    # userID = verify_identification_token(event['params']['header']['Authorization'])
    #
    # user_upload_directory = get_user_upload_directory(userID)
    # filename = event['body']['filename']
    # presigned = create_presigned_post(BUCKET, '{}/{}'.format(user_upload_directory, filename))
    #
    # presigned['fields']['bucket'] = BUCKET
    #
    # response = {"statusCode": 200, "body": json.dumps({
    #     "presigned": presigned
    # }), 'headers': {"Access-Control-Allow-Origin": "*"}, "Content-Type":"application/json"}
    #
    # return response


# #set($inputRoot = $input.path('$.errorMessage'))
# $inputRoot
#
#
# #set($inputRoot = $input.path('$')) {
#     "error": "$inputRoot.errorMessage"
# }


    # print("header")
    # print((event['params']['header']['Authorization'])
    # if 'Authorization' not in event['params']['header'] or not verify_identification_token(
    #         event['params']['header']['Authorization']):
    #     return {"statusCode": 403, "body": json.dumps({
    #         "errorMessage": "failure"
    #     }), 'headers': {"Access-Control-Allow-Origin": "*", "Content-Type":"application/json"}}
    #
    # userID = verify_identification_token(event['params']['header']['Authorization'])
    #
    # user_upload_directory = get_user_upload_directory(userID)
    # filename = event['body']['filename']
    # presigned = create_presigned_post(BUCKET, '{}/{}'.format(user_upload_directory, filename))
    #
    # presigned['fields']['bucket'] = BUCKET
    #
    # response = {"statusCode": 200, "body": json.dumps({
    #     "presigned": presigned
    # }), 'headers': {"Access-Control-Allow-Origin": "*", "Content-Type":"application/json"}}