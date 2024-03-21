from glob import glob
from datetime import datetime
from django.conf import settings

from addcorpus.python_corpora.extract import Combined, Constant, CSV
from addcorpus.python_corpora.corpus import CSVCorpusDefinition
from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults
import corpora.utils.formatting as formatting
from corpora.utils.constants import document_context

def extract_ministerial_role(speaker, question_answered_by_minister_title):
    """
    Return the ministerial role if the speaker is the minister answering the question.
    """
    if question_answered_by_minister_title and speaker == 'Presidenten':
        return question_answered_by_minister_title

def extract_speaker_id(speaker_id, speaker, question_answered_by_id):
    """
    Return the speaker ID if specified. If this is a minister answering a question, get their ID.
    """
    if speaker_id:
        return speaker_id

    if speaker == 'Presidenten':
        return question_answered_by_id


def format_sequence(sequence):
    if sequence:
        return sequence.strip()

def format_language(language):
    languages = {
        'nno': 'Norwegian (Nynorsk)',
        'nob': 'Norwegian (Bokmål)'
    }

    return languages.get(language, None)

EMPTY_VALUES = ['', 'NA']

class ParliamentNorwayNew(Parliament, CSVCorpusDefinition):
    '''
    Class for indexing Norwegian parliamentary data
    '''

    title = "People & Parliament (Norway, 1998-2016)"
    description = "Speeches from the Storting"
    min_date = datetime(year=1998, month=1, day=1)
    max_date = datetime(year=2016, month=12, day=31)
    data_directory = settings.PP_NORWAY_NEW_DATA
    es_index = getattr(settings, 'PP_NORWAY_NEW_INDEX', 'parliament-norway-new')
    word_model_path = getattr(settings, 'PP_NORWAY_WM', None)
    image = 'norway.JPG'
    languages = ['no']
    description_page = 'norway-new.md'
    document_context = document_context()

    def sources(self, start, end):
        for csv_file in glob('{}/**/*.csv'.format(self.data_directory), recursive=True):
            yield csv_file, {}

    country = field_defaults.country()
    country.extractor = Constant('Norway')
    country.searchable = False

    chamber = field_defaults.chamber()
    chamber.extractor = Constant('Stortinget')
    chamber.visualizations = None
    chamber.search_filter = None
    chamber.searchable = False

    date = field_defaults.date()
    date.extractor = CSV(field='date')
    date.search_filter.lower = min_date
    date.search_filter.upper = max_date

    debate_title = field_defaults.debate_title()
    debate_title.extractor = CSV(
        field = 'debate_title',
        convert_to_none = EMPTY_VALUES
    )

    debate_id = field_defaults.debate_id()
    debate_id.extractor = CSV(field = 'debate_reference')

    debate_type = field_defaults.debate_type()
    debate_type.extractor = CSV(
        field = 'debate_type',
        convert_to_none = EMPTY_VALUES
    )

    legislature = field_defaults.legislature()
    legislature.extractor = CSV(
        field = 'cabinet_short',
        convert_to_none = EMPTY_VALUES,
    )

    party = field_defaults.party()
    party.extractor = CSV(
        field = 'party_name',
        convert_to_none = EMPTY_VALUES,
    )

    party_id = field_defaults.party_id()
    party_id.extractor = CSV(
        field='party_id',
        convert_to_none = EMPTY_VALUES,
    )

    party_role = field_defaults.party_role()
    party_role.extractor = CSV(
        field = 'party_role',
        convert_to_none = EMPTY_VALUES,
    )

    role = field_defaults.parliamentary_role()
    role.extractor = CSV(
        field='speaker_role',
        convert_to_none = EMPTY_VALUES,
    )

    ministerial_role = field_defaults.ministerial_role()
    ministerial_role.extractor = Combined(
        CSV(field='rep_name', convert_to_none=EMPTY_VALUES),
        CSV(field='question_answered_by_minister_title', convert_to_none=EMPTY_VALUES),
        transform = lambda values: extract_ministerial_role(*values)
    )

    speaker = field_defaults.speaker()
    speaker.extractor = CSV(
        field='rep_name',
        convert_to_none = EMPTY_VALUES,
    )

    speaker_id = field_defaults.speaker_id()
    speaker_id.extractor = Combined(
        CSV(field='rep_id', convert_to_none = EMPTY_VALUES),
        CSV(field='rep_name', convert_to_none = EMPTY_VALUES),
        CSV(field='question_answered_by_id', convert_to_none = EMPTY_VALUES),
        transform = lambda values: extract_speaker_id(*values)
    )

    speaker_constituency = field_defaults.speaker_constituency()
    speaker_constituency.extractor = CSV(
        field='county',
        convert_to_none = EMPTY_VALUES
    )

    speaker_gender = field_defaults.speaker_gender()
    speaker_gender.extractor = CSV(
        field='rep_gender',
        convert_to_none = EMPTY_VALUES
    )

    speaker_birth_year = field_defaults.speaker_birth_year()
    speaker_birth_year.extractor = CSV(
        field = 'rep_birth',
        transform = lambda date: formatting.extract_year(date, pattern = r'\d{2}\.\d{2}\.(\d{4})')
    )

    speaker_death_year = field_defaults.speaker_death_year()
    speaker_death_year.extractor = CSV(
        field = 'rep_death',
        transform = lambda date: formatting.extract_year(date, pattern = r'\d{2}\.\d{2}\.(\d{4})')
    )

    speech = field_defaults.speech(language='no')
    speech.extractor = CSV(field='text')

    speech_id = field_defaults.speech_id()
    speech_id.extractor = CSV(field='id')

    subject = field_defaults.subject()
    subject.extractor = CSV(
        field = 'keyword',
        convert_to_none = EMPTY_VALUES
    )

    topic = field_defaults.topic()
    topic.extractor = CSV(
        field='debate_subject',
        convert_to_none = EMPTY_VALUES
    )

    sequence = field_defaults.sequence()
    sequence.extractor = CSV(
        field = 'order',
        transform = format_sequence,
        convert_to_none = EMPTY_VALUES,
    )

    language = field_defaults.language()
    language.extractor = CSV(
        field = 'language',
        transform = format_language
    )

    def __init__(self):
        self.fields = [
            self.chamber,
            self.country,
            self.date,
            self.debate_title, self.debate_id, self.debate_type,
            self.language,
            self.legislature,
            self.party,
            self.party_id,self.party_role,
            self.role, self.ministerial_role,
            self.speaker,
            self.speaker_id, self.speaker_birth_year, self.speaker_death_year, self.speaker_constituency, self.speaker_gender,
            self.speech,
            self.speech_id,
            self.subject,
            self.topic,
            self.sequence,
        ]
