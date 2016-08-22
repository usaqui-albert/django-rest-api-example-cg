import os
from uuid import uuid4
from django.utils.deconstruct import deconstructible

from plans.helpers import filtering_dict_by_keys

@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(uuid4().hex, ext)
        return os.path.join(self.path, filename)

charities_filter_keys = ['name', 'id', 'city', 'postcode', 'state', 'website', 'active'
                         'address', 'facebook_url']

def get_charity_response(charities):
    return [filtering_dict_by_keys(charity['cause']['attrib'],
                                   charities_filter_keys) for charity in charities]

def get_content_response(dic_list):
    return [i for i in dic_list if 'content' in i][0]['content']

def get_causes_response(dic_list):
    return [i for i in dic_list if 'causes' in i][0]['causes']
