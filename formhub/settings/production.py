# this system uses structured settings.py as defined in http://www.slideshare.net/jacobian/the-best-and-worst-of-django

from base import *

DEBUG = False  # this setting file will not work on "runserver" -- it needs a server for static files

# override to set the actual location for the production static and media directories
MEDIA_ROOT = '/var/formhub-media'
STATIC_ROOT = "/srv/formhub-static"
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, "static"),
)
ADMINS = (
    # ('Adam Thompson', 'adam@ehealthafrica.org'),
)
# your actual production settings go here...,.
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'phis',
        'USER': 'phis',
        'PASSWORD': 'nopolio4u',
        'HOST': 'nomads.eocng.org',
        'OPTIONS': {
            'autocommit': True,
        },
    },
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'America/New_York'
TIME_ZONE = 'Africa/Lagos'

TOUCHFORMS_URL = 'http://localhost:9000/'

MONGO_DATABASE = {
    'HOST': 'localhost',
    'PORT': 27017,
    'NAME': 'formhub',
    'USER': '',
    'PASSWORD': ''
}
# Make this unique, and don't share it with anybody.
SECRET_KEY = "&!1#=b7b7w*qb$w1nz=b04zwaan@^hi52k_o+^9dy#eb_he1u8"

ALLOWED_HOSTS = ['.eocng.org', '.ehealthafrica.org']

INTERNAL_IPS = ('192.168.0.0/16',)

WSGI_APPLICATION = "formhub.wsgi.application"
