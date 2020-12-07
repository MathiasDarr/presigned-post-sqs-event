import boto3
import os
from boto3.dynamodb.conditions import Key
import json

dynamo_endpoint = os.getenv('dynamo_endpoint')
if dynamo_endpoint == 'cloud':
    dynamo_resource = boto3.resource('dynamodb')
else:
    dynamo_resource = boto3.resource('dynamodb', endpoint_url=dynamo_endpoint)

UPLOAD_TABLE_NAME = os.getenv('user_upload_table')
# USER_TABLE_NAME = os.getenv('user_table')
# USER_TABLE_NAME ='Users'
upload_table = dynamo_resource.Table(UPLOAD_TABLE_NAME)
user_table = dynamo_resource.Table('Users')

region = 'us-west-2'


def get_user_email_from_directory(upload_directory):
    """
    Return the email address give the directory at which the file has been uploaded.
    :param upload_directory:
    :return:
    """
    response = user_table.query(
        IndexName='upload_directory_index',
        KeyConditionExpression=Key('upload_directory').eq(upload_directory)
    )
    return response['Items'][0]['email']


def insert_user_upload(upload):
    return upload_table.put_item(
        Item={
            'user': upload['user'],
            'filename': upload['filename'],
            'fileurl': upload['fileurl'],
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
    records = event['Records']
    r1 = records[0]
    s3_record = r1['s3']
    bucket = s3_record['bucket']['name']
    key = s3_record['object']['key']

    upload_directory = key.split('/')[0]
    userid = get_user_email_from_directory(upload_directory)

    filename = key.split('/')[-1]
    object_url = 'http://{}-{}.amazonaws.com/{}'.format(bucket, region, key)

    upload = {'filename': filename, 'fileurl': object_url, 'user': userid}
    insert_user_upload(upload)
