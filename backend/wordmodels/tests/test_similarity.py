from copy import deepcopy
import pytest
from gensim.models import KeyedVectors

import wordmodels.similarity as similarity
from wordmodels.visualisations import load_word_models

def test_term_similarity(mock_corpus):
    case = {
        'term': 'elizabeth',
        'similar_term': 'she',
        'less_similar': 'he',
        'uppercase_term': 'She'
    }
    binned_models = load_word_models(mock_corpus)
    model = binned_models[0]

    similarity1 = similarity.term_similarity(model, case['term'], case['similar_term'])
    assert type(similarity1) == float

    similarity2 = similarity.term_similarity(model, case['term'], case['less_similar'])

    assert similarity1 > similarity2

    similarity3 = similarity.term_similarity(model, case['term'], case['uppercase_term'])
    assert similarity1 == similarity3

def test_n_nearest_neighbours_amount(mock_corpus):

    for n in range(1, 16, 5):
        term = 'elizabeth'
        binned_models = load_word_models(mock_corpus)
        model = binned_models[0]

        result = similarity.find_n_most_similar(model, term, n)
        assert len(result) == n

@pytest.fixture
def model_with_term_removed(mock_corpus):
    binned_models = load_word_models(mock_corpus)
    original_model = binned_models[0]

    term = 'darcy'
    vocab = deepcopy(original_model['vectors'].index_to_key)
    vocab.remove(term)

    new_vectors = KeyedVectors(original_model['vectors'].vector_size)
    new_vectors.add_vectors(
            vocab, [original_model['vectors'][word] for word in vocab])
    new_model = {'vectors': new_vectors}

    return new_model, original_model, term, vocab

def test_vocab_is_subset_of_model(model_with_term_removed):
    '''Test cases where the vocab array is a subset of terms with vectors.'''

    model, original_model, missing_term, vocab = model_with_term_removed
    assert missing_term not in vocab

    other_term = 'elizabeth'

    # there SHOULD be a score for the original model...
    similarity_score = similarity.term_similarity(original_model, missing_term, other_term)
    assert similarity_score != None

    # ... but not with the adjusted vocab
    similarity_score = similarity.term_similarity(model, missing_term, other_term)
    assert similarity_score == None

    # term should be included in nearest neighbours with original model...
    similar_term = 'bingley'
    neighbours = similarity.find_n_most_similar(original_model, similar_term, 10)
    assert any([neighbour['key'] == missing_term for neighbour in neighbours])
    assert len(neighbours) == 10

    # ... but not with the adjusted vocab
    neighbours = similarity.find_n_most_similar(model, similar_term, 10)
    assert not any([neighbour['key'] == missing_term for neighbour in neighbours])
    assert len(neighbours) == 10
