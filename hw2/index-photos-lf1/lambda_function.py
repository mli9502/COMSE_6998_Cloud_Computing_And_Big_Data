import json
import urllib.parse
import boto3

from opensearchpy import OpenSearch, RequestsHttpConnection

print('Loading function')

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

s3 = boto3.client('s3')
rekognition_client = boto3.client('rekognition')

def get_labels_from_rekognition(bucket, key, max_labels=10):
    # Code taken from https://docs.aws.amazon.com/rekognition/latest/dg/labels-detect-labels-image.html
    response = rekognition_client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':key}},
     MaxLabels=max_labels,
    )
    print('Detected labels for ' + key)
    # print()
    rtn = []
    for label in response['Labels']:
        # print("Label: " + label['Name'])
        rtn.append(label['Name'])
        # print("Confidence: " + str(label['Confidence']))
        # print("Instances:")
        # for instance in label['Instances']:
        #     print(" Bounding box")
        #     print(" Top: " + str(instance['BoundingBox']['Top']))
        #     print(" Left: " + str(instance['BoundingBox']['Left']))
        #     print(" Width: " + str(instance['BoundingBox']['Width']))
        #     print(" Height: " + str(instance['BoundingBox']['Height']))
        #     print(" Confidence: " + str(instance['Confidence']))
        #     print()
    
        # print("Parents:")
        # for parent in label['Parents']:
        #     print(" " + parent['Name'])
    
        # print("Aliases:")
        # for alias in label['Aliases']:
        #     print(" " + alias['Name'])
    
        # print("Categories:")
        # for category in label['Categories']:
        #     print(" " + category['Name'])
        #     print("----------")
        #     print()
    print('@mli: rekognition labels: ', rtn)
    return rtn 

def get_s3_custom_labels(bucket, key):
    resp = s3.head_object(Bucket=bucket, Key=key)
    if 'Metadata' not in resp:
        return []
    if 'customlabels' not in resp['Metadata']:
        return []
    custom_labels = json.loads(resp['Metadata']['customlabels'])
    print('@mli: custom labels: ', custom_labels)
    return custom_labels

def update_opensearch(bucket, key, all_labels):
    pass

def lambda_handler(event, context):
    print('@mli: index-photos-lf1 called')
    os_query('japanese')
    
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        print('@mli: key: ', key)
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
    
    custom_labels = get_s3_custom_labels(bucket, key)
    rekognition_labels = get_labels_from_rekognition(bucket, key)
    all_labels = set()
    for lbl in custom_labels:
        all_labels.add(lbl)
    for lbl in rekognition_labels:
        all_labels.add(lbl)
    print('@mli: all labels: ', list(all_labels))
