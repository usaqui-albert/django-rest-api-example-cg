from ConnectGood.settings import BENEVITY_COMPANY_ID, BENEVITY_API_KEY
from benevity_library import benevity
from events.views import get_user_params
from users.models import User

from pprint import PrettyPrinter

pp = PrettyPrinter(indent=1)

benevity.api_key = BENEVITY_API_KEY
benevity.company_id = BENEVITY_COMPANY_ID

bryan = User.objects.get(email='bryan@connectgood.net')
data = get_user_params(bryan)
data.pop('active')
data.pop('country')

user_detail = benevity.get_user_profile(user=str(bryan.benevity_id))
pp.pprint(user_detail)

user_updated = benevity.update_user(**data)
pp.pprint(user_updated)

user_detail = benevity.get_user_profile(user=str(bryan.benevity_id))
pp.pprint(user_detail)
