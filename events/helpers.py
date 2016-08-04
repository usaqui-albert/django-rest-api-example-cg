import uuid
from django.db import IntegrityError

from ConnectGood.settings import BENEVITY_BASE_URL

STATUS_OF_THE_EVENT = (('ACCEPTED', 'A'), ('REJECTED', 'R'))

def validate_uuid4(uuid_string):
    try:
        val = uuid.UUID(uuid_string, version=4)
    except ValueError:
        return False
    else:
        return True

def get_event_status(status_requested):
    return [y for x, y in STATUS_OF_THE_EVENT if x == status_requested][0]

def update_event_status(user_event, event_status):
    try:
        user_event.status = event_status
        user_event.save()
    except IntegrityError:
        return False
    else:
        return True

def benevity_request_handler(company_id, operation, **query_params):
    https_request = BENEVITY_BASE_URL + str(company_id) + '/' + operation
    if len(query_params) > 0:
        https_request += '?'
        for key, value in query_params.iteritems():
            https_request += key + '=' + value + '&'
        https_request = https_request[:-1]
    return https_request
