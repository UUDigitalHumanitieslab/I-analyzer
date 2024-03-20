import os
import json
import pytest

_here = os.path.abspath(os.path.dirname(__file__))

@pytest.fixture()
def json_corpus_data():
    path = os.path.join(_here, 'tests', 'mock_corpus.json')
    with open(path) as f:
        return json.load(f)
