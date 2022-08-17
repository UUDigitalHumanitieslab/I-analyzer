import re
import numpy as np
from wordmodels.decompose import total_alignment_loss, alignment_loss_adjacent_timeframes, initial_coordinates,  pairwise_similarities, similarity_loss
from wordmodels.visualisations import load_word_models, get_2d_contexts_over_time
import pytest

NUMBER_SIMILAR = 5

def find_term(term, interval_result):
    data = interval_result['data']
    return next((item for item in data if item['label'] == term), None)

def test_2d_context_over_time_result(test_app):
    """Test if the context result makes sense."""
    all_data = get_2d_contexts_over_time('she', 'mock-corpus')

    for interval in all_data:
        assert find_term('she', interval)
        assert find_term('her', interval)

    assert find_term('elizabeth', all_data[0])
    assert find_term('alice', all_data[1])

def test_term_not_in_all_intervals(test_app):
    all_data = get_2d_contexts_over_time('alice', 'mock-corpus', NUMBER_SIMILAR)

    # check that each interval returns coordinates for the keyword
    for interval in all_data:
        assert find_term('alice', interval)

    # check that interval 1 includes neighbouring words, but 0 and 2 do not
    keyword_in_model = [all_data[1]]
    keyword_not_in_model = [all_data[0], all_data[2]]

    for interval in keyword_in_model:
        assert len(interval['data']) == NUMBER_SIMILAR + 1

    for interval in keyword_not_in_model:
        assert len(interval['data']) == 1

def test_2d_contexts_over_time_format(test_app):
    term = 'she'

    data = get_2d_contexts_over_time(term, 'mock-corpus')
    assert data and len(data)

    for item in data:
        assert 'time' in item
        assert re.match(r'\d{4}-\d{4}', item['time'])

        assert 'data' in item

        for point_data in item['data']:
            assert set(point_data.keys()) == {'label', 'x', 'y'}
            assert type(point_data['x']) == type(point_data['y']) == float

def test_initial_map():
    vectors_per_timeframe = [
        np.random.rand(3, 4),
        np.random.rand(1, 4),
        np.random.rand(3, 4),
    ]

    terms_per_timeframe = [
        ['a', 'b', 'c'],
        ['a'],
        ['a', 'b', 'd']
    ]

    coordinates_per_timeframe = initial_coordinates(vectors_per_timeframe, terms_per_timeframe)

    assert len(coordinates_per_timeframe) == len(terms_per_timeframe)

    for coordinates, terms in zip(coordinates_per_timeframe, terms_per_timeframe):
        assert coordinates.shape == (len(terms), 2)


def test_pairwise_similarities():
    vectors = np.array([
        [1.0, 1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0, 0.0],
        [1.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0, 1.0]
    ])

    similarities = pairwise_similarities(vectors)

    assert similarities.size == 6

    assert round(similarities[0], 5) == 1.0
    assert round(similarities[1], 5) == 0.5
    assert round(similarities[2], 5) == 0.0

def test_similarity_loss():

    X_identical = np.array([
        [1.0, 1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0, 0.0]
    ])

    X_orthagonal = np.array([
        [0.0, 0.0, 1.0, 1.0],
        [1.0, 1.0, 0.0, 0.0]
    ])

    y_identical = np.array([
        [1.0, 0.0],
        [1.0, 0.0]
    ])

    y_mixed = np.array([
        [1.0, 0.0],
        [0.5, 0.5]
    ])

    y_orthagonal = np.array([
        [1.0, 0.0],
        [0.0, 1.0]
    ])

    assert similarity_loss(X_identical, y_identical) < similarity_loss(X_identical, y_mixed)
    assert similarity_loss(X_identical, y_identical) < similarity_loss(X_identical, y_orthagonal)

    assert similarity_loss(X_orthagonal, y_orthagonal) < similarity_loss(X_orthagonal, y_identical)
    assert similarity_loss(X_orthagonal, y_orthagonal) < similarity_loss(X_orthagonal, y_mixed)

def test_alignment_loss_adjacent_timeframes():

    coordinates_1 = np.array([
        [1.0, 0.0],
        [0.0, 1.0]
    ])

    coordinates_2 = np.array([
        [0.0, 1.0],
        [1.0, 0.0],
    ])

    terms_1 = ['a', 'b']
    terms_2 = ['b', 'a']

    assert alignment_loss_adjacent_timeframes(coordinates_1, terms_1, coordinates_2, terms_2) == 0.0
    assert alignment_loss_adjacent_timeframes(coordinates_1, terms_1, coordinates_2, terms_1) == 1.0

    terms_2_alt = ['c', 'a']
    assert alignment_loss_adjacent_timeframes(coordinates_1, terms_1, coordinates_2, terms_2_alt) == 0.0

    coordinates_2_alt = np.array([
        [0.0, 1.0],
        [1.0, 0.5],
    ])
    assert alignment_loss_adjacent_timeframes(coordinates_1, terms_1, coordinates_2_alt, terms_2) == 0.0625

def test_alignment_loss():
    coordinates = [
        np.array([
            [1.0, 0.0],
            [0.0, 1.0]
        ]),
        np.array([
            [0.0, 1.0],
            [1.0, 0.0],
        ]),
        np.array([
            [0.0, 1.0],
            [1.0, 0.5],
        ])
    ]

    terms = [
        ['a', 'b'],
        ['b', 'a'],
        ['b', 'a']
    ]

    assert total_alignment_loss(coordinates, terms) == 0.0625
    assert total_alignment_loss(coordinates[:2], terms[:2]) == 0.0
