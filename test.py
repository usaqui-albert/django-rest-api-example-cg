from ConnectGood.settings import BENEVITY_COMPANY_ID, BENEVITY_API_KEY
from benevity_library import benevity
from charities.helpers import get_content_response, get_receipts_response, get_receipt_response

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

company_transfer = benevity.company_transfer_credits_to_user(
    user='user2',
    credits='10000',
    refno='CG1003',
    cashable='no'
)
pp.pprint(company_transfer)

# receipt = benevity.get_receipt_pdf(receipt='D6399685NT, D78N2ABLZ1')
user_transfer = benevity.user_transfer_credits_to_causes(
    user='user2',
    credits=200,
    refno='CG1003',
    cause='124-106846942RR0001'
)
pp.pprint(user_transfer)

generated_receipt = benevity.generate_user_receipts(user='user2')
pp.pprint(generated_receipt)

content = get_content_response(generated_receipt['children'])
pp.pprint(content)

receipts = get_receipts_response(content['children'])
pp.pprint(receipts)

receipt = get_receipt_response(receipts['children'])
pp.pprint(receipt)

for i in range(50):
    print ''

receipts_list = benevity.get_receipt_list(user='user2')
pp.pprint(receipts_list)
