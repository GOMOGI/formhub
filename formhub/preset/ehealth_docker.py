#
# Alter this skeleton to agree with the needs of your local environment

# Note: if you are using a URL 12-Factor configuration scheme, you will not be using this file

# important thing we do here is to import all those symbols that are defined in settings.py
from ..settings import *  # get most settings from ../settings.py

import os

# or perhaps you would prefer something like:
# from staging import *  # which in turn imports ../settings.py

import logging
import tempfile
south_logger=logging.getLogger('south')
south_logger.setLevel(logging.INFO)


# # # and now you can override the settings which we just got from settings.py # # # #

# for example, choose a different database...
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'formhubdjangodb',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        #'OPTIONS': {
        #    'autocommit': True,  # NOTE: this option becomes obsolete in django 1.6
        #}
    },
}
# or:
DEBUG = True

SECRET_KEY = 'mlfs33^s1l4xf6a36$0#srgcpj%dd*sisfo6HOktYXB9y'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

TESTING_MODE = True


TOUCHFORMS_URL = 'http://localhost:8000/'

ENKETO_URL = 'https://enketo.org/'
#ENKETO_API_TOKEN = 'nfg5qaxk5oe'

#this token is needed for testing
ENKETO_API_TOKEN = 'abc'

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


BROKER_BACKEND = 'memory'

#MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')

_temp_media = tempfile.mkdtemp()
MEDIA_ROOT = _temp_media
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')

#DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
