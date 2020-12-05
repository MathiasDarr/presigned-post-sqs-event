import boto3


def authenticate_user(username, password):
    response = cidp.initiate_auth(AuthFlow='USER_PASSWORD_AUTH',
                                  AuthParameters={'USERNAME': username, 'PASSWORD': password},
                                  ClientId=user_pool_client)

    return response['AuthenticationResult']['IdToken']

cf_client = boto3.client('cloudformation')
stackname = 'upload-api-userpool-stack'
response = cf_client.describe_stacks(StackName=stackname)
outputs = response["Stacks"][0]["Outputs"]

user_pool = ''
user_pool_client = ''
for output in outputs:
    keyName = output["OutputKey"]
    if keyName == "UserPool":
        user_pool = output["OutputValue"]
    elif keyName == "UserPoolClient":
        user_pool_client = (output["OutputValue"])

cidp = boto3.client('cognito-idp')

# This is less secure, but simpler
user = 'dakobedbard@gmail.com'
password = '1!ZionTF'

id_token = authenticate_user(user, password)


