# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

def get_backend(path=None):
    path = path or getattr(settings, 'LOGSTREAM_BACKEND',
       'django_logstream.server.backends.zeromq')
    
    module = import_module(path + ".base")
    try:
        klass = getattr(module, 'Backend')
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define '
                                    'a "Backend" class' % (module))
    return klass()
