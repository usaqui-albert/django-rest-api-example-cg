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
    'term': 'HABITAT FOR HUMANITY'
}
search_params_2 = {
    'country': '124',
    'term': 'FREE THE CHILDREN'
}
search_params_3 = {
    'country': '124',
    'term': 'DOCTORS WITHOUT BORDERS'
}
search_params_4 = {
    'country': '124',
    'term': 'AMNESTY INTERNATIONAL'
}
search_params_5 = {
    'country': '124',
    'term': 'SICKKIDS FOUNDATION'
}

causes = benevity.search_causes(**search_params)
for i in range(40):
    print ''
causes_2 = benevity.search_causes(**search_params_2)
for j in range(40):
    print ''
causes_3 = benevity.search_causes(**search_params_3)
for k in range(40):
    print ''
causes_4 = benevity.search_causes(**search_params_4)
for l in range(40):
    print ''
causes_5 = benevity.search_causes(**search_params_5)
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
