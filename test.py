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

data = {
    'cashable': 'no',
    'user': '2ec25bf3-5f36-40bd-925a-69b23c15586e',
    'refno': 'e9c22c22-62d4-47ca-881e-4feabd9911db',
    'credits': '7500'
}

transfer = benevity.company_transfer_credits_to_user(**data)
pp.pprint(transfer)
