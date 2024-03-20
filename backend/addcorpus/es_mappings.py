from addcorpus.es_settings import add_language_string

def main_content_mapping(token_counts=True, stopword_analysis=False, stemming_analysis=False, language=None, updated_highlighting=True):
    '''
    Mapping for the main content field. Options:

    - `token_counts`: enables aggregations for the total number of words. Used for relative term frequencies.
    - `stopword_analysis`: enables analysis using stopword removal.
    - `stemming_analysis`: enables analysis using stemming.
    - `updated_highlighting`: enables the new highlighter, which only works for fields that are indexed with the term vector set to 'with_positions_offsets'.
    '''

    mapping = {
        'type': 'text'
    }

    if updated_highlighting:
        mapping.update({
        'term_vector': 'with_positions_offsets' # include char positions on _source (in addition to the multifields) for highlighting
    })

    if any([token_counts, stopword_analysis, stemming_analysis]):
        multifields = {}
        if token_counts:
            multifields['length'] = {
                "type":     "token_count",
                "analyzer": "standard"
            }
        if stopword_analysis:
            multifields['clean'] = {
                "type": "text",
                "analyzer": add_language_string('clean', language),
                "term_vector": "with_positions_offsets" # include character positions for highlighting
            }
        if stemming_analysis:
            multifields['stemmed'] = {
                "type": "text",
                "analyzer": add_language_string('stemmed', language),
                "term_vector": "with_positions_offsets",
            }
        mapping['fields'] = multifields

    return mapping


def text_mapping():
    '''
    Mapping for text fields that are not the main content. Performs tokenisation and lowercasing for full-text
    search, but does not support other analysis options.
    '''

    return {
        'type': 'text'
    }

def keyword_mapping(enable_full_text_search = False):
    '''
    Mapping for keyword fields. Keyword fields allow filtering and histogram visualisations.

    They do not have full text search by default. Set `enable_full_text_search = True` if you want this field to be searchable as well as filterable.
    '''

    mapping = {
        'type': 'keyword'
    }
    if enable_full_text_search:
        mapping['fields'] = {
            'text': { 'type': 'text' },
        }

    return mapping

def date_mapping(format='yyyy-MM-dd'):
    return {
        'type': 'date',
        'format': format
    }

def date_estimate_mapping(format='yyyy-MM-dd'):
    return {
        'type': 'date_range',
        'format': format
    }

def int_mapping():
    return {
        'type': 'integer'
    }

def float_mapping():
    return {
        'type': 'float'
    }


def bool_mapping():
    return {'type': 'boolean'}

def geo_mapping():
    return {'type': 'geo_point'}
