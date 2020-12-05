import json
import boto3
import base64
import uuid
# import requests

sqs = boto3.resource('sqs', region_name='us-west-2')
queue = 'https://sqs.us-west-2.amazonaws.com/710339184759/InitiateTransformsQueue'

s3 = boto3.client('s3')
BUCKET = 'dakobed-transcriptions-service'


dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('UserUploads')


def lambda_handler(event, context):
    userID = event['pathParams']['userid']
    title = event['queryParams']['title']

    user = userID.split('@')[0]
    file_path = '{}/{}.wav'.format(user, title.lower().replace(' ', '-'))

    file_content = base64.b64decode(event['content'])
    s3_response = ''

    try:
        s3_response = s3.put_object(Bucket='dakobed-transcriptions-service', Key=file_path, Body=file_content)
        table.put_item(Item={"userID": userID, "title": title, "path": file_path})
        response = queue.send_message(MessageBody=json.dumps({'bucket': BUCKET, 'user': user, 'path': file_path}))
    except Exception as e:
        s3_response = str(e)
        print(e)

    return {
        'statusCode': 200,
        'body': user
    }
