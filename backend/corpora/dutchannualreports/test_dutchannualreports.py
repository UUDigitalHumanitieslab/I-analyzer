import os
from corpora.utils_test import corpus_from_api

here = os.path.abspath(os.path.dirname(__file__))

def test_dutchannualreports(settings, db, admin_client):
    settings.CORPORA = {
        'dutchannualreports': os.path.join(here, 'dutchannualreports.py')
    }
    settings.DUTCHANNUALREPORTS_DATA = ''

    corpus = corpus_from_api(admin_client)
    assert corpus['title'] == 'Dutch Annual Reports'
