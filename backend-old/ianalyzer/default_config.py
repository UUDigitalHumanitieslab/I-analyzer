'''
Configuration.
'''

import logging
import binascii
from os import urandom
from os.path import expanduser, realpath, join, relpath
from datetime import datetime, timedelta

# Flask
DEBUG = False
TESTING = False
# set to a fixed value to retain sessions after a server reset
# Python >= 3.5 urandom(24)
SECRET_KEY = binascii.hexlify(urandom(24))
SERVER_NAME = 'localhost:4200'

# CSRF Token
CSRF_COOKIE_NAME = 'csrf_token'
CSRF_HEADER_NAME = 'X-XSRF-TOKEN'

# SAML
SAML_FOLDER = "saml"
SAML_SOLISID_KEY = "uuShortID"
SAML_MAIL_KEY = "mail"

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost:3306/ianalyzer'
SQLALCHEMY_TRACK_MODIFICATIONS = False

LOG_CONFIG = 'logging.json'

# the corpora dictionary provides the file path of the corpus definition
# this information can be anywhere on the file system
CORPORA = {
    'times': 'corpora/times/times.py'
}

IMAGE_PATH = 'images'
DESCRIPTION_PATH = 'description'
DOCUMENT_PATH = 'documents'
WM_PATH = 'wm'

# Specify indexing servers here
SERVERS = {
    # Default ElasticSearch server
    'default': {
        'host': 'localhost',
        'port': 9200,
        'username': '',
        'password': '',
        'chunk_size': 900,  # Maximum number of documents sent during ES bulk operation
        'max_chunk_bytes': 1*1024*1024,  # Maximum size of ES chunk during bulk operation
        'bulk_timeout': '60s',  # Timeout of ES bulk operation
        'overview_query_size': 20,  # Number of results to appear in the overview query
        'scroll_timeout': '3m',  # Time before scroll results time out
        'scroll_page_size': 5000  # Number of results per scroll page
    }
}

# Example configuration for the mail server
# Copy to your local config.py!
# MAIL_SERVER = 'localhost'
# MAIL_PORT = 25
# MAIL_USE_TLS = False
# MAIL_USE_SSL = False
# MAIL_USERNAME = ''
# MAIL_PASSWORD = ''
# MAIL_FROM_ADRESS='example@dhlab.nl'
# MAIL_REGISTRATION_SUBJECT_LINE='Thank you for signing up at I-analyzer'
# MAIL_CSV_SUBJECT_LINE='Your I-analyzer csv file is ready'
# BASE_URL='http://localhost:4200'
# LOGO_LINK='http://dhstatic.hum.uu.nl/logo-lab/png/dighum-logo.png'

# Specify which corpora are not using the default server
CORPUS_SERVER_NAMES = {
    'times': 'default',
}

CORPUS_DEFINITIONS = {}

###### CORPUS VARIABLES #######

DUTCHANNUALREPORTS_DESCRIPTION_PAGE = 'dutchannualreports.md'
DUTCHANNUALREPORTS_SCAN_IMAGE_TYPE = 'application/pdf'
DUTCHANNUALREPORTS_ALLOW_IMAGE_DOWNLOAD = True
DUTCHANNUALREPORTS_MAP = {}
DUTCHANNUALREPORTS_MAP_FILE = 'dutchannualreports_mapping.csv'
DUTCHANNUALREPORTS_WM = None

DUTCHNEWSPAPERS_TITLES_FILE = 'newspaper_titles.txt'
DUTCHNEWSPAPERS_ES_INDEX = 'dutchnewspapers-public'
DUTCHNEWSPAPERS_DATA = '/directory/to/data'  # remember to set this in config.py

DUTCHNEWSPAPERS_ALL_ES_INDEX = 'dutchnewspapers-all'
# remember to set this in config.py
DUTCHNEWSPAPERS_ALL_DATA = '/directory/to/data'

GOODREADS_DESCRIPTION_PAGE = 'goodreads.md'

TIMES_ES_INDEX = 'times'
TIMES_DATA = '/mnt/times'
TIMES_SCAN_IMAGE_TYPE = 'image/png'
TIMES_DESCRIPTION_PAGE = 'times.md'

TML_ES_INDEX = 'tml'
TML_DATA = '/mnt/tml'

TROONREDES_WM = None

GO_SCAN_IMAGE_TYPE = 'application/pdf'

ECCO_DATA = '/directory/to/data'  # remember to set this in config.py
ECCO_SCAN_IMAGE_TYPE = 'application/pdf'

PERIODICALS_SCAN_IMAGE_TYPE = 'image/jpeg'
PERIODICALS_DESCRIPTION_PAGE = '19thCenturyUKPeriodicals.md'


PP_UK_WM = None
PP_DE_WM = None
PP_FR_WM = None
PP_CA_WM = None
PP_NL_WM = None

#################

# Celery configuration
CELERY_BROKER_URL = 'redis://'
CELERY_BACKEND = 'redis://'
CSV_FILES_PATH = '<abs_path_to_backend>/api/csv_files'

MAIL_CSV_SUBJECT_LINE = 'I-Analyzer download'

WORDCLOUD_LIMIT = 10000
