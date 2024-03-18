from ianalyzer.settings import *


def path_in_testdir(app, *path_from_app_tests):
    return os.path.join(BASE_DIR, app, 'tests', *path_from_app_tests)


CORPORA = {
    'small-mock-corpus': path_in_testdir('visualization', 'mock_corpora', 'small_mock_corpus.py'),
    'large-mock-corpus': path_in_testdir('visualization', 'mock_corpora', 'large_mock_corpus.py'),
    'multilingual-mock-corpus': path_in_testdir('download', 'mock_corpora', 'multilingual_mock_corpus.py'),
    'times': os.path.join(BASE_DIR, 'corpora', 'times', 'times.py'),
    'media-mock-corpus': path_in_testdir('media', 'media_mock_corpus.py'),
    'mock-csv-corpus': path_in_testdir('addcorpus', 'mock_csv_corpus.py'),
    'mock-basic-corpus': path_in_testdir('addcorpus', 'mock_basic_corpus.py'),
    'wordmodels-mock-corpus': path_in_testdir('wordmodels', 'mock-corpus', 'mock_corpus.py'),
    'tagging-mock-corpus': path_in_testdir('tag', 'tag_mock_corpus.py'),
}

TIMES_DATA = path_in_testdir('addcorpus', '../python_corpora/tests')
TIMES_ES_INDEX = 'times-test'
