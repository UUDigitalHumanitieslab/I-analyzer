from glob import glob
import logging
from datetime import datetime

from django.conf import settings

from corpora.parliament.parliament import Parliament
from addcorpus.python_corpora.extract import Constant, Combined, CSV
from addcorpus.python_corpora.corpus import CSVCorpusDefinition
import corpora.utils.formatting as formatting
import corpora.parliament.utils.field_defaults as field_defaults


class ParliamentGermanyNew(Parliament, CSVCorpusDefinition):
    title = 'People & Parliament (Germany 1949-2021)'
    description = "Speeches from the Bundestag"
    min_date = datetime(year=1949, month=1, day=1)
    max_date = datetime(year=2021, month=12, day=31)
    data_directory = settings.PP_GERMANY_NEW_DATA
    es_index = getattr(settings, 'PP_GERMANY_NEW_INDEX', 'parliament-germany-new')
    image = 'germany-new.jpeg'
    languages = ['de']
    word_model_path = getattr(settings, 'PP_DE_WM', None)

    field_entry = 'id'
    required_field = 'speech_content'

    description_page = 'germany-new.md'

    def sources(self, start, end):
        logger = logging.getLogger('indexing')
        for csv_file in glob('{}/*.csv'.format(self.data_directory)):
            yield csv_file, {}

    country = field_defaults.country()
    country.extractor = Constant(
        value='Germany'
    )

    date = field_defaults.date()
    date.extractor = CSV(
        field='date'
    )
    date.search_filter.lower = min_date

    chamber = field_defaults.chamber()
    chamber.extractor = Constant(
        value='Bundestag'
    )
    chamber.search_filter = None
    chamber.visualizations = []
    chamber.language = 'de'

    debate_id = field_defaults.debate_id()
    debate_id.extractor = CSV(
        field='session'
    )

    # in Germany, abbreviations are the most common way to refer to parties
    party = field_defaults.party()
    party.extractor = CSV(
        field='party_abbreviation'
    )
    party.language = 'de'

    party_full = field_defaults.party_full()
    party_full.extractor = CSV(
        field='party_full_name'
    )
    party_full.language = 'de'

    party_id = field_defaults.party_id()
    party_id.extractor = CSV(
        field='party_id'
    )

    role = field_defaults.parliamentary_role()
    role.extractor = CSV(
        field='position_short'
    )
    role.language = 'en'

    role_long = field_defaults.role_long()
    role_long.extractor = CSV(
        field='position-long'
    )

    speaker = field_defaults.speaker()
    speaker.extractor = Combined(
        CSV(field='speaker_first_name', convert_to_none=False),
        CSV(field='speaker_last_name', convert_to_none=False),
        transform=lambda x: ' '.join(x)
    )

    speaker_id = field_defaults.speaker_id()
    speaker_id.extractor = CSV(
        field='speaker_id'
    )

    speaker_aristocracy = field_defaults.speaker_aristocracy()
    speaker_aristocracy.extractor = CSV(
        field='speaker_aristocracy'
    )

    speaker_academic_title = field_defaults.speaker_academic_title()
    speaker_academic_title.extractor = CSV(
        field='speaker_academic_title'
    )

    speaker_birth_country = field_defaults.speaker_birth_country()
    speaker_birth_country.extractor = CSV(
        field='speaker_birth_country'
    )
    speaker_birth_country.language = 'de'

    speaker_birthplace = field_defaults.speaker_birthplace()
    speaker_birthplace.extractor = CSV(
        field='speaker_birth_place'
    )
    speaker_birthplace.language = 'de'

    speaker_birth_year = field_defaults.speaker_birth_year()
    speaker_birth_year.extractor = CSV(
        field='speaker_birth_date',
        transform=formatting.extract_year
    )

    speaker_death_year = field_defaults.speaker_death_year()
    speaker_death_year.extractor = CSV(
        field='speaker_death_date',
        transform=formatting.extract_year
    )

    speaker_gender = field_defaults.speaker_gender()
    speaker_gender.extractor = CSV(
        field='speaker_gender'
    )
    speaker_gender.language = 'en'

    speaker_profession = field_defaults.speaker_profession()
    speaker_profession.extractor = CSV(
        field='speaker_profession'
    )
    speaker_profession.language = 'de'

    speech = field_defaults.speech(language='de')
    speech.extractor = CSV(
        field='speech_content',
        multiple=True,
        transform=lambda x : ' '.join(x)
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = CSV(
        field='id'
    )

    url = field_defaults.url()
    url.extractor = CSV(
        field='document_url'
    )

    # order of speeches: value is identical to speech_id
    # but saved as integer for sorting
    sequence = field_defaults.sequence()
    sequence.extractor = CSV(
        field = 'id'
    )

    def __init__(self):
        self.fields = [
            self.country, self.date,
            self.chamber,
            self.debate_id,
            self.speaker, self.speaker_id,
            self.speaker_aristocracy, self.speaker_academic_title,
            self.speaker_birth_country, self.speaker_birthplace,
            self.speaker_birth_year, self.speaker_death_year,
            self.speaker_gender, self.speaker_profession,
            self.role, self.role_long,
            self.party, self.party_full, self.party_id,
            self.speech, self.speech_id,
            self.url,
            self.sequence,
        ]



