# Presigned Posts Uploads & SQS Events #

## This repository contains ##
* Lambda function & API developed using SAM & Swagger
    - Lambda function returns a presigned post for uploading to s3
    
    
   
* Vue Front End
    - Authenticated users are able to upload files to S3 using the presigned post url returned by the Lambda 
    - AWS Cognito User Pool for authentication 

* Integration tests
    - test suite utilizes the python requests module to invoke the Lambda function via the API Gateway resouce & method
    - use requests to upload file file using the presigned post url returned by the lambda function 



### Run the integration tests ###




{"filename": "jazz3_solo.wav", "userID": "dakobedbard@gmail.com"}