import json
import boto3

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# For opensearch.
REGION = 'us-east-2'
HOST = 'search-restaurants-h2lvh4wxokm3335ppbygg4ks3q.us-east-2.es.amazonaws.com'
INDEX = 'restaurants'
def os_query(term):
    q = {'size': 5, 'query': {'multi_match': {'query': term}}}

    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=os_get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)

    res = client.search(index=INDEX, body=q)
    print(res)

    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_source'])

    return results

def os_get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)

client = boto3.client('dynamodb', 'us-east-1')
# setup the SQS Service
sqs = boto3.client('sqs', 'us-east-2')

def retrieve_and_delete_sqs_msgs():
    queue_url = 'https://sqs.us-east-2.amazonaws.com/416716646862/MyQueue'

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=10,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=20
    )
    if 'Messages' not in response:
        return []
    print("@mli: resp: ", response)
    print("@mli: message number from sqs: ", len(response['Messages']))
    rtn = []
    for message in response['Messages']:
        print("@mli: message from sqs: ", message)
        rtn.append(message)
        # Delete received message from queue
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message['ReceiptHandle']
        )
    return rtn

def process_msg(msg):
    info = json.loads(msg['Body'])
    print('@mli: info: ', info)
    # First get stuff from opensearch.
    os_resp = os_query(info['Cuisine'])
    print(os_resp)
    

def lambda_handler(event, context):
    while True:
        msgs = retrieve_and_delete_sqs_msgs()
        if len(msgs) == 0:
            break
    for msg in msgs:
        process_msg(msg)
    # queue_url = 'https://sqs.us-east-2.amazonaws.com/416716646862/MyQueue'

    # # Receive message from SQS queue
    # response = sqs.receive_message(
    #     QueueUrl=queue_url,
    #     AttributeNames=[
    #         'All'
    #     ],
    #     MaxNumberOfMessages=10,
    #     MessageAttributeNames=[
    #         'All'
    #     ],
    #     VisibilityTimeout=0,
    #     WaitTimeSeconds=20
    # )
    
    # print("@mli: message number from sqs: ", len(response['Messages']))
    # for message in response['Messages']:
    #     print("@mli: message from sqs: ", message)
    #     # Delete received message from queue
    #     sqs.delete_message(
    #         QueueUrl=queue_url,
    #         ReceiptHandle=message['ReceiptHandle']
    #     )
    #     print('Received and deleted message: %s' % message)
    
    # message = response['Messages'][0]
    # receipt_handle = message['ReceiptHandle']

    

    
# # Get a record from dynamo db
# def lambda_handler(event, context):
#     data = client.query(
#         TableName='yelp-restaurants',
#         IndexName='business_id-index',
#         ExpressionAttributeValues={
#         ':bus_id': {
#             'S': 'aWkekCYI9zNA6xDwYEtYpg',
#         },
#     },
#     KeyConditionExpression='business_id = :bus_id',
#     )
#     response = {
#         'statusCode': 200,
#         'body': json.dumps(data),
#         'headers': {
#             'Content-Type': 'application/json',
#             'Access-Control-Allow-Origin': '*'
#         }
#     }
#     print(response)
  
# def pp(dict):
#     print(json.dumps(dict, indent=2))
  
