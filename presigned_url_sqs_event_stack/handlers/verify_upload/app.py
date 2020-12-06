import boto3
import os
import json

dynamo_endpoint = os.getenv('dynamo_endpoint')
if dynamo_endpoint == 'cloud':
    dynamo_resource = boto3.resource('dynamodb')
else:
    dynamo_resource = boto3.resource('dynamodb', endpoint_url=dynamo_endpoint)

TABLE_NAME = os.getenv('user_upload_table')

table = dynamo_resource.Table(TABLE_NAME)
region = 'us-west-2'


def insert_user_upload(upload):
    return table.put_item(
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

    username = key.split('/')[0]
    filename = key.split('/')[-1]
    object_url = 'http://{}-{}.amazonaws.com/{}'.format(bucket, region, key)

    print("FILENAME " + filename)
    print("KEY" + key  )

    upload = {'filename': filename, 'fileurl': object_url, 'user': username}
    insert_user_upload(upload)