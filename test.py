from ConnectGood.settings import BENEVITY_COMPANY_ID, BENEVITY_API_KEY
from benevity_library import benevity

from pprint import PrettyPrinter

pp = PrettyPrinter(indent=1)

benevity.api_key = BENEVITY_API_KEY
benevity.company_id = BENEVITY_COMPANY_ID

query_params = {
    'user': '2ec25bf3-5f36-40bd-925a-69b23c15586e',
    'lastname': 'Usaqui',
    'firstname': 'Albert',
    'email': 'usaqui.albert@gmail.com',
    'country': '124',
    'address-city': 'Toronto',
    'address-country': '124',
    'address-state': 'Alberta',
    'address-postcode': '123-456',
    'address-street': 'Plaza Venezuela',
    'active': 'yes'
}

# receipt = benevity.get_receipt_pdf(receipt='D6399685NT, D78N2ABLZ1')
data = {
    'user': '2ec25bf3-5f36-40bd-925a-69b23c15586e',
    'credits': '7500',
    'refno': 'e9c22c22-62d4-47ca-881e-4feabd9911db',
    'cause': '840-131788491'
}

transfer = benevity.user_transfer_credits_to_causes(**data)
pp.pprint(transfer)
