import boto3
import os
import json

dynamo_endpoint = os.getenv('dynamo_endpoint')
if dynamo_endpoint == 'cloud':
    dynamo_resource = boto3.resource('dynamodb')
else:
    dynamo_resource = boto3.resource('dynamodb', endpoint_url=dynamo_endpoint)

TABLE_NAME = os.getenv('user_table')

table = dynamo_resource.Table(TABLE_NAME)
region = 'us-west-2'


def insert_user(user):
    return table.put_item(
        Item={
            'email': user['email'],
            'upload_directory': user['upload_directory']
        }
    )

def lambda_handler(event, context):
    """
    This lambda function is triggered by an S3 object creation notification.  This function extracts the fileurl, filename
    & determines the userid from the event & creates an entry in the dynamo table.

    :param event:
    :param context:
    :return:
    """
    email = event['request']['userAttributes']['email']
    prefix = email.split('@')[0]
    suffix = email.split('@')[1].split('.')[0]
    upload_directory = '{}_{}'.format(prefix, suffix)
    user = {'email': email, 'upload_directory': upload_directory}
    insert_user(user)
    return event

