# Django settings for snapex project.
import sys
import os.path

reload(sys)
sys.setdefaultencoding('utf-8')
gettext = lambda s: s

PROJECT_ROOT = os.path.join(
    os.path.realpath(os.path.dirname(__file__)), os.pardir)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TESTING_ON_LOCAL = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('admin', 'snapex@163.com')
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'beXsKRIOGfKKTwkkcTkh',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '4vvtke0DV3yR9bIYcGyDvKBC',
        'PASSWORD': '1B65i354OUTyyyVxMhI9IlgBxFztCp84',
        'HOST': 'sqld.duapp.com',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '4050',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
# TIME_ZONE = 'Asia/Shanghai'
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

LANGUAGES = (
    ('en', gettext('English')),
    ('zh_CN', gettext('Chinese'))
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'g#(-&3v+q5d(_3xh3s29+$r%jx39m*$^jwo26yrizna3ykmhg8'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'snapex.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'snapex.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    #'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'xadmin',
    'crispy_forms',
    'rest_framework',
    'polls',
    'signin',
    'api',
    'mypage',
    'test',
    'myview',

)

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i'
TIME_FORMAT = 'H:i'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/home/bae/log/debug.log',
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'polls': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
        },
        'test': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
        },
    }
}

# FOR sessions
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 86400 # sec
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_NAME = 'DSESSIONID'
SESSION_COOKIE_SECURE = False

LOGIN_URL = '/signin/'

# default password for testees and researchers in User model
DEFAULT_PASSWORD = SECRET_KEY
PUSH_ON_TIME = True


#### BCS BUCKET RELATED SETTINGS #####
BCS_SETTINGS = {
    "HOST" : "http://bcs.duapp.com/",
    "BUCKET_LIST" : {
        "other" : "snapex-others",
        "image"   : "snapex-images",
        "photo"   : "snapex-photos",
        "audio"   : "snapex-audios",
        "default" : "snapex-user-media"
    },
    "AK" : "4vvtke0DV3yR9bIYcGyDvKBC",
    "SK" : "1B65i354OUTyyyVxMhI9IlgBxFztCp84"
}



### IF TESTING ON LOCAL #####
TESTING_ON_LOCAL = 'SERVER_SOFTWARE' not in os.environ ## DEBUGGING ON LOCAL
if TESTING_ON_LOCAL:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
        }
    }
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            #'NAME': 'beXsKRIOGfKKTwkkcTkh',                      # Or path to database file if using sqlite3.
            'NAME':'production_copy',
            # The following settings are not used with sqlite3:
            'USER': 'snapex',
            'PASSWORD': 'snapex',
            'HOST': '127.0.0.1',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': '3306',                      # Set to empty string for default.
        }
    }


if TESTING_ON_LOCAL:
    #STATIC_ROOT = '/Users/Yuming/Codes/BAE/appid282gcboc93/static'
    STATICFILES_DIRS = (
        # Put strings here, like "/home/html/static" or "C:/www/django/static".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
        '/Users/Yuming/Codes/BAE-v2/appid282gcboc93/static',
    )
    #STATIC_ROOT = '/Users/Yuming/Codes/BAE/appid282gcboc93/static'

USE_TEST_BUCKETS = False

if TESTING_ON_LOCAL & USE_TEST_BUCKETS:

    BCS_SETTINGS = {
        "HOST" : "http://bcs.duapp.com/",
        "BUCKET_LIST" : {
            "other" : "snapex-others-test",
            "image"   : "snapex-images-test",
            "photo"   : "snapex-photos-test",
            "audio"   : "snapex-audios-test",
            "default" : "snapex-user-media-test"
        },
        "AK" : "4vvtke0DV3yR9bIYcGyDvKBC",
        "SK" : "1B65i354OUTyyyVxMhI9IlgBxFztCp84"
    }