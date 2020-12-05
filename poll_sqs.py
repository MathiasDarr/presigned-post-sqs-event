import boto3
import json
import logging
import time
import librosa

sqs = boto3.resource('sqs', region_name='us-west-2')
s3 = boto3.client('s3')

queue = sqs.get_queue_by_name(QueueName='LibrosaTransformsQueue')


max_queue_messages = 10
message_bodies = []

while True:
    messages_to_delete = []
    for message in queue.receive_messages(
            MaxNumberOfMessages=max_queue_messages):
        # process message body
        body = json.loads(message.body)
        message_bodies.append(body)
        # add message to delete
        messages_to_delete.append(message)

    # if you don't receive any notifications the
    # messages_to_delete list will be empty
    if len(messages_to_delete) == 0:
        break
    # delete messages to remove them from SQS queue
    # handle any errors
    else:
        delete_response = queue.delete_messages(Entries=messages_to_delete)





while True:
    for message in dakobed_transform_queue.receive_messages():
        try:
            messagebody = message.body
            messagebody = json.loads(messagebody)
            print(messagebody)
            message.delete()
        except Exception as e:
            logging.info(e)
            print(e)

