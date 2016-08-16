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
    'country': '840',
    'term': 'LEUKEMIA SOCIETY'
}
search_params_2 = {
    'country': '840',
    'term': 'PATIENT ACCESS NETWORK FOUNDATION'
}
search_params_3 = {
    'country': '840',
    'term': 'CANCER RESEARCH INSTITUTE'
}

causes = benevity.search_causes(**search_params)
for i in range(40):
    print ''
causes_2 = benevity.search_causes(**search_params_2)
for j in range(40):
    print ''
causes_3 = benevity.search_causes(**search_params_3)

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
