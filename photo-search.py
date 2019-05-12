import boto3
import json
import requests
from requests_aws4auth import AWS4Auth

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://vpc-newphotos-w2hwdiynb7nywf7gx3vjaxyabq.us-east-1.es.amazonaws.com'
index = 'photos'
url = host + '/' + index + '/_search'

lex_client = boto3.client('lex-runtime')


def lambda_handler(event, context):
    print('event: ' + str(event))
    # don't forget to change!
    inputText = event['queryStringParameters']['q']


    response_lex = lex_client.post_text(
        botAlias="$LATEST",
        botName="SearchPhotos",
        userId='USER1',
        inputText=inputText
    )

    print(response_lex)
    key1 = response_lex['slots']['typea']
    if key1 is not None:
        keywords = key1
    key2 = response_lex['slots']['typeb']
    if key2 is not None and key1 is None:
        keywords = key2
    print(key1)
    print(key2)
    if key1 is not None and key2 is not None:
        keywords = key1 + ',' + key2
    print("keys:", keywords)
    query = {"size": 25, "query": {"multi_match": {"query": keywords}}}
    headers = {"Content-Type": "application/json"}

    r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
    print(r.text)

    response = {"statusCode": 200, "headers": {
        "Access-Control-Allow-Origin": '*'
    }, "isBase64Encoded": False, 'body': r.text}

    return response

