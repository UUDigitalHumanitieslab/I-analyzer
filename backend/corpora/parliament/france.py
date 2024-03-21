from glob import glob
import logging
from datetime import datetime

from django.conf import settings

from corpora.parliament.parliament import Parliament
from addcorpus.python_corpora.extract import Constant, Combined, CSV
from addcorpus.python_corpora.corpus import CSVCorpusDefinition
import corpora.parliament.utils.field_defaults as field_defaults
from corpora.utils.formatting import underscore_to_space
from corpora.utils.constants import document_context

class ParliamentFrance(Parliament, CSVCorpusDefinition):
    title = "People & Parliament (France 1881-2022)"
    description = "Speeches from the 3rd, 4th and 5th republic of France"
    min_date = datetime(year=1881, month=1, day=1)
    data_directory = settings.PP_FR_DATA
    es_index = getattr(settings, 'PP_FR_INDEX', 'parliament-france')
    image = 'france.jpeg'
    languages = ['fr']
    description_page = 'france.md'
    word_model_path = getattr(settings, 'PP_FR_WM', None)

    field_entry = 'speech_id'

    document_context = document_context()

    def sources(self, start, end):
        logger = logging.getLogger('indexing')

        for csv_file in glob('{}/**/*.csv'.format(self.data_directory), recursive=True):
            yield csv_file, {}

    book_id = field_defaults.book_id()
    book_id.extractor = Combined(
        CSV(field='book_id'),
        CSV(field='book_part_id'),
        CSV(field='page_id'),
        transform=lambda x: ' '.join(filter(None, x))
    )

    chamber = field_defaults.chamber()
    chamber.extractor = CSV(
        field='chamber',
        transform=underscore_to_space
    )
    chamber.language = 'fr'

    country = field_defaults.country()
    country.extractor = Constant(
        value='France'
    )

    date = field_defaults.date()
    date.extractor = CSV(
        field='date'
    )

    date_is_estimate = field_defaults.date_is_estimate()
    date_is_estimate.extractor = CSV(
        field='date_is_estimate',
        transform=lambda x: x=='True'
    )

    debate_id = field_defaults.debate_id()
    debate_id.extractor = Combined(
        CSV(field='date'),
        CSV(field='seance_order'),
        transform=lambda x: '_'.join(filter(None, x))
    )

    # debate title is not included in field list below
    # the values of 'seance' field seem very limited (Première séance, Deuxième séance, etc.,)
    # so we don't want this to be treated as a text field
    debate_title = field_defaults.debate_title()
    debate_title.extractor = CSV(
        field='seance'
    )

    debate_type = field_defaults.debate_type()
    debate_type.extractor = CSV(
        field='session_type',
        transform=lambda x: x.title() if x else None,
    )

    era = field_defaults.era(include_aggregations=False)
    era.extractor = CSV(
        field='era',
        transform=underscore_to_space
    )

    legislature = field_defaults.legislature()
    legislature.extractor = CSV(
        field='legislature'
    )

    page = field_defaults.page()
    page.extractor = CSV(
        field='page_order'
    )

    page_source = field_defaults.page_source()
    page_source.extractor = CSV(
        field='page_source'
    )

    sequence = field_defaults.sequence()
    sequence.extractor = CSV(
        field='sequence'
    )

    speech = field_defaults.speech(language='fr')
    speech.extractor = CSV(
        field='page_text'
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = CSV(
        field='speech_id'
    )

    url_pdf = field_defaults.url()
    url_pdf.extractor = CSV(
        field='pdf_url'
    )
    url_pdf.display_name = 'Source url (PDF)'
    url_pdf.description = 'URL to PDF source file of this speech'

    url_html = field_defaults.url()
    url_html.extractor = CSV(
        field='html_url'
    )
    url_html.name = 'url_html'
    url_html.display_name = 'Source url (HTML)'
    url_html.description = 'URL to HTML source file of this speech'

    def __init__(self):
        self.fields = [
            self.date,
            self.book_id,
            self.chamber,
            self.country,
            self.date_is_estimate,
            self.debate_id, self.debate_type,
            self.era,
            self.legislature,
            self.page, self.page_source,
            self.sequence,
            self.speech, self.speech_id,
            self.url_pdf, self.url_html
        ]









