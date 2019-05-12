import json
import boto3
import requests
from requests_aws4auth import AWS4Auth

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://vpc-newphotos-w2hwdiynb7nywf7gx3vjaxyabq.us-east-1.es.amazonaws.com' # ES domain
index = 'photos'
type = 'lambda'
url = host + '/' + index + '/' + type
print(url)

headers = {"Content-Type": "application/json"}


def detect_labels(bucket, key, max_labels=10, min_confidence=90, region="us-east-1"):
    rekognition = boto3.client("rekognition", region)
    response = rekognition.detect_labels(
        Image={
            "S3Object": {
                "Bucket": bucket,
                "Name": key,
            }
        },
        MaxLabels=max_labels,
        MinConfidence=min_confidence,
    )
    return response['Labels']


def lambda_handler(event, context):
    for record in event['Records']:
        BUCKET = record['s3']['bucket']['name']
        KEY = record['s3']['object']['key']
        timestamp = record['eventTime']

    result_labels = []
    for label in detect_labels(BUCKET, KEY):
        result_labels.append(label['Name'])
    result = {"objectKey": KEY, "bucket": BUCKET, "createdTimestamp": timestamp, "labels": result_labels}
    print(result)
    r = requests.post(url, auth=awsauth, json=result, headers=headers)
    print('read to es')
    r.raise_for_status()
    print(r)

    return {'statusCode': 200, 'body': json.dumps('Hello from Lambda!')}