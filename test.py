from ConnectGood.settings import BENEVITY_COMPANY_ID, BENEVITY_API_KEY
from benevity_library import benevity

from pprint import PrettyPrinter

pp = PrettyPrinter(indent=1)

benevity.api_key = BENEVITY_API_KEY
benevity.company_id = BENEVITY_COMPANY_ID

query_params = {
    'user': 'user',
    'lastname': 'Tremaine',
    'firstname': 'Kimberly',
    'email': 'KimberlyJTremaine@example.example',
    'country': '124',
    'address-city': 'Calgary',
    'address-country': '124',
    'address-state': 'AB',
    'address-postcode': 'T3B2C3',
    'address-street': '504',
    'active': 'yes'
}
search_params = {
    'country': '124',
    'term': 'cross',
    'page': 1,
    'pagesize': 5
}

response = benevity.get_company_user_list(active='yes')
pp.pprint(response)
