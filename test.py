from ConnectGood.settings import BENEVITY_COMPANY_ID, BENEVITY_API_KEY
from benevity_library import benevity

from pprint import PrettyPrinter

pp = PrettyPrinter(indent=1)

benevity.api_key = BENEVITY_API_KEY
benevity.company_id = BENEVITY_COMPANY_ID

query_params = {
    'user': 'user2',
    'lastname': 'Tremaine',
    'initials': 'J',
    'firstname': 'Kimberly',
    'email': 'KimberlyJTremaine@example.example',
    'country': '124',
    'active': 'yes'
}
search_params_2 = {
    'country': '840',
    'term': 'RARE'
}
search_params = {
    'country': '840',
    'term': 'red cross'
}

causes = benevity.search_causes(**search_params)
pp.pprint(causes)
