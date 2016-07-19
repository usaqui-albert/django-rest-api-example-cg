def card_string_format(card_type, last4):
    return card_type + ' **** **** **** ' + last4

def card_list(queryset):
    return [{"id": i.id, "name": card_string_format(i.brand, i.last4)} for i in queryset]
