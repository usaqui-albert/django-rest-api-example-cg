from stripe.error import APIConnectionError, InvalidRequestError, CardError

def card_string_format(card_type, last4):
    return card_type + ' **** **** **** ' + last4

def card_list(queryset):
    return [{"id": i.id, "name": card_string_format(i.brand, i.last4)} for i in queryset]

def stripe_errors_handler(error):
    response = ''
    if isinstance(error, APIConnectionError):
        response = str(error).split('.')[0]
    if isinstance(error, InvalidRequestError) or isinstance(error, CardError):
        body = error.json_body
        response = str(body['error']['message'])
    return response
