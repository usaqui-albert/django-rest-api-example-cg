"""This a library to handle request to the benevity api"""
import urllib
import urllib2
import hmac
import base64
import collections

from lxml import etree, objectify
from hashlib import sha1

BENEVITY_BASE_URL = 'https://sandbox.benevity.org'


def error_handler(error):
    if isinstance(error, urllib2.HTTPError):
        return 'HTTP %s %s' % (error.code, error.reason)
    if isinstance(error, urllib2.URLError):
        return str(error.reason)

def objectifying_response(response):
    root = etree.XML(response)
    xml_string = etree.tostring(root)
    print xml_string
    return objectify.fromstring(xml_string)

def post(function):
    def decorated_function(instance, **kwargs):
        try:
            u = urllib2.urlopen(function(instance, **kwargs), data="").read()
        except (urllib2.URLError, urllib2.HTTPError) as e:
            return error_handler(e)
        else:
            return objectifying_response(u)
    return decorated_function

def get(function):
    def decorated_function(instance, **kwargs):
        try:
            u = urllib2.urlopen(function(instance, **kwargs)).read()
        except (urllib2.URLError, urllib2.HTTPError) as e:
            return error_handler(e)
        else:
            return objectifying_response(u)
    return decorated_function

class Benevity(object):

    def __init__(self):
        self.company_id = str()
        self.api_key = str()

    @get
    def get_company_user_list(self, **kwargs):
        return self.get_url_request('GetCompanyUserList', **kwargs)

    @post
    def add_user(self, **kwargs):
        return self.get_url_request('AddUser', **kwargs)

    @post
    def activate_user(self, **kwargs):
        return self.get_url_request('ActivateUser', **kwargs)

    @get
    def get_company_cause_list(self, **kwargs):
        return self.get_url_request('GetCompanyCauseList', **kwargs)

    @get
    def search_causes(self, **kwargs):
        return self.get_url_request('SearchCauses', **kwargs)

    @post
    def company_transfer_credits_to_cause(self, **kwargs):
        return self.get_url_request('CompanyTransferCreditsToCause', **kwargs)

    @post
    def company_transfer_credits_to_cause_for_user(self, **kwargs):
        return self.get_url_request('CompanyTransferCreditsToCauseForUser', **kwargs)

    @post
    def company_transfer_credits_to_user(self, **kwargs):
        return self.get_url_request('CompanyTransferCreditsToUser', **kwargs)

    @post
    def user_transfer_credits_to_causes(self, **kwargs):
        return self.get_url_request('UserTransferCreditsToCauses', **kwargs)

    def get_url_request(self, operation, **kwargs):
        url_hmac = self.get_url_hmac(operation, **kwargs)
        return BENEVITY_BASE_URL + url_hmac + '&' + self.get_hmac_code(url_hmac)

    def get_url_hmac(self, operation, **kwargs):
        url_request = '/Adapter.General/' + self.company_id + '/' + operation
        return url_request + self.query_params_handler(kwargs) if len(kwargs) > 0 else url_request

    def get_hmac_code(self, url_hmac):
        digest = hmac.new(self.api_key, url_hmac, sha1).digest()
        return urllib.urlencode({'hmac': base64.encodestring(digest).strip()})

    @staticmethod
    def query_params_handler(dic):
        query_path = '?'
        ordered_dic = collections.OrderedDict(sorted(dic.items()))
        for key, value in ordered_dic.iteritems():
            query_path += key + '=' + str(value) + '&'
        return query_path[:-1]

benevity = Benevity()
