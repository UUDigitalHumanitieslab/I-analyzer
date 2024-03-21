from datetime import datetime
from glob import glob

from addcorpus.python_corpora.corpus import CSVCorpusDefinition
from addcorpus.python_corpora.extract import CSV, Combined, Constant
from addcorpus.python_corpora.filters import MultipleChoiceFilter
from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults
from corpora.utils.constants import document_context
from corpora.utils import formatting

from django.conf import settings

class ParliamentFinlandOld(Parliament, CSVCorpusDefinition):
    title = 'People and Parliament (Finland, 1863-1905)'
    description = 'Speeches from the early Finnish estates'
    max_date = datetime(year=1906, month=12, day=31)
    min_date = datetime(year=1863, month=1, day=1)
    data_directory = settings.PP_FINLAND_OLD_DATA
    es_index = getattr(settings, 'PP_FINLAND_OLD_INDEX', 'parliament-finland-old')

    def sources(self, start, end):
        for csv_file in glob('{}/**/*.csv'.format(self.data_directory), recursive=True):
            yield csv_file, {}

    languages = ['sv', 'fi']
    description_page = 'finland-old.md'
    image = 'finland-old.jpg'

    document_context = document_context()

    default_sort = {'field': 'date_latest', 'ascending': False}


    chamber = field_defaults.chamber()
    chamber.extractor = CSV(field='estate')
    chamber.search_filter = MultipleChoiceFilter(
        description='Search only in debates from the selected chamber(s)',
        option_count=4
    )

    country = field_defaults.country()
    country.extractor = Constant('Finland')

    date_earliest = field_defaults.date_earliest()
    date_earliest.extractor = CSV(
        field='year_start',
        transform=lambda value: formatting.get_date_from_year(value, 'earliest')
    )
    date_earliest.search_filter.lower = min_date
    date_earliest.search_filter.upper = max_date

    date_latest = field_defaults.date_latest()
    date_latest.extractor = CSV(
        field='year_end',
        transform=lambda value: formatting.get_date_from_year(value, 'latest')
    )
    date_latest.search_filter.lower = min_date
    date_latest.search_filter.upper = max_date

    language = field_defaults.language()
    language.extractor = CSV(field='language')

    page = field_defaults.page()
    page.extractor = CSV(field='page')

    source_archive = field_defaults.source_archive()
    source_archive.extractor = CSV(field='file')

    speech = field_defaults.speech(language='fin')
    speech.extractor = CSV(field='text')

    speech_id = field_defaults.speech_id()
    speech_id.extractor = Combined(
        CSV(field='file'),
        CSV(field='page'),
        transform=lambda x: '_'.join(x)
    )

    speech_type = field_defaults.speech_type()
    speech_type.extractor = CSV(field='type')

    def __init__(self):
        self.fields = [
            self.chamber,
            self.country,
            self.date_earliest,
            self.date_latest,
            self.language,
            self.page,
            self.source_archive,
            self.speech,
            self.speech_id, self.speech_type,
        ]
