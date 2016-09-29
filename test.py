from ConnectGood.settings import BENEVITY_COMPANY_ID, BENEVITY_API_KEY
from benevity_library import benevity
from users.models import User

from pprint import PrettyPrinter

pp = PrettyPrinter(indent=1)

benevity.api_key = BENEVITY_API_KEY
benevity.company_id = BENEVITY_COMPANY_ID

def get_data(user):
    return {
        'email': str(user.email),
        'firstname': str(user.company) if user.is_corporate_account() else str(user.first_name),
        'lastname': '-' if user.is_corporate_account() else str(user.last_name),
        'active': 'yes',
        'user': str(user.benevity_id),
        'country': str(user.get_country_iso_code()),
        'address-city': str(user.city),
        'address-country': str(user.get_country_iso_code()),
        'address-postcode': str(user.zip_code),
        'address-state': str(user.get_state_as_string()),
        'address-street': str(user.street_address)
    }

bryan = User.objects.get(email='bryan@connectgood.net')
data = get_data(bryan)

user_detail = benevity.get_user_profile(user=str(bryan.benevity_id))
pp.pprint(user_detail)

user_updated = benevity.update_user(**data)
pp.pprint(user_updated)

user_detail = benevity.get_user_profile(user=str(bryan.benevity_id))
pp.pprint(user_detail)
