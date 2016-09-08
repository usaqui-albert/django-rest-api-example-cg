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

# receipt = benevity.get_receipt_pdf(receipt='D6399685NT, D78N2ABLZ1')

receipts_list = benevity.get_receipt_list(user='user')
pp.pprint(receipts_list)

receipt_1 = benevity.get_receipt_detail(receipt='D6399685NT')
pp.pprint(receipt_1)

receipt_2 = benevity.get_receipt_detail(receipt='D78N2ABLZ1')
pp.pprint(receipt_2)
