#!/bin/bash

# IMPORTANT: Bucket names must be unique for all AWS users.
BUCKET="mir-cloudformation-artifacts"

if [[ -z $2 ]]
then
  stackname=upload-api-userpool-stack
else
  stackname=$2
fi

# Uploads files to S3 bucket and creates CloudFormation template
aws cloudformation package \
    --template-file template.yaml \
    --s3-bucket $BUCKET \
    --output-template-file package.yaml

aws cloudformation deploy \
      --template-file package.yaml \
      --stack-name ${stackname} \
      --capabilities CAPABILITY_NAMED_IAM
