from datetime import datetime
from glob import glob

from addcorpus.python_corpora.corpus import XMLCorpusDefinition
from addcorpus.python_corpora.extract import XML, Combined, Constant, Metadata
from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults
from corpora.utils.constants import document_context
from bs4 import BeautifulSoup
from corpora.parliament.utils.parlamint import extract_all_party_data, extract_people_data, extract_role_data, party_attribute_extractor, person_attribute_extractor, clean_value

from django.conf import settings

def format_role(values):
    id, roles = values
    if id:
        clean_id = id.replace('#', '')
        return roles.get(clean_id, clean_id)

def speech_metadata(speech_node):
    """Gets the `note` sibling to the speech."""
    return speech_node.find_previous_sibling('note')

def find_topic(speech_node):
    return speech_node.parent.find_previous_sibling('head')

def find_debate_node(speech_node):
    return speech_node.find_parent('TEI')

def find_debate_title(speech_node):
    debate_node = find_debate_node(speech_node)
    return debate_node.teiHeader.find('title')

def find_date(speech_node):
    debate_node = find_debate_node(speech_node)
    return debate_node.teiHeader.find('date')


class ParliamentFinland(Parliament, XMLCorpusDefinition):
    title = 'People and Parliament (Finland, 1907-)'
    description = 'Speeches from the eduskunta'
    min_date = datetime(year=1907, month=1, day=1)
    data_directory = settings.PP_FINLAND_DATA
    es_index = getattr(settings, 'PP_FINLAND_INDEX', 'parliament-finland')
    word_model_path = getattr(settings, 'PP_FINLAND_WM', None)

    def sources(self, start, end):
        for xml_file in glob('{}/**/*.xml'.format(self.data_directory), recursive=True):

            with open(xml_file) as infile:
                soup = BeautifulSoup(infile, features = 'xml')
            role_data = extract_role_data(soup)
            party_data = extract_all_party_data(soup)
            person_data = extract_people_data(soup)

            metadata = {
                'roles': role_data,
                'parties': party_data,
                'persons': person_data
            }

            yield xml_file, metadata

    languages = ['fi']
    description_page = 'finland.md'
    image = 'finland.jpg'

    document_context = document_context()

    tag_toplevel = 'teiCorpus'
    tag_entry = 'u'

    country = field_defaults.country()
    country.extractor = Constant('Finland')

    date = field_defaults.date()
    date.extractor = XML(
        transform_soup_func = find_date,
        attribute = 'when'
    )

    debate_id = field_defaults.debate_id()
    debate_id.extractor = XML(
        transform_soup_func = find_debate_node,
        attribute = 'xml:id'
    )

    debate_title = field_defaults.debate_title()
    debate_title.extractor = XML(
        transform_soup_func = find_debate_title,
        transform = clean_value,
    )

    party = field_defaults.party()
    party.extractor = party_attribute_extractor('name')
    party.language = 'fi'

    party_id = field_defaults.party_id()
    party_id.extractor = person_attribute_extractor('party_id')

    party_role = field_defaults.party_role()
    party_role.extractor = party_attribute_extractor('role')
    party_role.language = 'fi'

    role = field_defaults.parliamentary_role()
    role.extractor = Combined(
        XML(attribute = 'ana'),
        Metadata('roles'),
        transform = format_role,
    )

    speaker = field_defaults.speaker()
    speaker.extractor = person_attribute_extractor('name')

    speaker_id = field_defaults.speaker_id()
    speaker_id.extractor = person_attribute_extractor('id')

    speaker_gender = field_defaults.speaker_gender()
    speaker_gender.extractor = person_attribute_extractor('gender')

    speaker_birth_year = field_defaults.speaker_birth_year()
    speaker_birth_year.extractor = person_attribute_extractor('birth_year')

    speech = field_defaults.speech(language='fin')
    speech.extractor = XML(transform = clean_value)

    speech_id = field_defaults.speech_id()
    speech_id.extractor = XML(
        attribute = 'xml:id'
    )

    speech_type = field_defaults.speech_type()
    speech_type.extractor = XML(
        transform_soup_func = speech_metadata,
        attribute = 'speechType'
    )
    speech_type.language = 'fi'

    topic = field_defaults.topic()
    topic.extractor = XML(
        transform_soup_func = find_topic,
        transform = clean_value,
    )

    url = field_defaults.url()
    url.extractor = XML(
        transform_soup_func = speech_metadata,
        attribute = 'link'
    )

    sequence = field_defaults.sequence()
    sequence.extractor = XML(
        attribute = 'xml:id',
        transform = lambda value: value.split('_')[-1]
    )

    def __init__(self):
        self.fields = [
            self.country,
            self.date,
            self.debate_id, self.debate_title,
            self.party, self.party_id, self.party_role,
            self.role,
            self.speaker,
            self.speaker_id, self.speaker_gender, self.speaker_birth_year,
            self.speech,
            self.speech_id, self.speech_type,
            self.topic,
            self.url,
            self.sequence,
        ]
