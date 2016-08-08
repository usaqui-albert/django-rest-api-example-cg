"""This a library to handle request to the benevity api"""
import urllib2
import hmac
import base64
import collections

from lxml import etree, objectify
from hashlib import sha1

BENEVITY_BASE_URL = 'https://sandbox.benevity.org'

def do_request(function):
    def decorated_function(instance, **kwargs):
        url = function(instance, **kwargs)
        try:
            u = urllib2.urlopen(url).read()
        except (urllib2.URLError, urllib2.HTTPError) as e:
            if isinstance(e, urllib2.HTTPError):
                return 'HTTP %s %s' % (e.code, e.reason)
            if isinstance(e, urllib2.URLError):
                return str(e.reason)
        else:
            root = etree.XML(u)
            xml_string = etree.tostring(root)
            print xml_string
            xml_object = objectify.fromstring(xml_string)
            return xml_object
    return decorated_function

class Benevity(object):

    def __init__(self):
        self.company_id = str()
        self.api_key = str()

    @do_request
    def get_company_user_list(self, **kwargs):
        return self.get_url_request('GetCompanyUserList', **kwargs)

    @do_request
    def add_user(self, **kwargs):
        return self.get_url_request('AddUser', **kwargs)

    @do_request
    def activate_user(self, **kwargs):
        return self.get_url_request('ActivateUser', **kwargs)

    @do_request
    def get_company_cause_list(self, **kwargs):
        return self.get_url_request('GetCompanyCauseList', **kwargs)

    @do_request
    def search_causes(self, **kwargs):
        return self.get_url_request('SearchCauses', **kwargs)

    @do_request
    def company_transfer_credits_to_cause(self, **kwargs):
        return self.get_url_request('CompanyTransferCreditsToCause', **kwargs)

    @do_request
    def company_transfer_credits_to_cause_for_user(self, **kwargs):
        return self.get_url_request('CompanyTransferCreditsToCauseForUser', **kwargs)

    @do_request
    def company_transfer_credits_to_user(self, **kwargs):
        return self.get_url_request('CompanyTransferCreditsToUser', **kwargs)

    @do_request
    def user_transfer_credits_to_causes(self, **kwargs):
        return self.get_url_request('UserTransferCreditsToCauses', **kwargs)

    def get_url_request(self, operation, **kwargs):
        url_hmac = self.get_url_hmac(operation, **kwargs)
        return BENEVITY_BASE_URL + url_hmac + 'hmac=%s' % self.get_hmac_code(url_hmac)

    def get_url_hmac(self, operation, **kwargs):
        url_request = '/Adapter.General/' + self.company_id + '/' + operation
        return url_request + self.query_params_handler(kwargs) if len(kwargs) > 0 else url_request

    def get_hmac_code(self, url_hmac):
        digest = hmac.new(self.api_key, url_hmac, sha1).digest()
        return base64.encodestring(digest)

    @staticmethod
    def query_params_handler(dic):
        query_path = '?'
        ordered_dic = collections.OrderedDict(sorted(dic.items()))
        for key, value in ordered_dic.iteritems():
            query_path += key + '=' + str(value) + '&'
        return query_path[:-1]

benevity = Benevity()
