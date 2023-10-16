import json
import boto3

from botocore.exceptions import ClientError
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

# For DynamoDb.
def retrieve_from_dynamo(ids):
    print('@mli: In retrieve_from_dynamo, ids: ', ids)
    client = boto3.client('dynamodb', 'us-east-1')
    rtn = {}
    for id in ids:
        data = client.query(
                TableName='yelp-restaurants',
                IndexName='business_id-index',
                ExpressionAttributeValues={
                ':bus_id': {
                    'S': id,
                },
            },
            KeyConditionExpression='business_id = :bus_id',
        )
        print('@mli: data from dynamo: ', data)
        if 'ResponseMetadata' not in data or 'HTTPStatusCode' not in data['ResponseMetadata'] or data['ResponseMetadata']['HTTPStatusCode'] != 200 or 'Count' not in data or data['Count'] < 1:
            continue
        for item in data['Items']:
            rtn[item['business_id']['S']] = {
                'name': item['name']['S'],
                'address': item['address']['S']
            }
    return rtn
    
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
        WaitTimeSeconds=15,
        VisibilityTimeout=3
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
    print('@mli: rtn len: ', len(rtn))
    return rtn

def process_msg(msg):
    info = json.loads(msg['Body'])
    print('@mli: info: ', info)
    # First get stuff from opensearch.
    os_resp = os_query(info['Cuisine'])
    print('@mli: os_resp: ', os_resp)
    email_content = 'Sorry, did not find any {} restaurants for {} people, at {} {} in {}'.format(info['Cuisine'], info['NumberOfPeople'], info['DiningDate'], info['DiningTime'], info['Location'])
    if len(os_resp) != 0:
        ids = []
        for this_os_resp in os_resp:
            ids.append(this_os_resp['RestaurantID'])
        # Retrieve restaurant from dynamodb.
        additional_info = retrieve_from_dynamo(ids)
        print('@mli: additional_info: ', additional_info)
        if(len(additional_info) == len(ids)):
            email_content = 'Hello! Here are my {} restaurant suggestions for {} people, for {} at {}: \n'.format(info['Cuisine'], info['NumberOfPeople'], info['DiningDate'], info['DiningTime'])
            cnt = 1
            for id in ids:
                if id not in additional_info:
                    continue
                email_content = email_content + '{}: {} at {}\n'.format(cnt, additional_info[id]['name'], additional_info[id]['address'])
                cnt += 1
    print('@mli: email: ', email_content)
    return email_content

def send_email(to_address, content):
    print('@mli: content: ', content)
    SENDER = 'Restaurant Bot <ml4643@columbia.edu>'
    RECIPIENT = to_address
    AWS_REGION = 'us-east-1'
    SUBJECT = 'Restaurant Recommendation'
    BODY_TEXT = str(content)
    BODY_HTML = """<html>
<head></head>
<body>
  <h1>Restaurant Recommendations</h1>
  <p>{}</p>
</body>
</html>
            """.format(str(content))
    CHARSET = "UTF-8"
    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': str(BODY_HTML),
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': str(BODY_TEXT),
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    

def lambda_handler(event, context):
    msgs = []
    print('@mli: start...')
    while True:
        retrieved_msgs = retrieve_and_delete_sqs_msgs()
        msgs.extend(retrieved_msgs)
        print('@mli: len: ', len(retrieved_msgs))
        if len(retrieved_msgs) == 0:
            break
    print('@mli: here...')
    print('@mli: msgs: ', msgs)
    if msgs is None:
        return
    for msg in msgs:
        email_address = json.loads(msg['Body'])['EmailAddress']
        email_content = process_msg(msg)
        print('sending email to {}:\n{}'.format(email_address, email_content))
        send_email(email_address, email_content)
