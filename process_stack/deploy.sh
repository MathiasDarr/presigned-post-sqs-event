#!/bin/bash

if [[ -z $2 ]]
then
  stackname=librosa-ec2-process-stack
else
  stackname=$2
fi

aws cloudformation deploy \
    --template-file template.yaml \
    --stack-name ${stackname} \
    --capabilities CAPABILITY_NAMED_IAM

