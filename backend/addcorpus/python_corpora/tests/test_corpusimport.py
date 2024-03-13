import os
import pytest
from addcorpus.python_corpora import load_corpus
from addcorpus.models import Corpus

def test_key_error(db, settings):
    ''' Verify that exception is correctly raised
    - in case the config.CORPORA variable is empty
    '''

    settings.CORPORA = {}

    with pytest.raises(KeyError) as e:
        corpora = load_corpus.load_all_corpus_definitions()
        corpora['times']

def test_import_error(db, settings):
    ''' Verify that exceptions is correctly raised
    - in case the file path in config.CORPORA is faulty
    '''

    settings.CORPORA = {'times2': '/somewhere/times/times.py'}

    with pytest.raises(FileNotFoundError) as e:
        load_corpus.load_corpus_definition('times2')

    # corpus should not be included when
    # loading all corpora
    corpora = load_corpus.load_all_corpus_definitions()
    assert 'times2' not in corpora
    assert not Corpus.objects.filter(name='times2')

mock_corpus_definition = '''
class Times():
    title = "Times"
    description = "Newspaper archive, 1785-2010"
    fields = []
    es_index = 'some-other-name'
'''

@pytest.fixture()
def temp_times_definition(tmpdir, settings):
    '''Provide a temporary definition files for the
    times corpus
    '''
    testdir = tmpdir.mkdir('/testdir')

    with open(os.path.join(testdir, 'times.py'), 'w') as f:
        f.write(mock_corpus_definition)
    path_testfile = str(testdir)+'/times.py'

    settings.CORPORA = {'times': path_testfile}

def test_import_from_anywhere(db, temp_times_definition):
    ''' Verify that the corpus definition
    can live anywhere in the file system
    '''
    corpus_definitions = load_corpus.load_all_corpus_definitions()
    assert 'times' in corpus_definitions
    corpus = corpus_definitions['times']
    assert corpus.title == 'Times'

def test_corpus_dir_is_absolute(db, temp_times_definition):
    corpus_dir = load_corpus.corpus_dir('times')
    assert os.path.isabs(corpus_dir)

def test_mismatch_corpus_index_names(temp_times_definition):
    times = load_corpus.load_corpus_definition('times')
    assert times.es_index == 'some-other-name'
