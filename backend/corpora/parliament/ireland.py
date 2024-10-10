from datetime import datetime
from django.conf import settings
import os
from glob import glob
import re
from bs4 import BeautifulSoup
import json
import csv
from ianalyzer_readers.xml_tag import Tag, PreviousSiblingTag

from addcorpus.python_corpora.corpus import CorpusDefinition, CSVCorpusDefinition, XMLCorpusDefinition
from addcorpus.python_corpora.extract import Constant, CSV, XML, Metadata, Combined, Backup
from addcorpus.es_mappings import main_content_mapping
from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults
import corpora.utils.formatting as formatting
import corpora.parliament.utils.parlamint as parlamint


def in_date_range(corpus, start, end):
    start_date = start or corpus.min_date
    end_date = end or corpus.max_date

    return start_date <= corpus.max_date and end_date >= corpus.min_date

def format_mininster_role(position, department):
    '''Format 1919-2013 minister positions analogous to the 2014-2020 positions'''

    if position == 'Taoiseach':
        return position
    elif position == 'Minister':
        return f'{position} for {department}'
    else:
        return f'{position} at the department of {department}'

def extract_minister_data(data_directory):
    for filename in glob('{}/**/*ministers.tab'.format(data_directory)):
        with(open(filename)) as tsv_file:
            reader = csv.DictReader(tsv_file, delimiter='\t')
            for row in reader:
                speaker_id = row['memberID']
                start_date = row['start_date']
                end_date = row['end_date'] if row['end_date'] != 'NULL' else '2011-12-01' # data goes up to 2011
                position = row['position']
                department = row['department']

                yield {
                    'speaker_id': speaker_id,
                    'start_date': datetime.strptime(start_date, '%Y-%m-%d'),
                    'end_date': datetime.strptime(end_date, '%Y-%m-%d'),
                    'role': format_mininster_role(position, department)
                }


def between_dates(date, start_date, end_date):
    return date >= start_date and date <= end_date

def find_ministerial_role(data):
    speaker_id, datestring, minister_data = data
    date = datetime.strptime(datestring, '%Y-%m-%d')

    def identity_matches(minister):
        return minister['speaker_id'] == speaker_id and between_dates(date, minister['start_date'], minister['end_date'])

    positions = list(filter(identity_matches, minister_data))

    if len(positions):
        return ', '.join(position['role'] for position in positions)

class ParliamentIrelandOld(CSVCorpusDefinition):
    '''
    Class for extracting 1919-2013 Irish debates.

    Only used for data extraction, use the `ParliamentIreland` class in the application.
    '''

    data_directory = settings.PP_IRELAND_DATA
    min_date = datetime(year=1919, month=1, day=1)
    max_date = datetime(year=2013, month=12, day=31)

    field_entry = 'speechID'
    delimiter = '\t'

    def sources(self, start, end):
        if in_date_range(self, start, end):
            min_year = start.year if start else self.min_date.year
            max_year = end.year if end else self.max_date.year
            for tsv_file in glob('{}/**/Dail_debates_1919-2013_*.tab'.format(self.data_directory), recursive=True):
                year = int(re.search(r'(\d{4}).tab$', tsv_file).group(1))
                if year >= min_year and year <= max_year:
                    minister_data = list(extract_minister_data(self.data_directory))
                    metadata = {
                        'ministers': minister_data
                    }
                    yield tsv_file, metadata
        else:
            return []

    country = field_defaults.country()
    country.extractor = Constant('Ireland')

    chamber = field_defaults.chamber()
    chamber.extractor = Constant('Dáil')

    date = field_defaults.date()
    date.extractor = CSV('date')

    ministerial_role = field_defaults.ministerial_role()
    ministerial_role.extractor = Combined(
        CSV('memberID'),
        CSV('date'),
        Metadata('ministers'),
        transform = find_ministerial_role,
    )

    party = field_defaults.party()
    party.extractor = CSV('party_name')

    party_id = field_defaults.party_id()
    party_id.extractor = CSV('partyID')

    speaker = field_defaults.speaker()
    speaker.extractor = CSV('member_name')

    speaker_id = field_defaults.speaker_id()
    speaker_id.extractor = CSV('memberID')

    speaker_constituency = field_defaults.speaker_constituency()
    speaker_constituency.extractor = CSV('const_name')

    speech = field_defaults.speech()
    speech.extractor = CSV(
        'speech',
        multiple=True,
        transform = '\n'.join,
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = CSV('speechID')

    topic = field_defaults.topic()
    topic.extractor = CSV('title')

    sequence = field_defaults.sequence()
    sequence.extractor = CSV(
        'speechID',
        transform = formatting.extract_integer_value
    )

    source_archive = field_defaults.source_archive()
    source_archive.extractor = Constant('1919-2013')

    fields = [
        date,
        country,
        chamber,
        ministerial_role,
        party, party_id,
        speaker, speaker_id, speaker_constituency,
        speech, speech_id,
        sequence,
        source_archive,
        topic,
    ]

def get_json_metadata(directory):
    files = os.listdir(directory)
    filename = next(f for f in files if f.endswith('.json'))
    path = os.path.join(directory, filename)
    with open(path) as json_file:
        data = json.load(json_file)

    return data

def format_chamber(house_code):
    codes = {
        'dail': 'Dáil',
        'seanad': 'Seanad'
    }
    return codes.get(house_code, house_code)

def get_file_metadata(json_data, filename):

    data = next(
        file_data for file_data in json_data
        if file_data['file'] == filename
    )

    chamber_data = data['house_uri']
    useful_data = {
        'url': data['xml_url'],
        'house': format_chamber(chamber_data['houseCode']),
        'debate_type': chamber_data['chamberType'],
        'committee': chamber_data['showAs'] if chamber_data.get('committeeCode', None) else None,
        'legislature': chamber_data['houseNo'],
    }

    return useful_data


def extract_people_data(soup):
    references = soup.find(['meta', 'identification', 'references'])
    people_nodes = references.find_all('TLCPerson')
    data = map(extract_reference_data, people_nodes)
    return {
        id: person_data for id, person_data in data
    }

def extract_reference_data(reference_node):
    id = '#' + reference_node['eId']
    name = reference_node['showAs']
    return id, { 'name': name }

def extract_roles_data(soup):
    references = soup.find(['meta', 'identification', 'references'])
    role_nodes = references.find_all('TLCRole')
    data = map(extract_reference_data, role_nodes)
    return {
        id: person_data for id, person_data in data
    }

def extract_roles_from_roll_call(soup):
    '''
    Extract roles written in the roll call section
    '''

    roll_call = soup.find('rollCall')
    if not roll_call:
        return {}
    people = roll_call.find_all('person')
    return {
        person['refersTo'] : person.get('as', None)
        for person in people
    }

def find_person_in_roll_call(person, roles):
    return roles.get(person, None)

def strip_and_join_paragraphs(paragraphs):
    '''Strip whitespace from each  paragraph and join into a single string'''

    stripped = map(str.strip, filter(None, paragraphs))
    return '\n'.join(stripped)

def extract_number_from_id(id):
    match = re.search(r'\d+', id)
    if match:
        return int(match.group(0))


def get_debate_id(filename):
    name, _ = os.path.splitext(filename)
    # leave out the first segments which are the same for the whole corpus
    parts = name.split('#')
    shortened_name = '#'.join(parts[3:])
    return shortened_name


def compose(function_1, function_2):
    '''
    Compose two unary functions.
    '''
    return lambda x: function_1(function_2(x))

def role_type_filter(role_type):
    '''
    Returns a unary function that filters role names on the given type.
    I.e. only pass parliamentary roles, or only ministerial roles. For the
    other type, return None.
    '''
    parliamentary_roles = ['Chair', 'Acting Chairman']

    def filter_role(role):
        if role in parliamentary_roles:
            if role_type == 'parliamentary':
                return role
        else:
            if role_type != 'parliamentary':
                return role

    return filter_role

def role_id_extractor():
    '''
    Extractor for 2014-2020 role IDs (used in role extractor)
    '''
    from_speech_attribute = XML(attribute='as')
    from_roll_call = Combined(
        XML(attribute='by'),
        Metadata('roll_call'),
        transform = lambda data: find_person_in_roll_call(*data)
    )

    return Backup(from_speech_attribute, from_roll_call)

def role_extractor(role_type):
    '''
    Extractor for 2014-2020 roles.
    '''
    return Combined(
        role_id_extractor(),
        Metadata('roles'),
        transform = compose(
            role_type_filter(role_type),
            parlamint.metadata_attribute_transform_func('name')
        ),
    )


class ParliamentIrelandNew(XMLCorpusDefinition):
    '''
    Class for extracting 2014-2020 Irish debates.

    Only used for data extraction, use the `ParliamentIreland` class in the application.
    '''

    data_directory = settings.PP_IRELAND_DATA
    min_date = datetime(year=2014, month=1, day=1)
    max_date = datetime(year=2020, month=12, day=31)

    tag_toplevel = Tag('debate')
    tag_entry = Tag('speech')

    def sources(self, start, end):
        if in_date_range(self, start, end):
            for root, _, files in os.walk(self.data_directory):
                xml_files = [f for f in files if f.endswith('.xml')]
                if any(xml_files):
                    json_metadata = get_json_metadata(root)
                    for filename in xml_files:
                        xml_file = os.path.join(root, filename)

                        with open(xml_file) as infile:
                            soup = BeautifulSoup(infile, features = 'xml')

                        metadata = {
                            **get_file_metadata(json_metadata, filename),
                            'roles': extract_roles_data(soup),
                            'persons': extract_people_data(soup),
                            'roll_call': extract_roles_from_roll_call(soup),
                            'id': get_debate_id(filename),
                        }

                        yield xml_file, metadata
        else:
            return []

    country = field_defaults.country()
    country.extractor = Constant('Ireland')

    chamber = field_defaults.chamber()
    chamber.extractor = Metadata(
        'house'
    )

    committee = field_defaults.committee()
    committee.extractor = Metadata('committee')

    date = field_defaults.date()
    date.extractor = XML(
        Tag('docDate'),
        attribute = 'date',
        toplevel = True,
    )

    debate_type = field_defaults.debate_type()
    debate_type.extractor = Metadata('debate_type')

    ministerial_role = field_defaults.ministerial_role()
    ministerial_role.extractor = role_extractor('ministerial')

    parliamentary_role = field_defaults.parliamentary_role()
    parliamentary_role.extractor = role_extractor('parliamentary')

    party = field_defaults.party()
    party_id = field_defaults.party_id()

    speaker = field_defaults.speaker()
    speaker.extractor = parlamint.person_attribute_extractor(
        'name',
        id_attribute = 'by'
    )

    speaker_id = field_defaults.speaker_id()
    speaker_id.extractor = XML(attribute='by')

    speech = field_defaults.speech()
    speech.extractor = XML(
        Tag('p'),
        multiple = True,
        transform = strip_and_join_paragraphs,
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = Combined(
        Metadata('id'),
        XML(attribute='eId'),
        transform = lambda parts: '#'.join(parts)
    )

    topic = field_defaults.topic()
    topic.extractor = XML(
        PreviousSiblingTag('heading'),
        extract_soup_func = lambda node : node.text,
    )

    sequence = field_defaults.sequence()
    sequence.extractor = XML(
        attribute = 'eId',
        transform = extract_number_from_id,
    )

    source_archive = field_defaults.source_archive()
    source_archive.extractor = Constant('2014-2020')

    url = field_defaults.url()
    url.extractor = Metadata('url')

    fields = [
        date,
        country,
        chamber,
        committee,
        debate_type,
        ministerial_role,
        parliamentary_role,
        party, party_id,
        speaker, speaker_id,
        speech, speech_id,
        sequence,
        source_archive,
        topic,
        url,
    ]


class ParliamentIreland(Parliament, CorpusDefinition):
    '''
    Class for 1919-2020 Irish debates.
    '''

    title = 'People & Parliament (Ireland)'
    description = 'Speeches from the Dáil Éireann and Seanad Éireann'
    min_date = datetime(year=1919, month=1, day=1)
    max_date = datetime(year=2020, month=12, day=31)
    data_directory = settings.PP_IRELAND_DATA
    es_index = getattr(settings, 'PP_IRELAND_INDEX', 'parliament-ireland')
    word_model_path = getattr(settings, 'PP_IRELAND_WM', None)
    image = 'ireland.png'
    description_page = 'ireland.md'
    es_settings = {'index': {'number_of_replicas': 0}} # do not include analyzers in es_settings
    languages = ['en', 'ga']

    @property
    def subcorpora(self):
        return [
            ParliamentIrelandOld(),
            ParliamentIrelandNew(),
        ]

    def sources(self, start, end):
        for i, subcorpus in enumerate(self.subcorpora):
            for source in subcorpus.sources(start, end):
                filename, metadata = source
                metadata['subcorpus'] = i
                yield filename, metadata

    def source2dicts(self, source):
        filename, metadata = source

        subcorpus_index = metadata['subcorpus']
        subcorpus = self.subcorpora[subcorpus_index]

        docs = subcorpus.source2dicts(source)
        for doc in docs:
            yield {
                field.name : doc.get(field.name, None)
                for field in self.fields
            }

    country = field_defaults.country()
    chamber = field_defaults.chamber()
    committee = field_defaults.committee()
    debate_type = field_defaults.debate_type()

    date = field_defaults.date()
    date.search_filter.lower = min_date
    date.search_filter.upper = max_date

    ministerial_role = field_defaults.ministerial_role()
    parliamentary_role = field_defaults.parliamentary_role()
    party = field_defaults.party()
    party_id = field_defaults.party_id()
    speaker = field_defaults.speaker()
    speaker_id = field_defaults.speaker_id()
    speaker_constituency = field_defaults.speaker_constituency()

    # no language-specific analysers since the corpus is mixed-language
    speech = field_defaults.speech()

    speech_id = field_defaults.speech_id()
    topic = field_defaults.topic()
    sequence = field_defaults.sequence()
    source_archive = field_defaults.source_archive()
    url = field_defaults.url()

    def __init__(self):
        self.fields = [
            self.country,
            self.date,
            self.chamber,
            self.committee,
            self.debate_type,
            self.ministerial_role,
            self.parliamentary_role,
            self.party, self.party_id,
            self.speaker, self.speaker_id, self.speaker_constituency,
            self.speech, self.speech_id,
            self.sequence,
            self.source_archive,
            self.topic,
            self.url,
        ]
