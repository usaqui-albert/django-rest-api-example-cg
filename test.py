from ConnectGood.settings import BENEVITY_COMPANY_ID, BENEVITY_API_KEY
from benevity_library import benevity

from pprint import PrettyPrinter

pp = PrettyPrinter(indent=1)

benevity.api_key = BENEVITY_API_KEY
benevity.company_id = BENEVITY_COMPANY_ID

query_params = {
    'user': 'user3',
    'lastname': 'Tremaine',
    'firstname': 'Kimberly',
    'email': 'KimberlyJTremaine@example.example',
    'country': '124',
    'address-city': 'Calgary',
    'address-country': '124',
    'address-state': 'ABCDFGHIJK',
    'address-postcode': 'T3B2C3',
    'address-street': '504',
    'active': 'yes'
}

transaction_data = {
    'user': 'user',
    'credits': '100',
    'refno': 'CG1',
    'cause.124-119219814RR0001': '100'
}

transaction = benevity.user_transfer_credits_to_causes(**transaction_data)
pp.pprint(transaction)

response = benevity.get_receipt_list(user='user')
pp.pprint(response)
