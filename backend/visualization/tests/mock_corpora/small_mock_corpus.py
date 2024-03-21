from datetime import datetime
import os

from addcorpus.python_corpora.corpus import FieldDefinition, CSVCorpusDefinition
from addcorpus.python_corpora.extract import CSV
from addcorpus.es_mappings import date_mapping, keyword_mapping, main_content_mapping, text_mapping
from addcorpus.es_settings import es_settings


# Fake corpus class for unit tests

here = os.path.abspath(os.path.dirname(__file__))

class SmallMockCorpus(CSVCorpusDefinition):
    title = 'Mock Corpus'
    description = 'Corpus for testing'
    visualize = []
    min_date = datetime(year=1800, month=1, day=1)
    max_date = datetime(year=1899, month=12, day=31)
    es_index = 'ianalyzer-mock-corpus'
    image = 'test.jpeg'
    data_directory = 'bogus'
    languages = ['en']
    category = 'book'

    es_settings = es_settings(['en'], stopword_analysis=True)

    def sources(self, start=min_date, end=max_date):
        for csv_file in os.listdir(os.path.join(here, 'source_files')):
            yield os.path.join(here, 'source_files', csv_file), {}

    date = FieldDefinition(
        name = 'date',
        es_mapping = date_mapping(),
        extractor = CSV('date')
    )

    title_field = FieldDefinition(
        name = 'title',
        es_mapping = text_mapping(),
        extractor = CSV('title')
    )

    content = FieldDefinition(
        name = 'content',
        display_type='text_content',
        es_mapping = main_content_mapping(True, True, False, 'en'),
        extractor = CSV('content'),
        language='en',
    )

    genre = FieldDefinition(
        name = 'genre',
        es_mapping = keyword_mapping(),
        extractor = CSV('genre')
    )

    fields = [date, title_field, content, genre]

SPECS = {
    'min_date': SmallMockCorpus.min_date,
    'max_date': SmallMockCorpus.max_date,
    'total_docs': 3,
    'total_words': 67,
    'has_token_counts': True,
    'fields':  ['date', 'title', 'genre', 'content'],
    'example_query': 'to',
    'content_field': 'content',
}
