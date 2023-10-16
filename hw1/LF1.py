import json
import boto3

from datetime import datetime
from zoneinfo import ZoneInfo

# This is `LF1` in the assignment.

def buildCloseResponse(request, message):
    request['sessionState']['intent']['state'] = 'Fulfilled'
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'Close'
            },
            'intent': request['sessionState']['intent']
        },
        'messages': [{
            'contentType': 'PlainText',
            'content': message
        }],
        'sessionId': request['sessionId'],
        'requestAttributes': request['requestAttributes'] if 'requestAttributes' in request else None
    }

def buildElicitIntentResponse(request, message):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            }
        },
        'messages': [ {
            'contentType': 'PlainText',
            'content': message
        } ],
        'requestAttributes': request['requestAttributes'] if 'requestAttributes' in request else None
    }
 
def buildElicitSlotResponse(request, slot, message):
    request['sessionState']['intent']['state'] = 'InProgress'
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitSlot',
                'slotToElicit': slot
            },
            'intent': request['sessionState']['intent']
        },
        'messages': [ {
            'contentType': 'PlainText',
            'content': message
        } ],
        'requestAttributes': request['requestAttributes'] if 'requestAttributes' in request else None
    }

def handleGreeting(request):
    print('@mli: Got GreetingIntent: ', request)
    return buildElicitIntentResponse(request, 'Hi there, how can I help?')

def handleThankYou(request):
    print('@mli: Got ThankYouIntent: ', request)
    return buildCloseResponse(request, 'You are welcome. Bye.')

def verifySlot(slot, slots):
    if slot == 'DiningDate':
        provided_date = datetime.strptime(slots[slot]['value']['interpretedValue'], '%Y-%m-%d')
        today = datetime.strptime(datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%d'), '%Y-%m-%d')
        print('provided_date: {}, today: {}'.format(provided_date, today))
        if provided_date < today:
            return False
    elif slot == 'DiningTime':
        provided_dt = datetime.strptime('{} {}'.format(slots['DiningDate']['value']['interpretedValue'], slots[slot]['value']['interpretedValue']), '%Y-%m-%d %H:%M')
        now = datetime.strptime(datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
        print('provided_dt: {}, today: {}'.format(provided_dt, now))
        if provided_dt <= now:
            return False
    elif slot == 'NumberOfPeople':
        if int(slots[slot]['value']['interpretedValue']) <= 0:
            return False
    return True

# TODO: @mli: proposedNextState->prompt->attempt: Initial/Retry can probably be used to see whether we have tried to get this slot before, to better customize response.
def handleDiningSuggestions(request):
    slot_key_prompt_order = ['Location', 'Cuisine', 'DiningDate', 'DiningTime', 'NumberOfPeople', 'EmailAddress']
    slot_key_to_prompt = {
        'Location': 'What city or city area are you looking to dine in?',
        'Cuisine': 'What cuisine would you like to try?',
        'DiningDate': 'What date?',
        'DiningTime': 'What time?',
        'NumberOfPeople': 'How many people are in your party?',
        'EmailAddress': 'I need your email address so I can send you my findings.'
    }
    print('@mli: Got DiningSuggestionsIntent: ', request)
    slots = request['sessionState']['intent']['slots']
    last_slot = None
    last_slot_value = None
    for slot in slot_key_prompt_order:
        if slots[slot] is None:
            confirm_msg = ''
            if last_slot is not None:
                confirm_msg = 'Okay, got {} for {}, next question, '.format(last_slot, last_slot_value)
            return buildElicitSlotResponse(request, slot, '{}{}'.format(confirm_msg, slot_key_to_prompt[slot]))

        if 'interpretedValue' in slots[slot]['value'] and slots[slot]['value']['interpretedValue'] is not None and verifySlot(slot, slots):
            print('@mli: Got value for slot: {} -> {}'.format(slot, slots[slot]['value']['interpretedValue']))
            last_slot = slot
            last_slot_value = slots[slot]['value']['interpretedValue']
            continue
        else:
            print('@mli: Got wrong value for slot: {} -> {}'.format(slot, slots[slot]['value']['originalValue']))
            return buildElicitSlotResponse(request, slot, 'Got invalid value: {}. Please try again. {}'.format(slots[slot]['value']['originalValue'], slot_key_to_prompt[slot]))
    print('Got value for all slots!')
    slot_values = {}
    for slot in slot_key_prompt_order:
        slot_values[slot] = slots[slot]['value']['interpretedValue']
    print('@mli: slot_values: ', slot_values)
    sqs = boto3.client('sqs', 'us-east-2')
    resp = sqs.send_message(QueueUrl='https://sqs.us-east-2.amazonaws.com/416716646862/MyQueue', MessageBody=json.dumps(slot_values))
    print('@mli: sqs resp: ', resp)
    msg = 'You are all set. But message failed to push to queue. Please start over.'
    if 'ResponseMetadata' in resp and 'HTTPStatusCode' in resp['ResponseMetadata'] and resp['ResponseMetadata']['HTTPStatusCode'] == 200:
        msg = 'You are all set. Expect my suggestions shortly! Have a good day.'
    return buildElicitIntentResponse(request, msg)
    
def dispatch(intent_request):
    print('@mli: intent_request: ', json.dumps(intent_request))
    intent_name = intent_request['sessionState']['intent']['name']
    response = None
    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingIntent':
        return handleGreeting(intent_request)
    elif intent_name == 'DiningSuggestionsIntent':
        return handleDiningSuggestions(intent_request)
    elif intent_name == 'ThankYouIntent':
        return handleThankYou(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    response = dispatch(event)
    return response