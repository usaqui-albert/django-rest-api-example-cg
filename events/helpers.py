import uuid

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

def get_custom_host(request):
    http_or_https = request.build_absolute_uri().split(':')[0]
    return http_or_https + '://' + request.get_host()

def error_message_handler(message, host):
    return message if '3000' in host else 'Unexpected error'

def get_message_error(dic):
    try:
        messages = [i for i in dic['children'] if 'messages' in i][0]['messages']['children']
        message = messages[0]['message']
        error_message = 'Message error: %s - %s, Code error: %s' % (
            message['attrib']['field'],
            message['text'].strip(),
            message['attrib']['code'],
        )
    except (KeyError, IndexError):
        return None
    else:
        return error_message
