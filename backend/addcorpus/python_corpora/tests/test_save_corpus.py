import sys
import pytest
from django.conf import settings
from addcorpus.tests.mock_csv_corpus import MockCSVCorpus
from addcorpus.models import Corpus, CorpusConfiguration
from addcorpus.python_corpora.save_corpus import _save_field_in_database, \
    load_and_save_all_corpora, _save_or_skip_corpus


def test_saved_corpora(db):
    '''
    Assert that all the mock corpora are saved to the database
    during test setup
    '''

    configured = settings.CORPORA

    for corpus_name in configured:
        assert Corpus.objects.filter(name=corpus_name).exists()
        corpus = Corpus.objects.get(name=corpus_name)
        assert corpus.has_configuration

    assert len(Corpus.objects.all()) == len(configured)
    assert len(CorpusConfiguration.objects.all()) == len(configured)

def test_no_errors_when_saving_corpora(db, capsys):
    # try running the save function
    # sys.stdout/stderr needs to be passed explicitly for capture to work
    load_and_save_all_corpora(verbose=True, stdout=sys.stdout, stderr=sys.stderr)
    captured = capsys.readouterr()

    # assert no errors are logged
    assert not captured.err

    # assert stdout contains only success statements
    for line in captured.out.split('\n'):
        assert line == '' or line.startswith('Saved corpus:')

def test_saving_broken_corpus(db, mock_corpus):
    corpus = Corpus.objects.get(name=mock_corpus)
    corpus_def = MockCSVCorpus()

    corpus_def.min_date = 'Not a valid date'

    _save_or_skip_corpus(mock_corpus, corpus_def)

    corpus.refresh_from_db()
    # expect the the corpus to be inactive now
    assert corpus.active == False

def test_remove_corpus_from_settings(db, settings, mock_corpus):
    corpus = Corpus.objects.get(name=mock_corpus)
    assert corpus.has_configuration

    path = settings.CORPORA.pop(mock_corpus)
    load_and_save_all_corpora()
    corpus.refresh_from_db()
    assert not corpus.active

    settings.CORPORA[mock_corpus] = path
    load_and_save_all_corpora()
    corpus.refresh_from_db()
    assert corpus.active

@pytest.fixture()
def deactivated_corpus(mock_corpus):
    corpus = Corpus.objects.get(name=mock_corpus)
    corpus.active = False
    corpus.save()

    yield corpus

    corpus.active = True
    corpus.save()

def test_save_field_definition(db, mock_corpus, deactivated_corpus):
    corpus = Corpus.objects.get(name=mock_corpus)
    corpus_conf = corpus.configuration
    corpus_def = MockCSVCorpus()

    corpus_conf.fields.all().delete()

    for field_def in corpus_def.fields:
        field = _save_field_in_database(field_def, corpus_conf)
        assert field
        assert field.name == field_def.name

def test_save_corpus_purity(db, mock_corpus):
    '''
    Test that saved corpus configurations only depend
    on the definition at that time, not on the currently
    saved state
    '''

    corpus = Corpus.objects.get(name=mock_corpus)
    corpus_def = MockCSVCorpus()

    corpus_def.description_page = 'test.md'
    _save_or_skip_corpus(mock_corpus, corpus_def)
    corpus.refresh_from_db()
    assert corpus.configuration.description_page == 'test.md'

    corpus_def.description_page = None
    _save_or_skip_corpus(mock_corpus, corpus_def)
    corpus.refresh_from_db()
    assert not corpus.configuration.description_page
