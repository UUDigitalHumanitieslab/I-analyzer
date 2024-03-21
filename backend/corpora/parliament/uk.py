from glob import glob
import logging
from datetime import datetime

from django.conf import settings

from addcorpus.python_corpora.extract import Constant, CSV
from addcorpus.python_corpora.corpus import CSVCorpusDefinition
from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults
from corpora.utils.constants import document_context

def format_debate_title(title):
    if title.endswith('.'):
        title = title[:-1]

    return title.title()

def format_house(house):
    if 'commons_wmhall' in house.lower():
        return 'House of Commons - Westminster Hall'
    elif 'commons' in house.lower():
        return 'House of Commons'
    elif 'lords' in house.lower():
        return 'House of Lords'

def format_speaker(speaker):
    if speaker:
        if speaker.startswith('*'):
            speaker = speaker[1:]

        return speaker.title()

class ParliamentUK(Parliament, CSVCorpusDefinition):
    title = 'People & Parliament (UK)'
    description = "Speeches from the House of Lords and House of Commons"
    data_directory = settings.PP_UK_DATA
    min_date = datetime(year=1803, month=1, day=1)
    max_date = datetime(year=2021, month=12, day=31)
    es_index = getattr(settings, 'PP_UK_INDEX', 'parliament-uk')
    image = 'uk.jpeg'
    word_model_path = getattr(settings, 'PP_UK_WM', None)
    languages = ['en']
    description_page = 'uk.md'
    field_entry = 'speech_id'
    document_context = document_context()

    def sources(self, start, end):
        logger = logging.getLogger('indexing')
        for csv_file in glob('{}/*.csv'.format(self.data_directory)):
            yield csv_file, {}

    chamber =  field_defaults.chamber()
    chamber.extractor = CSV(
        field='house',
        transform=format_house
    )
    chamber.search_filter.option_count = 3

    country = field_defaults.country()
    country.extractor = Constant(
        value='United Kingdom'
    )

    date = field_defaults.date()
    date.extractor = CSV(
        field='date',
    )

    debate_title = field_defaults.debate_title()
    debate_title.extractor = CSV(
        field='debate',
        transform=format_debate_title
    )
    debate_title.language = 'en'

    debate_id = field_defaults.debate_id()
    debate_id.extractor = CSV(
        field='debate_id'
    )

    speech = field_defaults.speech(language='en')
    speech.extractor = CSV(
        field='content',
        multiple=True,
        transform=lambda x : ' '.join(x)
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = CSV(
        field='speech_id'
    )

    speech_type = field_defaults.speech_type()
    speech_type.extractor = CSV(
        field='speech_type'
    )

    speaker = field_defaults.speaker()
    speaker.extractor = CSV(
        field='speaker_name',
        transform=format_speaker
    )

    speaker_id = field_defaults.speaker_id()
    speaker_id.extractor = CSV(
        field='speaker_id',
    )

    topic = field_defaults.topic()
    topic.extractor = CSV(
        field='heading_major',
    )
    topic.language = 'en'

    subtopic = field_defaults.subtopic()
    subtopic.extractor = CSV(
        field='heading_minor',
    )
    subtopic.language = 'en'

    sequence = field_defaults.sequence()
    sequence.extractor = CSV(
        field='sequence',
    )

    def __init__(self):
        self.fields = [
            self.country, self.date,
            self.debate_title, self.debate_id,
            self.topic, self.subtopic,
            self.chamber,
            self.speech, self.speech_id, self.speech_type,
            self.sequence,
            self.speaker, self.speaker_id,
        ]
