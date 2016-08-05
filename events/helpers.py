import uuid
from django.db import IntegrityError

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
