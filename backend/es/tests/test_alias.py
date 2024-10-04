from addcorpus.models import Corpus
from es.es_alias import alias, get_highest_version_number


def test_alias(db, es_alias_client):
    corpus = Corpus.objects.get(name='times')
    assert corpus.configuration.es_index == 'times-test'
    alias(corpus)  # create an alias ianalyzer-times
    res = es_alias_client.indices.get_alias(name=corpus.configuration.es_index)
    assert res.get('times-test-2') is not None


def test_alias_with_clean(es_alias_client):
    corpus = Corpus.objects.get(name='times')
    indices = es_alias_client.indices.get(
        index='{}-*'.format(corpus.configuration.es_index))
    assert 'times-test-1' in list(indices.keys())
    alias(corpus, True)
    indices = es_alias_client.indices.get(
        index='{}-*'.format(corpus.configuration.es_index))
    assert 'times-test-1' not in list(indices.keys())


def test_highest_version_number(es_alias_client):
    corpus = Corpus.objects.get(name='times')
    indices = es_alias_client.indices.get(
        index='{}-*'.format(corpus.configuration.es_index))
    current_index = 'times-test'
    num = get_highest_version_number(indices, current_index)
    assert num == 2
    current_index = "fantasy-index-name"
    indices = es_alias_client.indices.get(index="{}-*".format(current_index))
    num = get_highest_version_number(indices, current_index)
    assert num == 0
