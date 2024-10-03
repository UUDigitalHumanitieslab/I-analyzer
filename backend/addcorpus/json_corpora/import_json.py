from typing import List, Dict, Iterable, Optional
from datetime import date, datetime


from addcorpus.models import Field
from addcorpus.json_corpora.utils import get_path
from addcorpus import es_mappings
from addcorpus.constants import VisualizationType
from django.conf import settings
from addcorpus.json_corpora.constants import DEFAULT_CSV_DELIMITER, DATE_FORMAT, DEFAULT_MAX_DATE, DEFAULT_MIN_DATE

def import_json_corpus(data: Dict) -> Dict:
    name = get_path(data, 'name')

    return {
        'name': name,
        'configuration': _parse_configuration(data)
    }

def create_index_name(corpus_name: str) -> str:
    prefix = settings.SERVERS['default'].get('index_prefix', None)
    if prefix:
        return f'{prefix}-{corpus_name}'
    return corpus_name


def _parse_configuration(data: Dict) -> Dict:
    return {
        'title': get_path(data, 'meta', 'title'),
        'description': get_path(data, 'meta', 'description'),
        'category': get_path(data, 'meta', 'category'),
        'es_index': create_index_name(get_path(data, 'name')),
        'languages': get_path(data, 'meta', 'languages'),
        'min_date': _parse_date(
            get_path(data, 'meta', 'date_range', 'min'), DEFAULT_MIN_DATE),
        'max_date': _parse_date(
            get_path(data, 'meta', 'date_range', 'max'), DEFAULT_MAX_DATE),
        'default_sort': get_path(
            data, 'options', 'default_sort') or {},
        'language_field': get_path(
            data, 'options', 'language_field') or '',
        'document_context': get_path(
            data, 'options', 'document_context') or {},
        'source_data_delimiter': get_path(
            data, 'source_data', 'options', 'delimiter') or DEFAULT_CSV_DELIMITER,
        'fields': _import_fields(data),
    }


def _parse_date(date: Optional[str], fallback: Optional[date]):
    if not date:
        return fallback
    return datetime.strptime(date, DATE_FORMAT).date()


def _import_fields(data: Dict) -> List[Dict]:
    fields_data = get_path(data, 'fields')

    parsed = [_parse_field(field) for field in fields_data]

    # TODO: replace this!!!!
    # for field in configuration.fields.exclude(name__in=(f['name'] for f in fields_data)):
    #     field.delete()

    _include_ngram_visualisation(parsed)
    return parsed


def _parse_field(field_data: Dict) -> Dict:
    results_overview = get_path(field_data, 'options', 'preview')
    parsed = {
        'name': get_path(field_data, 'name'),
        'display_name': get_path(field_data, 'display_name'),
        'description': get_path(field_data, 'description'),
        'results_overview': results_overview,
        'hidden': get_path(field_data, 'options', 'hidden'),
        'extract_column': get_path(field_data, 'extract', 'column'),
        'csv_core': results_overview,
    }

    field_type = get_path(field_data, 'type')
    parsers = {
        'text_content': _parse_text_content_field,
        'text_metadata': _parse_text_metadata_field,
        'url': _parse_url_field,
        'integer': _parse_numeric_field,
        'float': _parse_numeric_field,
        'date': _parse_date_field,
        'boolean': _parse_boolean_field,
        'geo_point': _parse_geo_field,
    }
    type_specific_data = parsers[field_type](field_data)
    parsed.update(type_specific_data)
    return parsed


def _parse_text_content_field(field_data: Dict) -> Field:
    language = _parse_language(field_data)
    has_single_language = language and language != 'dynamic'

    parsed = {
        'es_mapping': es_mappings.main_content_mapping(
            token_counts=True,
            stopword_analysis=has_single_language,
            stemming_analysis=has_single_language,
            language=language if has_single_language else None,
        ),
        'language': language,
        'display_type': 'text_content',
        'search_filter': {},
        'searchable': True,
        'search_field_core': True,
    }

    visualize = get_path(field_data, 'options', 'visualize')
    if visualize:
        parsed['visualizations'] = [
            VisualizationType.WORDCLOUD.value
        ]

    return parsed


def _parse_text_metadata_field(field_data: Dict) -> Dict:
    searchable = get_path(field_data, 'options', 'search')
    filter_setting = get_path(field_data, 'options', 'filter')
    filterable = filter_setting != 'none'
    sortable = get_path(field_data, 'options', 'sort')
    visualize = get_path(field_data, 'options', 'visualize')

    parsed = {
        'language': _parse_language(field_data)
    }

    if searchable and not (sortable or filterable):
        parsed['es_mapping'] = es_mappings.text_mapping()
        parsed['display_type'] = 'text'
        parsed['search_filter'] = {}
        parsed['searchable'] = True
        if visualize:
            parsed['visualizations'] = [
                VisualizationType.WORDCLOUD.value
            ]
    else:
        parsed['es_mapping'] = es_mappings.keyword_mapping(
            enable_full_text_search=searchable
        )
        parsed['display_type'] = 'keyword'
        if filter_setting == 'show':
            parsed['search_filter'] = {
                'name': 'MultipleChoiceFilter',
                'description': f'Select results based on {field_data["display_name"]}',
            }
        else:
            parsed['search_filter'] = {}
        parsed['searchable'] = searchable
        parsed['sortable'] = sortable
        if visualize:
            parsed['visualizations'] = [
                VisualizationType.RESULTS_COUNT.value,
                VisualizationType.TERM_FREQUENCY.value,
            ]

    return parsed


def _parse_language(field_data: Dict) -> str:
    return get_path(field_data, 'language') or ''


def _parse_url_field(_field_data: Dict) -> Dict:
    parsed = {
        'es_mapping': es_mappings.keyword_mapping(),
        'display_type': 'url',
        'search_filter': {},
    }
    return parsed

def _parse_numeric_field(field_data: Dict) -> Dict:
    parsed = {
        'display_type': get_path(field_data, 'type')
    }

    if parsed['display_type'] == 'integer':
        parsed['es_mapping'] = es_mappings.int_mapping()
    else:
        parsed['es_mapping'] = es_mappings.float_mapping()

    parsed['sortable'] = get_path(field_data, 'options', 'sort')

    filter_setting = get_path(field_data, 'options', 'filter')
    if filter_setting == 'show':
        parsed['search_filter'] = {
            'name': 'RangeFilter',
            'description': f'Select results based on {field_data["display_name"]}',
        }
    else:
        parsed['search_filter'] = {}

    visualize = get_path(field_data, 'options', 'visualize')
    if visualize:
        parsed['visualizations'] = [
            VisualizationType.RESULTS_COUNT.value,
            VisualizationType.TERM_FREQUENCY.value
        ]
        parsed['visualization_sort'] = 'key'
    return parsed


def _parse_date_field(field_data: Dict) -> Dict:
    filter_setting = get_path(field_data, 'options', 'filter')

    parsed = {
        'display_type': 'date',
        'es_mapping': es_mappings.date_mapping(),
        'sortable': get_path(field_data, 'options', 'sort'),

    }

    if filter_setting == 'show':
        parsed['search_filter'] = {
            'name': 'DateFilter',
            'description': f'Select results based on {field_data["display_name"]}',
        }
    else:
        parsed['search_filter'] = {}

    visualize = get_path(field_data, 'options', 'visualize')
    if visualize:
        parsed['visualizations'] = [
            VisualizationType.RESULTS_COUNT.value,
            VisualizationType.TERM_FREQUENCY.value
        ]
    return parsed


def _parse_boolean_field(field_data: Dict) -> Dict:
    parsed = {
        'display_type': 'boolean',
        'es_mapping': es_mappings.bool_mapping(),
    }

    filter_setting = get_path(field_data, 'options', 'filter')

    if filter_setting == 'show':
        parsed['search_filter'] = {
            'name': 'BooleanFilter',
            'description': f'Select results based on {field_data["display_name"]}',
        }
    else:
        parsed['search_filter'] = {}

    visualize = get_path(field_data, 'options', 'visualize')
    if visualize:
        parsed['visualizations'] = [
            VisualizationType.RESULTS_COUNT.value,
            VisualizationType.TERM_FREQUENCY.value
        ]
    return parsed


def _parse_geo_field(field_data: Dict) -> Dict:
    return {
        'display_type': 'geo_point',
        'es_mapping': es_mappings.geo_mapping(),
        'search_filter': {},
    }


def _include_ngram_visualisation(fields: Iterable[Dict]) -> None:
    '''
    Check if the ngram visualisation can be included and add it if possible.

    This can't be done in the initial parse because you have to check if a date
    field is present.
    '''

    if any(get_path(field, 'es_mapping', 'type') == 'date' for field in fields):
        for field in fields:
            if field['display_type'] == 'text_content':
                field['visualizations'].append(VisualizationType.NGRAM.value)
