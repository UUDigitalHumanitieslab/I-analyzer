from datetime import datetime


from django.conf import settings

from corpora.parliament.parliament import Parliament
from addcorpus.python_corpora.extract import Constant, CSV
from addcorpus.python_corpora.corpus import CSVCorpusDefinition
import corpora.parliament.utils.field_defaults as field_defaults


def standardize_bool(date_is_estimate):
    return date_is_estimate.lower()

class ParliamentGermanyOld(Parliament, CSVCorpusDefinition):
    title = 'People & Parliament (Germany Reichstag - 1867-1942)'
    description = "Speeches from the Reichstag"
    min_date = datetime(year=1867, month=1, day=1)
    max_date = datetime(year=1942, month=12, day=31)
    data_directory = settings.PP_GERMANY_OLD_DATA
    es_index = getattr(settings, 'PP_GERMANY_OLD_INDEX', 'parliament-germany-old')
    image = 'germany-old.jpeg'
    languages = ['de']
    word_model_path = getattr(settings, 'PP_DE_WM', None)

    description_page = 'germany-old.md'

    field_entry = 'item_order'
    required_field = 'text'

    country = field_defaults.country()
    country.extractor = Constant(
        value='Germany'
    )

    book_id = field_defaults.book_id()
    book_id.extractor = CSV(
        field='book_id'
    )

    book_label = field_defaults.book_label()
    book_label.extractor = CSV(
        field='book_label'
    )

    era = field_defaults.era(include_aggregations= False)
    era.extractor = CSV(
        field='parliament'
    )

    date = field_defaults.date()
    date.extractor = CSV(
        field='date'
    )
    date.search_filter.lower = min_date
    date.search_filter.upper = max_date

    date_is_estimate = field_defaults.date_is_estimate()
    date_is_estimate.extractor = CSV(
        field='date_is_estimate',
        transform=standardize_bool
    )

    page = field_defaults.page()
    page.extractor = CSV(
        field='page_number'
    )

    speech = field_defaults.speech(language='de')
    speech.extractor = CSV(
        field='text',
        multiple=True,
        transform=lambda x : ' '.join(x)
    )

    url = field_defaults.url()
    url.extractor = CSV(
        field='img_url'
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = CSV(
        field='item_order'
    )

    def __init__(self):
        self.fields = [
            self.country,
            self.book_id, self.book_label,
            self.era,
            self.date, self.date_is_estimate,
            self.page,
            self.speech, self.speech_id,
            self.url,
        ]
