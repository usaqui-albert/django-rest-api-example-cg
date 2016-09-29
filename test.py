from ConnectGood.settings import BENEVITY_COMPANY_ID, BENEVITY_API_KEY
from benevity_library import benevity
from events.helpers import get_message_error

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

data = {
    'user': '2ec25bf3-5f36-40bd-925a-69b23c15586e',
    'lastname': 'Usaqui',
    'country': '840',
    'address-city': 'Toronto',
    'address-country': '840',
    'address-state': 'Alabama',
    'address-postcode': '654-321',
    'address-street': 'Cubo Negro'
}

user_detail = benevity.get_user_profile(user='2ec25bf3-5f36-40bd-925a-69b23c15586e')
pp.pprint(user_detail)

user_updated = benevity.update_user(**data)
pp.pprint(user_updated)

user_detail = benevity.get_user_profile(user='2ec25bf3-5f36-40bd-925a-69b23c15586e')
pp.pprint(user_detail)
