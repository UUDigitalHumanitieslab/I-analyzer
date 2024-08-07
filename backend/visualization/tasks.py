from celery import chord, group, shared_task
from django.conf import settings
from visualization import wordcloud, ngram, term_frequency
from es import download as es_download
from api.api_query import api_query_to_es_query

@shared_task()
def get_wordcloud_data(request_json):
    corpus_name = request_json['corpus']
    es_query = api_query_to_es_query(request_json, corpus_name)
    list_of_texts, _ = es_download.scroll(corpus_name, es_query, settings.WORDCLOUD_LIMIT)
    word_counts = wordcloud.make_wordcloud_data(list_of_texts, request_json['field'], request_json['corpus'])
    return word_counts


@shared_task()
def get_geo_data(request_json):
    ''' Fetch all documents regardless of number of search results.
    This should be fast enough for this operation.
    '''
    corpus_name = request_json['corpus']
    geo_field = request_json['field']
    es_query = api_query_to_es_query(request_json, corpus_name)
    list_of_documents, _ = es_download.scroll(
        corpus_name, es_query, source_includes=['id', geo_field])

    # Convert documents to GeoJSON features
    geojson_features = []
    for doc in list_of_documents:
        if doc['_source'][geo_field] is not None:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": doc['_source'][geo_field]['coordinates']
                },
                "properties": {
                    "id": doc['_source']['id']
                }
            }
            geojson_features.append(feature)

    return geojson_features


@shared_task
def get_ngram_data_bin(**kwargs):
    return ngram.tokens_by_time_interval(**kwargs)

@shared_task
def integrate_ngram_results(results, **kwargs):
    return ngram.get_ngrams(results, **kwargs)

def ngram_data_tasks(request_json):
    corpus_name = request_json['corpus_name']
    es_query = api_query_to_es_query(request_json, corpus_name)
    freq_compensation = request_json['freq_compensation']
    bins = ngram.get_time_bins(es_query, corpus_name)

    return chord(group([
        get_ngram_data_bin.s(
            corpus_name=corpus_name,
            es_query=es_query,
            field=request_json['field'],
            bin=b,
            ngram_size=request_json['ngram_size'],
            term_position=request_json['term_position'],
            freq_compensation=freq_compensation,
            subfield=request_json['subfield'],
            max_size_per_interval=request_json['max_size_per_interval'],
            date_field=request_json['date_field']
        )
        for b in bins
    ]), integrate_ngram_results.s(
            number_of_ngrams=request_json['number_of_ngrams']
        )
    )

@shared_task()
def get_histogram_term_frequency_bin(es_query, corpus_name, field_name, field_value, size, include_query_in_result = False):
    '''
    Calculate the value for a single series + bin in the histogram term frequency
    graph.
    '''
    return term_frequency.get_aggregate_term_frequency(
        es_query, corpus_name, field_name, field_value, size,
        include_query_in_result = include_query_in_result
    )

def histogram_term_frequency_tasks(request_json, include_query_in_result = False):
    '''
    Calculate values for an entire series in the histogram term frequency graph.
    Schedules one task for each bin, which can be run in parallel.
    '''
    corpus_name = request_json['corpus_name']
    es_query = api_query_to_es_query(request_json, corpus_name)
    bins = request_json['bins']

    return group([
        get_histogram_term_frequency_bin.s(
            es_query,
            corpus_name,
            request_json['field_name'],
            bin['field_value'],
            bin['size'],
            include_query_in_result = include_query_in_result
        )
        for bin in bins
    ])

@shared_task()
def get_timeline_term_frequency_bin(es_query, corpus_name, field_name, start_date, end_date, size, include_query_in_result = False):
    '''
    Calculate the value for a single series + bin in the timeline term frequency
    graph.
    '''
    return term_frequency.get_date_term_frequency(
        es_query, corpus_name, field_name, start_date, end_date, size,
        include_query_in_result = include_query_in_result
    )

def timeline_term_frequency_tasks(request_json, include_query_in_result = False):
    '''
    Calculate values for an entire series in the timeline term frequency graph.
    Schedules one task for each bin, which can be run in parallel.
    '''

    corpus_name = request_json['corpus_name']
    es_query = api_query_to_es_query(request_json, corpus_name)
    bins = request_json['bins']

    return group(
        get_timeline_term_frequency_bin.s(
            es_query,
            corpus_name,
            request_json['field_name'],
            bin['start_date'],
            bin['end_date'],
            bin['size'],
            include_query_in_result = include_query_in_result
        )
        for bin in bins
    )
