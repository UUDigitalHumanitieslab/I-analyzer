"""
Django settings for ianalyzer project.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import warnings

from ianalyzer.common_settings import *


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'kxreeb3bds$oibo7ex#f3bi5r+d(1x5zljo-#ms=i2%ih-!pvn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('SQL_DATABASE', 'ianalyzer'),
        'USER': os.getenv('SQL_USER', 'ianalyzer'),
        'PASSWORD': os.getenv('SQL_PASSWORD', 'ianalyzer'),
        'HOST': os.getenv('SQL_HOST', 'localhost'),
        'PORT': os.getenv('SQL_PORT', '5432')
    }
}


STATICFILES_DIRS = []
PROXY_FRONTEND = None

# Authentication
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']

SITE_NAME = 'IANALYZER'
HOST = 'localhost:8000'

# Download location
_here = os.path.abspath(os.path.dirname(__file__))
_backend_path = os.path.join(_here, '..')
CSV_FILES_PATH = os.path.join(_backend_path, 'download/csv_files')

# Specify elasticsearch servers
SERVERS = {
    # Default ElasticSearch server
    'default': {
        'host': os.getenv('ES_HOST', 'localhost'),
        'port': 9200,
        'chunk_size': 900,  # Maximum number of documents sent during ES bulk operation
        'max_chunk_bytes': 1*1024*1024,  # Maximum size of ES chunk during bulk operation
        'bulk_timeout': '60s',  # Timeout of ES bulk operation
        'scroll_timeout': '3m',  # Time before scroll results time out
        'scroll_page_size': 5000,  # Number of results per scroll page
        'index_prefix': 'ianalyzer'  # Prefix applied to index names created on this server
    }
}

CORPUS_SERVER_NAMES = {}

CORPORA_LOCALES = {}

CORPORA = {}

WORDCLOUD_LIMIT = 1000

# Celery configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER', 'redis://')
CELERY_RESULT_BACKEND = os.getenv('CELERY_BROKER', 'redis://')

# url to the frontend for generating email links
BASE_URL = 'http://localhost:4200'

# list of corpora that have been re-indexed using the top-level term vector
# for main content fields, needed for the new highlighter
NEW_HIGHLIGHT_CORPORA = []

DEFAULT_FROM_EMAIL = 'ianalyzer@ianalyzer.dev'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "indexing": {
            "handlers": ["console"],
            "level": "INFO",
            "propragate": True
        }
    },
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'data')

# This needs to be the last line of the settings.py, so that all settings can be overridden.
try:
    from ianalyzer.settings_local import *
except ImportError as e:
    warnings.warn(
        'No local settings file - configure your environment in backend/ianalyzer/settings_local.py',
        Warning
    )
