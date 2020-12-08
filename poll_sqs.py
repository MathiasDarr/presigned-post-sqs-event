import boto3
import json
import logging
import time
import librosa
import numpy as np

s3 = boto3.client('s3')
BUCKET = 'dakobed-sqs-transform-bucket'

sqs = boto3.resource('sqs', region_name='us-west-2')
queue = sqs.get_queue_by_name(QueueName='LibrosaTransformsQueue')

dynamodb = boto3.resource('dynamodb')

upload_table = dynamodb.Table('UserUploadTable')


def add_transform_path_to_user_upload_item(user, filename, transform_key):
    response = upload_table.update_item(
        Key={
            'user': user,
            'filename': filename
        },
        UpdateExpression="set transform_key=:t_key",
        ExpressionAttributeValues={
            ':t_key': transform_key,
        },
        ReturnValues="UPDATED_NEW"
    )


# user = 'dakobedbard@gmail.com'
# filename = 'jazz3_solo.wav'
# transform_key = 'tkey'
#
# add_transform_path_to_user_upload_item(user, filename, transform_key)


def process_message(message):
    messagebody = json.loads(message.body)

    bucket = messagebody['bucket']
    key = messagebody['key']
    user = messagebody['user']
    filename = messagebody['filename']
    directory = key.split('/')[0]

    audio_file = ''.join([directory, filename])

    transform_file = '{}_cqt.npy'.format(audio_file.split('.')[0])

    with open(audio_file, 'wb') as f:
        s3.download_fileobj(bucket, key, f)

    y, sr = librosa.load(audio_file)
    cqt_raw = librosa.core.cqt(y, sr=sr, n_bins=144, bins_per_octave=36, fmin=librosa.note_to_hz('C2'), norm=1)
    np.save(transform_file, arr=cqt_raw)

    s3.upload_file(Filename=transform_file, Bucket=BUCKET, Key=transform_file)
    add_transform_path_to_user_upload_item(user, filename, transform_file)

while True:
    for message in queue.receive_messages():
        try:
            process_message(message)
            message.delete()
        except Exception as e:
            logging.info(e)
            print(e)
        time.sleep(5)