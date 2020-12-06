import logging
import boto3
from botocore.exceptions import ClientError
import os
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode
import json

region = os.getenv('region')
userpool_id = os.getenv('userpool_id')
app_client_id = os.getenv('app_client_id')
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)

with urllib.request.urlopen(keys_url) as f:
    response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']

BUCKET = os.getenv('UploadBucket')


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


def lambda_handler(event, context):
    if 'Authorization' not in event['headers'] or not verify_identification_token(event['headers']['Authorization']):
        return {"statusCode": 403, "body": json.dumps({
            "error": "Token has expired or been issued to different user."
        }), 'headers': {"Access-Control-Allow-Origin": "*"}}

    userID = verify_identification_token(event['headers']['Authorization'])
    user = userID.split('@')[0]

    body = json.loads(event['body'])
    filename = body['filename']

    presigned = create_presigned_post(BUCKET, '{}/{}'.format(user, filename))

    presigned['fields']['bucket'] = BUCKET
    response = {"statusCode": 200, "body": json.dumps({
        "presigned": presigned
    }), 'headers': {"Access-Control-Allow-Origin": "*"}}

    return response
