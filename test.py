from ConnectGood.settings import BENEVITY_COMPANY_ID, BENEVITY_API_KEY
from benevity_library import benevity

benevity.api_key = BENEVITY_API_KEY
benevity.company_id = BENEVITY_COMPANY_ID

query_params = {
    'user': 'User01120160331210259006',
    'lastname': 'Tremaine',
    'initials': 'J',
    'firstname': 'Kimberly',
    'email': 'KimberlyJTremaine@example.example',
    'country': '124',
    'address-street': '504SilverSpringsBlvd',
    'address-state': 'AB',
    'address-postcode': 'T3B2C3',
    'address-country': '124',
    'active': 'yes'
}

response = benevity.activate_user(**query_params)

if not isinstance(response, str):
    pass
