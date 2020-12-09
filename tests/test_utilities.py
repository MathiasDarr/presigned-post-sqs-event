"""
Utilities for tetsts
"""

from botocore.exceptions import ClientError


def authenticate_user(cidp, user_pool_client, username, password):
    """
    Authenticate a user & return JWT id token
    :param cidp: cognito identity provider client,
    :param user_pool_client: user pool client ID
    :param username:
    :param password:
    :return: JWT identificaiton token
    """
    response = cidp.initiate_auth(AuthFlow='USER_PASSWORD_AUTH',
                                  AuthParameters={'USERNAME': username, 'PASSWORD': password},
                                  ClientId=user_pool_client)
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


def get_user_upload(table, user, filename):
    """
    Returns a user upload item from Dynamo if found
    :param table: User Upload Dynamo Table
    :param user: partition key
    :param filename: range key
    :return: dynamo item
    """
    response = table.get_item(
        Key={
            'user': user,
            'filename': filename
        }
    )
    return response