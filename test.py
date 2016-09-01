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
    'cause': '124-119219814RR0001'
}

# receipt = benevity.get_receipt_pdf(receipt='D6399685NT')

company_transfer = benevity.company_transfer_credits_to_user(
    user='user',
    cashable='no',
    credits='10000',
    refno='CG1000'
)
pp.pprint(company_transfer)

user_transfer = benevity.user_transfer_credits_to_causes(
    user='user',
    credits=200,
    refno='CG1000',
    cause='124-119219814RR0001'
)
pp.pprint(user_transfer)

generated_receipt = benevity.generate_user_receipts(user='user')
pp.pprint(generated_receipt)

receipts = benevity.get_receipt_list(user='user')
pp.pprint(receipts)
