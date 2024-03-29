from time import sleep

import pytest
import requests
from allauth.account.models import EmailAddress

from ianalyzer.elasticsearch import elasticsearch
from addcorpus.python_corpora.load_corpus import load_corpus_definition
from addcorpus.python_corpora.save_corpus import load_and_save_all_corpora
from es import es_index as index

# user credentials and logged-in api clients
@pytest.fixture
def user_credentials():
    return {'username': 'basic_user',
            'password': 'basic_user',
            'email': 'basicuser@ianalyzer.com'}


@pytest.fixture
def admin_credentials():
    return {'username': 'admin',
            'password': 'admin',
            'email': 'admin@ianalyzer.com'}


@pytest.fixture
def auth_user(django_user_model, user_credentials):
    user = django_user_model.objects.create_user(
        username=user_credentials['username'],
        password=user_credentials['password'],
        email=user_credentials['email'])
    EmailAddress.objects.create(user=user,
                                email=user.email,
                                verified=True,
                                primary=True)
    return user


@pytest.fixture
def auth_client(client, auth_user, user_credentials):
    client.login(
        username=user_credentials['username'],
        password=user_credentials['password'])
    yield client
    client.logout()


@pytest.fixture
def admin_user(django_user_model, admin_credentials):
    user = django_user_model.objects.create_superuser(
        username=admin_credentials['username'],
        password=admin_credentials['password'],
        email=admin_credentials['email'],
        download_limit=1000000)
    return user


@pytest.fixture
def admin_client(client, admin_user, admin_credentials):
    client.login(
        username=admin_credentials['username'],
        password=admin_credentials['password'])
    yield client
    client.logout()

@pytest.fixture(scope='session')
def connected_to_internet():
    """
    Check if there is internet connection. Skip if no connection can be made.
    """
    try:
        requests.get("https://1.1.1.1")
    except:
        pytest.skip('Cannot connect to internet')


# elasticsearch
@pytest.fixture(scope='session')
def es_client():
    """
    Initialise an elasticsearch client for the default elasticsearch cluster. Skip if no connection can be made.
    """

    client = elasticsearch('small-mock-corpus') # based on settings_test.py, this corpus will use cluster 'default'
    # check if client is available, else skip test
    try:
        client.info()
    except:
        pytest.skip('Cannot connect to elasticsearch server')

    return client

# mock corpora
@pytest.fixture(autouse=True)
def add_mock_corpora_to_db(db):
    #add mock corpora to the database at the start of each test
    load_and_save_all_corpora()

def index_test_corpus(es_client, corpus_name):
    corpus = load_corpus_definition(corpus_name)
    index.create(es_client, corpus, False, True, False)
    index.populate(es_client, corpus_name, corpus)

    # ES is "near real time", so give it a second before we start searching the index
    sleep(2)

def clear_test_corpus(es_client, corpus_name):
    corpus = load_corpus_definition(corpus_name)
    index = corpus.es_index
    # check existence in case teardown is executed more than once
    if es_client.indices.exists(index = index):
        es_client.indices.delete(index = index)
