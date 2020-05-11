import boto3
import argparse
import os
import json
import hashlib
import time

# Handle parameters
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-b", "--bucket", help="S3 bucket to upload the video format: bucketname")
args = vars(ap.parse_args())

if args.get("video", None) is None:
    print('Please provide a video path, use -h for more info.')
    exit()

path, filename = os.path.split(args['video'])

if args.get("bucket", None) is None:
    print('Please provide a S3 bucket to upload the video, use -h for more info.')
    exit()
    
# Upload a video on S3
boto3.Session().resource('s3').Bucket(args['bucket']).Object('video/' + filename).upload_file(args['video'])
print('Video file uploaded to {}'.format(args['bucket']))

# Rekognition request
client = boto3.client('rekognition')
response = client.start_label_detection(
    Video={
        'S3Object': {
            'Bucket': args['bucket'],
            'Name': 'video/' + filename
        }
    },
    ClientRequestToken=hashlib.md5(filename.encode()).hexdigest(),
    MinConfidence=70,
)
job_id = response['JobId']

# Pulling results
in_progress = True
while in_progress:
    response = client.get_label_detection(
        JobId=job_id,
        MaxResults=1000,
        SortBy='TIMESTAMP'
    )
    if response['JobStatus'] == 'SUCCEEDED':
        in_progress = False
        continue
    
    print('Rekognition job in progress')
    time.sleep(20)

# Save response to json
with open('labels/' + filename + '.json', 'w') as f:
    json.dump(response, f)

print('response file saved to {}'.format('labels/' + filename + '.json'))
