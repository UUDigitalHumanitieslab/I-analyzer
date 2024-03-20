from addcorpus.json_corpora.utils import get_path

def test_get_path():
    data = {'a': 'b'}
    assert get_path(data, 'a') == 'b'
    assert get_path(data, 'x') == None

    data = {'a': { 'b': 'c' }}
    assert get_path(data, 'a', 'b') == 'c'
