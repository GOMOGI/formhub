# this system uses structured settings.py as defined in http://www.slideshare.net/jacobian/the-best-and-worst-of-django

try:
    from ..settings import *
except ImportError:
    import sys, django
    django.utils.six.reraise(RuntimeError, *sys.exc_info()[1:])  # use RuntimeError to extend the traceback
except:
    raise

import logging

logging.warning("Hey you shouldn't be using this.\n"
"If you are, copy this file to local_settings.py in the parent dir\n"
"See https://code.djangoproject.com/wiki/SplitSettings#Multiplesettingfilesimportingfromeachother")

