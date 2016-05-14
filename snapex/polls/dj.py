#-*- coding: utf-8 -*-
'''
Utilities with Django.
'''
import os
import sys
from django.contrib.auth import get_backends, login


def easy_login(req, user):
    '''
    Login a user without password authentication.
    '''
    backend = get_backends()[0]
    user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
    login(req, user)


def dj_setting(name=None):
    '''
    Get the setting moudle of django.
    if name is provided, the value of name will be returned,
    else the module itself will be returned.
    '''
    module_name = os.environ.get('DJANGO_SETTINGS_MODULE', '')
    if module_name:
        __import__(module_name)
        module = sys.modules[module_name]
        if name is None:
            return module
        else:
            return getattr(module, name, None)
    else:
        raise Exception("No Django setting module found.")


class SettingsContext(object):
    def __init__(self):
        self.settings = None

    def _prepare(self):
        ret = {}
        for k, v in vars(dj_setting()).items():
            if isinstance(v, basestring):
                ret["SETTINGS_%s" % k] = v
        self.settings = ret

    def __call__(self, request):
        if self.settings is None:
            self._prepare()        
        return self.settings

settings_context_processor = SettingsContext()
