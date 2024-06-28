from datetime import datetime
import json
import logging

from django.conf import settings
import langcodes
import requests

from addcorpus.python_corpora.corpus import JSONCorpusDefinition, FieldDefinition
from addcorpus.es_mappings import int_mapping, keyword_mapping
import addcorpus.python_corpora.extract as extract
from corpora.peaceportal.peaceportal import PeacePortal
from corpora.utils.exclude_fields import exclude_fields_without_extractor


def transform_language(language_array):
    ''' transform the language to an iso code,
    skip any languages which are not recognized by langcodes module
    TODO: we may also express the script as part of the code'''
    if not language_array:
        return None
    output = []
    for lang in language_array:
        try:
            output.append(langcodes.find(lang).to_tag())
        except:
            continue
    return output


def transform_centuries(century_array):
    ''' transform each item of the century array to integer
    abort if values such as "unknown" appear in the array '''
    if not century_array:
        return None
    output = []
    for item in century_array:
        try:
            output.append(int(item))
        except:
            return None
    return output

class JewishMigration(PeacePortal, JSONCorpusDefinition):
    ''' Class for indexing Jewish Migration data '''
    title = "Modelling Jewish Migration"
    description = "Inscriptions and book entries documenting Jewish settlements in the Mediterranean"
    min_date = datetime(year=1, month=1, day=1)
    max_date = datetime(year=1800, month=12, day=31)

    data_directory = getattr(settings, 'JMIG_DATA', None)
    data_url = getattr(settings, 'JMIG_DATA_URL', None)

    es_index = getattr(settings, 'JMIG_INDEX', 'jewishmigration')
    image = 'jewish_inscriptions.jpg'
    languages = ['en']

    category = 'inscription'

    def sources(self, start, end):
        if self.data_url:
            response = requests.get(self.data_url)
            list_of_sources = response.json()
        elif self.data_directory:
            with open(self.data_directory, 'r') as f:
                list_of_sources = json.load(f)
        else:
            logging.getLogger('indexing').warning(
                'No data directory or URL provided.')
        for source in list_of_sources:
            yield source


    def __init__(self):
        super().__init__()
        self._id.extractor = extract.JSON(key='source')
        self.source_database.extractor = extract.JSON(key='source')
        self.language.extractor = extract.JSON(
            key='languages')
        self.language_code.extractor = extract.JSON(
            key='languages', transform=transform_language)
        self.country.extractor = extract.JSON(key='area')
        self.region.extractor = extract.JSON(key='region')
        self.settlement.extractor = extract.JSON(key='place_name')
        self.coordinates.extractor = extract.JSON(key='coordinates')
        self.coordinates.visualizations = ['map']
        self.sex.extractor = extract.JSON(key='sex_deceased')
        self.iconography.extractor = extract.JSON(key='symbol')
        self.comments.extractor = extract.JSON(key='comments')
        self.transcription.extractor = extract.JSON(key='inscription')
        self.transcription_english.extractor = extract.JSON(
            key='transcription')
        extra_fields = [
            FieldDefinition(
                name='script',
                display_name='Script',
                description='Which alphabet the source was written in',
                es_mapping=keyword_mapping(),
                extractor=extract.JSON(key='scripts'),
            ),
            FieldDefinition(
                name='site_type',
                display_name='Site Type',
                description='Type of site where evidence for settlement was found',
                es_mapping=keyword_mapping(),
                extractor=extract.JSON(key='site_type')
            ),
            FieldDefinition(
                name='inscription_type',
                display_name='Inscription type',
                description='Type of inscription',
                es_mapping=keyword_mapping(),
                extractor=extract.JSON(key='inscription_type')
            ),
            FieldDefinition(
                name='period',
                display_name='Period',
                description='Period in which the inscription was made',
                es_mapping=keyword_mapping(),
                extractor=extract.JSON(key='period')
            ),
            FieldDefinition(
                name='estimated_centuries',
                display_name='Estimated Centuries',
                description='Estimate of centuries in which the inscription was made',
                es_mapping=int_mapping(),
                extractor=extract.JSON(
                    key='estimated_centuries', transform=transform_centuries)
            ),
            FieldDefinition(
                name='inscription_count',
                display_name='Inscription count',
                description='Number of inscriptions',
                es_mapping=int_mapping(),
                extractor=extract.JSON(key='inscriptions_count')
            ),
            FieldDefinition(
                name='religious_profession',
                display_name='Religious profession',
                description='Religious profession of deceased',
                es_mapping=keyword_mapping(),
                extractor=extract.JSON(key='religious_profession')
            ),
            FieldDefinition(
                name='sex_dedicator',
                display_name='Gender dedicator',
                description='Gender of the dedicator',
                es_mapping=keyword_mapping(),
                extractor=extract.JSON(key='sex_dedicator')
            )
        ]
        self.fields = [*exclude_fields_without_extractor(self.fields), *extra_fields]
