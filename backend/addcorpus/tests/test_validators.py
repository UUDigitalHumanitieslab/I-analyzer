import pytest
from addcorpus.models import Field
from addcorpus.es_mappings import int_mapping, text_mapping, keyword_mapping, main_content_mapping, date_mapping
from addcorpus.validation.creation import *

def test_validate_mimetype():
    validate_mimetype('image/jpeg')

    with pytest.raises(ValidationError):
        validate_mimetype('nonsense')

def test_validate_es_mapping():
    validate_es_mapping({'type': 'text'})

    with pytest.raises(ValidationError):
        validate_es_mapping({})

    with pytest.raises(ValidationError):
        validate_es_mapping({'type': 'perlocator'})

def test_validate_search_filter():
    validate_search_filter({
        'name': 'RangeFilter',
        'lower': 0,
        'upper': 100,
        'description': '...'
    })

    with pytest.raises(ValidationError):
        validate_search_filter({'name': 'UnkownFilter'})

def test_validate_search_filter_with_mapping():
    filter = {
        'name': 'RangeFilter',
        'lower': 0,
        'upper': 100,
        'description': '...'
    }

    validate_search_filter_with_mapping(int_mapping(), filter)

    with pytest.raises(ValidationError):
        validate_search_filter_with_mapping(keyword_mapping(), filter)

def test_validate_visualizations_with_mapping():
    validate_visualizations_with_mapping(text_mapping(), ['ngram'])
    validate_visualizations_with_mapping(keyword_mapping(), ['resultscount'])
    validate_visualizations_with_mapping(keyword_mapping(enable_full_text_search=True), ['ngram'])

    with pytest.raises(ValidationError):
        validate_visualizations_with_mapping(keyword_mapping(), ['ngram'])

    with pytest.raises(ValidationError):
        validate_visualizations_with_mapping(text_mapping(), ['resultscount'])

def test_validate_searchable_fields_has_fts():
    validate_searchable_field_has_full_text_search(text_mapping(), True)
    validate_searchable_field_has_full_text_search(
        keyword_mapping(enable_full_text_search=True), True
    )
    validate_searchable_field_has_full_text_search(int_mapping(), False)

    with pytest.raises(ValidationError):
        validate_searchable_field_has_full_text_search(int_mapping(), True)

    with pytest.warns(Warning):
        validate_searchable_field_has_full_text_search(keyword_mapping(), True)

def test_validate_sort_configuration():
    validate_sort_configuration({})

    validate_sort_configuration({
        'field': 'date',
        'ascending': False
    })

    with pytest.raises(ValidationError):
        validate_sort_configuration({
            'field': 'date',
            'ascending': None
        })
