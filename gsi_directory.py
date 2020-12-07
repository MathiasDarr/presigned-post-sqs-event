import boto3
from boto3.dynamodb.conditions import Key

dynamo_resource = boto3.resource('dynamodb')

table = dynamo_resource.Table('Users')
upload_directory = 'dakobedbard_gmail'
response = table.query(
    IndexName='upload_directory_index',
    KeyConditionExpression=Key('upload_directory').eq(upload_directory)
)

email = response['Items'][0]['email']