import json

from datetime import datetime
import boto3
client = boto3.client('lexv2-runtime', region_name='us-west-2')

def lambda_handler(event, context):
    print('@mli: event: ', event)
    print('@mli: context: ', context)
    print('@mli: user input: ', event['messages'][0]['unstructured']['text'])
    user_input = event['messages'][0]['unstructured']['text']
    
    response = client.recognize_text(
        botId='FM4N3RONQ3',
        botAliasId='TSTALIASID',
        localeId='en_US',
        sessionId="test_session",
        text=user_input)
        
    print('@mli: lex response: ', response)
    
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("@mli: lex text: ", response['messages'][0]['content'])
        return {
                'messages': [
                    {
                        'type': 'unstructured',
                        'unstructured': {
                            'id': 'some-random-id',
                            'text': response['messages'][0]['content'],
                            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'), 
                        }
                    }
                ]
            }
    else:
        return {
                'messages': [
                    {
                        'type': 'unstructured',
                        'unstructured': {
                            'id': 'some-random-id',
                            'text': 'I am not able to understand you',
                            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'), 
                        }
                    }
                ]
            }

