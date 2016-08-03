import urllib2
from xml.etree import ElementTree

url = 'https://sandbox.benevity.org/Adapter.General/1/ActivateUser?hmac=empty-key&user=User01120160331210259006&lastname=Tremaine&initials=J&firstname=Kimberly&email=KimberlyJTremaine@example.example&country=124&address-street=504SilverSpringsBlvd&address-state=AB&address-postcode=T3B2C3&address-country=124&active=yes'
request = urllib2.Request(url)
try:
    u = urllib2.urlopen(request)
except (urllib2.URLError, urllib2.HTTPError) as e:
    if isinstance(e, urllib2.HTTPError):
        print 'es un http error'
    if isinstance(e, urllib2.URLError):
        print 'es un url error'
    print e.reason
else:
    tree = ElementTree.parse(u)
    print tree
    rootElem = tree.getroot()
    print rootElem
    response = rootElem.find('response')
    print response
