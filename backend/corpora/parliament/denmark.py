from datetime import datetime
from glob import glob
import logging
from django.conf import settings

from corpora.parliament.parliament import Parliament
from addcorpus.python_corpora.extract import Constant, CSV
from addcorpus.python_corpora.corpus import CSVCorpusDefinition
import corpora.parliament.utils.field_defaults as field_defaults
import corpora.utils.formatting as formatting


def get_book_id(page_id):
    if page_id:
        *book_id, page = page_id.split('_')
        return '_'.join(book_id)

def format_chamber(chamber):
    chambers = {
        'folketinget': 'Folketinget',
        'landstinget': 'Landstinget',
    }

    return chambers.get(chamber, chamber)

class ParliamentDenmark(Parliament, CSVCorpusDefinition):
    title = 'People & Parliament (Denmark, 1848-2008)'
    description = "Speeches from the Folketing and Landsting"
    min_date = datetime(year=1848, month=1, day=1)
    max_date = datetime(year=2008, month=12, day=31)
    data_directory = settings.PP_DENMARK_DATA
    es_index = getattr(settings, 'PP_DENMARK_INDEX', 'parliament-denmark')
    image = 'denmark.jpg'
    description_page = 'denmark.md'

    languages = ['da']

    required_field = 'text'

    document_context = {
        'context_fields': ['book_id'],
        'sort_field': 'sequence',
        'context_display_name': 'book',
        'sort_direction': 'asc',
    }

    default_sort = {'field': 'date_latest', 'ascending': False}

    def sources(self, start, end):
        logger = logging.getLogger('indexing')

        for csv_file in glob('{}/**/*.csv'.format(self.data_directory), recursive=True):
            yield csv_file, {}



    book_label = field_defaults.book_label()
    book_label.extractor = CSV(field='title')

    book_id = field_defaults.book_id()
    book_id.extractor = CSV(
        field='id',
        transform = get_book_id
    )

    country = field_defaults.country()
    country.extractor = Constant('Denmark')

    chamber = field_defaults.chamber()
    chamber.extractor = CSV(
        field='chamber',
        transform = format_chamber,
    )

    date_earliest = field_defaults.date_earliest()
    date_earliest.extractor = CSV(
        field='year',
        transform= lambda value: formatting.get_date_from_year(value, 'earliest')
    )
    date_earliest.search_filter.lower = min_date
    date_earliest.search_filter.upper = max_date

    date_latest = field_defaults.date_latest()
    date_latest.extractor = CSV(
        field='year',
        transform= lambda value: formatting.get_date_from_year(value, 'latest')
    )
    date_latest.search_filter.lower = min_date
    date_latest.search_filter.upper = max_date

    page = field_defaults.page()
    page.extractor = CSV(field='page')

    speech = field_defaults.speech(language='da')
    speech.extractor = CSV(field='text')

    speech_id = field_defaults.speech_id()
    speech_id.extractor = CSV(field='id')

    sequence = field_defaults.sequence()
    sequence.extractor = CSV(
        field='page',
        transform = formatting.extract_integer_value,
    )

    def __init__(self):
        self.fields = [
            self.date_earliest, self.date_latest,
            self.book_label, self.book_id,
            self.country,
            self.chamber,
            self.page,
            self.speech,
            self.speech_id,
            self.sequence,
        ]
