from typing import Dict, Iterable
from datetime import datetime

from addcorpus.models import Corpus, CorpusConfiguration, Field
from addcorpus.json_corpora.utils import get_path, has_path
from addcorpus import es_mappings
from addcorpus.constants import VisualizationType
from addcorpus.validation.publishing import _any_date_fields

def import_json_corpus(data: Dict) -> Corpus:
    name = get_path(data, 'name')

    corpus, _created = Corpus.objects.get_or_create(name=name)

    configuration = _parse_configuration(data)
    configuration.corpus = corpus
    configuration.full_clean()
    configuration.save()

    _import_fields(data, configuration)

    return corpus

def _parse_configuration(data: Dict) -> CorpusConfiguration:
    title = get_path(data, 'meta', 'title')
    description = get_path(data, 'meta', 'description')
    category = get_path(data, 'meta', 'category')
    es_index = get_path(data, 'name')
    image = 'missing.png' # TODO: fix this
    languages = get_path(data, 'meta', 'languages')
    min_date = _parse_date(get_path(data, 'meta', 'date_range', 'min'))
    max_date = _parse_date(get_path(data, 'meta', 'date_range', 'max'))
    default_sort = get_path(data, 'options', 'default_sort') or {}
    language_field = get_path(data, 'options', 'language_field') or ''
    document_context = get_path(data, 'options', 'document_context') or {}
    return CorpusConfiguration(
        title=title,
        description=description,
        category=category,
        es_index=es_index,
        image=image,
        languages=languages,
        min_date=min_date,
        max_date=max_date,
        default_sort=default_sort,
        language_field=language_field,
        document_context=document_context,
    )

def _parse_date(date: str):
    return datetime.strptime(date, '%Y-%m-%d').date()

def _import_fields(data: Dict, configuration: CorpusConfiguration) -> None:
    fields_data = get_path(data, 'fields')

    for field_data in fields_data:
        field = _parse_field(field_data)
        field.corpus_configuration = configuration
        field.full_clean()
        field.save()

    _include_ngram_visualisation(configuration.fields.all())

def _parse_field(field_data: Dict) -> Field:
    name = get_path(field_data, 'name')
    display_name = get_path(field_data, 'display_name')
    description = get_path(field_data, 'description')
    results_overview = get_path(field_data, 'options', 'preview')
    hidden = get_path(field_data, 'options', 'hidden')

    field = Field(
        name=name,
        display_name=display_name,
        description=description,
        results_overview=results_overview,
        hidden=hidden,
        csv_core=results_overview,
    )

    field_type = get_path(field_data, 'type')
    parsers = {
        'text_content': _parse_text_content_field,
        'text_metadata': _parse_text_metadata_field,
        'url': _parse_url_field,
        'integer': _parse_numeric_field,
        'float': _parse_numeric_field,
        'date': _parse_date_field,
        'boolean': _parse_boolean_field,
        'geo_json': _parse_geo_field,
    }
    field = parsers[field_type](field, field_data)

    return field

def _parse_text_content_field(field: Field, field_data: Dict) -> Field:
    language = _parse_language(field_data)
    has_single_language = language and language != 'dynamic'

    field.es_mapping = es_mappings.main_content_mapping(
        token_counts=True,
        stopword_analysis=has_single_language,
        stemming_analysis=has_single_language,
        language=language if has_single_language else None,
    )
    field.language = language
    field.display_type = 'text_content'
    field.search_filter = {}
    field.searchable = True
    field.search_field_core = True

    visualize = get_path(field_data, 'options', 'visualize')
    if visualize:
        field.visualizations = [
            VisualizationType.WORDCLOUD.value
        ]

    return field

def _parse_text_metadata_field(field: Field, field_data: Dict) -> Field:
    searchable = get_path(field_data, 'options', 'search')
    filter_setting = get_path(field_data, 'options', 'filter')
    filterable = filter_setting != 'none'
    sortable = get_path(field_data, 'options', 'sort')
    visualize = get_path(field_data, 'options', 'visualize')

    field.language = _parse_language(field_data)

    if searchable and not (sortable or filterable):
        field.es_mapping = es_mappings.text_mapping()
        field.display_type = 'text'
        field.search_filter = {}
        field.searchable = True
        if visualize:
            field.visualizations = [
                VisualizationType.WORDCLOUD.value
            ]
    else:
        field.es_mapping = es_mappings.keyword_mapping(
            enable_full_text_search=searchable
        )
        field.display_type = 'keyword'
        if filter_setting == 'show':
            field.search_filter = {
                'name': 'MultipleChoiceFilter',
                'description': f'Select results based on {field.display_name}',
            }
        else:
            field.search_filter = {}
        field.searchable = searchable
        field.sortable = sortable
        if visualize:
            field.visualizations = [
                VisualizationType.RESULTS_COUNT.value,
                VisualizationType.TERM_FREQUENCY.value,
            ]

    return field

def _parse_language(field_data: Dict) -> str:
    return get_path(field_data, 'language') or ''

def _parse_url_field(field: Field, field_data: Dict) -> Field:
    field.es_mapping = es_mappings.keyword_mapping()
    field.display_type = 'keyword'
    field.search_filter = {}
    return field

def _parse_numeric_field(field: Field, field_data: Dict) -> Field:
    field.display_type = get_path(field_data, 'type')

    if field.display_type == 'integer':
        field.es_mapping = es_mappings.int_mapping()
    else:
        field.es_mapping = es_mappings.float_mapping()

    field.sortable = get_path(field_data, 'options', 'sort')

    filter_setting = get_path(field_data, 'options', 'filter')
    if filter_setting == 'show':
        field.search_filter = {
            'name': 'RangeFilter',
            'description': f'Select results based on {field.display_name}',
        }
    else:
        field.search_filter = {}

    visualize = get_path(field_data, 'options', 'visualize')
    if visualize:
        field.visualizations = [
            VisualizationType.RESULTS_COUNT.value,
            VisualizationType.TERM_FREQUENCY.value
        ]
        field.visualization_sort = 'key'
    return field

def _parse_date_field(field: Field, field_data: Dict) -> Field:
    field.display_type = 'date'
    field.es_mapping = es_mappings.date_mapping()
    field.sortable = get_path(field_data, 'options', 'sort')
    filter_setting = get_path(field_data, 'options', 'filter')

    if filter_setting == 'show':
        field.search_filter = {
            'name': 'DateFilter',
            'description': f'Select results based on {field.display_name}',
        }
    else:
        field.search_filter = {}

    visualize = get_path(field_data, 'options', 'visualize')
    if visualize:
        field.visualizations = [
            VisualizationType.RESULTS_COUNT.value,
            VisualizationType.TERM_FREQUENCY.value
        ]
    return field

def _parse_boolean_field(field: Field, field_data: Dict) -> Field:
    field.display_type = 'boolean'
    field.es_mapping = es_mappings.bool_mapping()
    filter_setting = get_path(field_data, 'options', 'filter')

    if filter_setting == 'show':
        field.search_filter = {
            'name': 'BooleanFilter',
            'description': f'Select results based on {field.display_name}',
        }
    else:
        field.search_filter = {}

    visualize = get_path(field_data, 'options', 'visualize')
    if visualize:
        field.visualizations = [
            VisualizationType.RESULTS_COUNT.value,
            VisualizationType.TERM_FREQUENCY.value
        ]
    return field

def _parse_geo_field(field: Field, field_data: Dict) -> Field:
    field.display_type = 'keyword'
    field.es_mapping = es_mappings.geo_mapping()
    field.search_filter = {}
    return field

def _include_ngram_visualisation(fields: Iterable[Field]):
    '''
    Check if the ngram visualisation can be included and add it if possible.

    This can't be done in the initial parse because you have to check if a date
    field is present.
    '''

    if _any_date_fields(fields):
        for field in fields:
            if field.display_type == 'text_content':
                field.visualizations.append(VisualizationType.NGRAM.value)
                field.save()
