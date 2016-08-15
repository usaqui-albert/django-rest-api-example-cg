from ConnectGood.settings import BENEVITY_COMPANY_ID, BENEVITY_API_KEY
from benevity_library import benevity

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

search_params = {
    'country': '124',
    'term': 'name.f:stroke'
}

print search_params

causes = benevity.search_causes(**search_params)
if not isinstance(causes, str):
    if causes.attrib['status'] == 'SUCCESS':
        print 'Causes fue success'
    else:
        print 'Causes fue error'

response = benevity.add_user(**query_params)
if not isinstance(response, str):
    if response.attrib['status'] == 'SUCCESS':
        print 'Add fue success'
    else:
        print 'Add fue error'
