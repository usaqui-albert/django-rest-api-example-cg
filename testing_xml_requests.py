import urllib2
from lxml import etree, objectify

from events.helpers import benevity_request_handler

query_params = {
    'hmac': 'empty-key',
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
url = benevity_request_handler(1, 'ActivateUser', **query_params)

try:
    u = urllib2.urlopen(url).read()
except (urllib2.URLError, urllib2.HTTPError) as e:
    if isinstance(e, urllib2.HTTPError):
        print 'es un http error'
    if isinstance(e, urllib2.URLError):
        print 'es un url error'
    print e.reason
else:
    root = etree.XML(u)
    xml_string = etree.tostring(root)
    print xml_string
    response = objectify.fromstring(xml_string)
    for i in response.request.param:
        print i.get('name'), i.get('value')
