"""This a library to handle request to the benevity api"""
import urllib
import urllib2
import hmac
import base64
import collections

from hashlib import sha1
from lxml import etree, objectify

BENEVITY_BASE_URL = 'https://sandbox.benevity.org'


def urllib2_error_handler(error):
    """Method to handle the errors of the urllib2 library

    :param error: urllib2 exception error
    :return: string with the error message
    """
    if isinstance(error, urllib2.HTTPError):
        return 'HTTP %s %s' % (error.code, error.reason)
    if isinstance(error, urllib2.URLError):
        return str(error.reason)

def benevity_response_handler(response):
    """Method to handle the response of the benevity api, xml to dict response

    :param response: benevity response as xml
    :return: response as dictionary
    """
    root = etree.XML(response)
    xml_string = etree.tostring(root)
    print xml_string
    return objectify.fromstring(xml_string)

def post(function):
    """Method to do a POST request to the benevity api handling response errors

    :param function: the function that is going to be decorated
    :return: decorated function
    """
    def decorated_function(instance, **kwargs):
        """Decorator function of the one passed by parameter"""
        try:
            response = urllib2.urlopen(function(instance, **kwargs), data="").read()
        except (urllib2.URLError, urllib2.HTTPError) as err:
            return urllib2_error_handler(err)
        else:
            return benevity_response_handler(response)
    return decorated_function

def get(function):
    """Method to do a GET request to the benevity api handling response errors

    :param function: the function that is going to be decorated
    :return: decorated function
    """
    def decorated_function(instance, **kwargs):
        """Decorator function of the one passed by parameter"""
        try:
            response = urllib2.urlopen(function(instance, **kwargs)).read()
        except (urllib2.URLError, urllib2.HTTPError) as err:
            return urllib2_error_handler(err)
        else:
            return benevity_response_handler(response)
    return decorated_function

class Benevity(object):
    """Class to handle benevity requests"""

    def __init__(self):
        self.company_id = str()
        self.api_key = str()

    @get
    def get_company_user_list(self, **kwargs):
        """Method to get url path for the benevity GetCompanyUserList endpoint"""
        return self.get_url_request('GetCompanyUserList', **kwargs)

    @post
    def add_user(self, **kwargs):
        """Method to get url path for the benevity AddUser endpoint"""
        return self.get_url_request('AddUser', **kwargs)

    @post
    def activate_user(self, **kwargs):
        """Method to get url path for the benevity ActivateUser endpoint"""
        return self.get_url_request('ActivateUser', **kwargs)

    @get
    def get_company_cause_list(self, **kwargs):
        """Method to get url path for the benevity GetCompanyCauseList endpoint"""
        return self.get_url_request('GetCompanyCauseList', **kwargs)

    @get
    def search_causes(self, **kwargs):
        """Method to get url path for the benevity SearchCauses endpoint"""
        return self.get_url_request('SearchCauses', **kwargs)

    @post
    def company_transfer_credits_to_cause(self, **kwargs):
        """Method to get url path for the benevity CompanyTransferCreditsToCause endpoint"""
        return self.get_url_request('CompanyTransferCreditsToCause', **kwargs)

    @post
    def company_transfer_credits_to_cause_for_user(self, **kwargs):
        """Method to get url path for the benevity CompanyTransferCreditsToCauseForUser
        endpoint
        """
        return self.get_url_request('CompanyTransferCreditsToCauseForUser', **kwargs)

    @post
    def company_transfer_credits_to_user(self, **kwargs):
        """Method to get url path for the benevity CompanyTransferCreditsToUser endpoint"""
        return self.get_url_request('CompanyTransferCreditsToUser', **kwargs)

    @post
    def user_transfer_credits_to_causes(self, **kwargs):
        """Method to get url path for the benevity UserTransferCreditsToCauses endpoint"""
        return self.get_url_request('UserTransferCreditsToCauses', **kwargs)

    def get_url_request(self, operation, **kwargs):
        """Method to get the complete url to requesting benevity api

        :param operation: action(endpoint) to requesting benevity api
        :param kwargs: data to send to the benevity api
        :return: complete url to hit benevity api
        """
        url_hmac = self.get_url_hmac(operation, **kwargs)
        return BENEVITY_BASE_URL + url_hmac.replace(' ', '+') + '&' + self.get_hmac_code(url_hmac)

    def get_url_hmac(self, operation, **kwargs):
        """Method to get url path that will be used to build the hmac code

        :param operation: action(endpoint) that we want to do in benevity
        :param kwargs: data to build the query param path
        :return: url path that will be used to build the hmac code
        """
        url_request = '/Adapter.General/' + self.company_id + '/' + operation
        return url_request + self.query_params_handler(kwargs) if len(kwargs) > 0 else url_request

    def get_hmac_code(self, url_hmac):
        """Method to get the hmac code ask by benevity to do requests

        :param url_hmac: url used to build the hmac code through hmac-sha1 and urlencode
        :return: hmac code to be append to the query params path
        """
        digest = hmac.new(self.api_key, url_hmac, sha1).digest()
        return urllib.urlencode({'hmac': base64.encodestring(digest).strip()})

    @staticmethod
    def query_params_handler(dic):
        """Method to build the query params path(alphabetically ordered)

        :param dic: dictionary with the data to be ordered by key
        :return: query params path alphabetically ordered
        """
        query_path = '?'
        ordered_dic = collections.OrderedDict(sorted(dic.items()))
        for key, value in ordered_dic.iteritems():
            query_path += key + '=' + str(value) + '&'
        return query_path[:-1]

benevity = Benevity()
