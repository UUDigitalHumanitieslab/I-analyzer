from glob import glob
from datetime import datetime
import re
from django.conf import settings
import os

from addcorpus.python_corpora.extract import Combined, Constant, CSV
from addcorpus.python_corpora.corpus import CSVCorpusDefinition
from corpora.utils.constants import document_context
from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults
import corpora.utils.formatting as formatting

def remove_file_extension(filename):
    name, ext = os.path.splitext(filename)
    return name

class ParliamentNorway(Parliament, CSVCorpusDefinition):
    '''
    Class for indexing Norwegian parliamentary data
    '''

    title = "People & Parliament (Norway, 1814-2004)"
    description = "Speeches from the Storting"
    min_date = datetime(year=1814, month=1, day=1)
    max_date = datetime(year=2004, month=12, day=31)
    data_directory = settings.PP_NORWAY_DATA
    es_index = getattr(settings, 'PP_NORWAY_INDEX','parliament-norway')
    image = 'norway.JPG'
    languages = ['no']
    description_page = 'norway.md'
    document_context = document_context(
        context_fields=['book_id'],
        context_display_name='book',
    )
    default_sort = {
        'field': 'date_latest',
        'ascending': False,
    }

    def sources(self, start, end):
        for csv_file in glob('{}/**/*.csv'.format(self.data_directory), recursive=True):
            _, filename = os.path.split(csv_file)
            year = re.search(r'\d{4}', filename)
            if year:
                date = datetime(year=int(year.group(0)), month=1, day=1)
                if start <= date <= end:
                    yield csv_file, {}

    book_id = field_defaults.book_id()
    book_id.extractor = CSV(
        field = 'source_file',
        transform = remove_file_extension,
    )

    book_label = field_defaults.book_label()
    book_label.extractor = Combined(
        CSV(field = 'title'),
        CSV(field = 'subtitle'),
        transform = lambda parts: '; '.join(parts)
    )


    chamber = field_defaults.chamber()
    chamber.extractor = Constant('Stortinget')
    chamber.visualizations = None
    chamber.search_filter = None
    chamber.searchable = False

    country = field_defaults.country()
    country.extractor = Constant('Norway')
    country.searchable = False

    date_earliest = field_defaults.date_earliest()
    date_earliest.extractor = CSV(
        field = 'year',
        transform = lambda value : formatting.get_date_from_year(value, 'earliest')
    )
    date_earliest.search_filter.lower = min_date
    date_earliest.search_filter.upper = max_date

    date_latest = field_defaults.date_latest()
    date_latest.extractor = CSV(
        field = 'year',
        transform = lambda value : formatting.get_date_from_year(value, 'latest')
    )
    date_latest.search_filter.lower = min_date
    date_latest.search_filter.upper = max_date


    page = field_defaults.page()
    page.extractor = CSV(field = 'page')

    speech = field_defaults.speech(language='no')
    speech.extractor = CSV(field = 'text')
    speech.language = 'no'

    sequence = field_defaults.sequence()
    sequence.extractor = CSV(field = 'page')

    def __init__(self):
        self.fields = [
            self.date_earliest, self.date_latest,
            self.book_id, self.book_label,
            self.chamber,
            self.country,
            self.page,
            self.speech,
            self.sequence,
        ]
