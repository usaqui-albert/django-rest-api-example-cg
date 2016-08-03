import urllib2
from lxml import etree, objectify

url = 'https://sandbox.benevity.org/Adapter.General/1/ActivateUser?hmac=empty-key&user=User01120160331210259006&lastname=Tremaine&initials=J&firstname=Kimberly&email=KimberlyJTremaine@example.example&country=124&address-street=504SilverSpringsBlvd&address-state=AB&address-postcode=T3B2C3&address-country=124&active=yes'

try:
    u = urllib2.urlopen(url).read()
except (urllib2.URLError, urllib2.HTTPError) as e:
    if isinstance(e, urllib2.HTTPError):
        print 'es un http error'
    if isinstance(e, urllib2.URLError):
        print 'es un url error'
    print e.reason
else:
    print u
    root = etree.XML(u)
    print root
    xml_string = etree.tostring(root)
    print xml_string
    response = objectify.fromstring(xml_string)
    for i in response.request.param:
        print i.get('name'), i.get('value')
