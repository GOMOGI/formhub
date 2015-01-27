# this system uses structured settings.py as defined in http://www.slideshare.net/jacobian/the-best-and-worst-of-django

try:
    from ..settings import *
except ImportError:
    import sys, django
    django.utils.six.reraise(RuntimeError, *sys.exc_info()[1:])  # use RuntimeError to extend the traceback
except:
    raise

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEMPLATE_STRING_IF_INVALID = ''

TIME_ZONE = 'Africa/Lagos'

# override to set the actual location for the production static and media directories
MEDIA_ROOT = '/var/formhub-media'
STATIC_ROOT = "/srv/formhub-static"

ADMINS = (
    ('Vernon Cole', 'vernon.cole@ehealthafrica.org'),
)

MANAGERS = ADMINS

#postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'formhub_dev',
        'USER': 'formhub_dev',
        'PASSWORD': '12345678',
        'HOST': 'cdc-staging.eocng.org',
        'OPTIONS': {
            'autocommit': True,  # NOTE: this option becomes obsolete in django 1.6
        }
    },
}

BROKER_URL = 'amqp://formhub:12345678@localhost:5672/formhub_vhost'

TOUCHFORMS_URL = 'http://localhost:9000/'

ALLOWED_HOSTS = ['.eocng.org', '.ehealth.org.ng' ,'forms.ehealthafrica.org', '']

SECRET_KEY = 'mlfs33^s1l4xf6a36$0#srgcpj%dd*sisfo6HOktYXB9y'

EMAIL_HOST = 'smtp.gmail.com'  #The host to use for sending email.

EMAIL_HOST_PASSWORD = os.environ.get("FORMHUB_EMAIL_PASSWORD", "12345678")
#Password to use for the SMTP server defined in EMAIL_HOST.
EMAIL_HOST_USER = 'do.not.reply@ehealthnigeria.org'

EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "do.not.reply@ehealthnigeria.org"

TOUCHFORMS_URL = 'http://localhost:9000/'

if len(sys.argv) >= 2 and (sys.argv[1] == "test" or sys.argv[1] == "test_all"):
    # This trick works only when we run tests from the command line.
    TESTING_MODE = True
else:
    TESTING_MODE = False

if TESTING_MODE:
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'test_media/')
    subprocess.call(["rm", "-r", MEDIA_ROOT])
    MONGO_DATABASE['NAME'] = "formhub_test"
    # need to have CELERY_ALWAYS_EAGER True and BROKER_BACKEND as memory
    # to run tasks immediately while testing
    CELERY_ALWAYS_EAGER = True
    BROKER_BACKEND = 'memory'

    ENKETO_API_TOKEN = 'abc'
    #TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

if PRINT_EXCEPTION and DEBUG:
    MIDDLEWARE_CLASSES += ('utils.middleware.ExceptionLoggingMiddleware',)
# Clear out the test database
if TESTING_MODE:
    MONGO_DB.instances.drop()
