from glob import glob
from bs4 import BeautifulSoup
import re
import logging
from os.path import join
from datetime import datetime

from flask import current_app

from addcorpus.extract import Constant, Combined, XML
from addcorpus.corpus import XMLCorpus, Field
from corpora.parliament.netherlands import ParliamentNetherlands
import corpora.parliament.utils.field_defaults as field_defaults

with open(join(current_app.config['PP_NL_RECENT_DATA'], 'ParlaMint-NL.xml'), 'rb') as f:
    soup = BeautifulSoup(f.read(), 'xml')

def format_house(url):
    ''' given a string of either eerstekamer.nl or tweedekamer.nl,
    return a string "Eerste Kamer" or "Tweede Kamer" '''
    try:
        split_string = url.split('.')[-2]
    except:
        return None
    if split_string=='eerstekamer':
        return 'Eerste Kamer'
    else:
        return 'Tweede Kamer'

def get_speaker(who):
    person = get_person(who)
    surname = person.find('surname').text
    forename = person.find('forename').textc
    return '{} {}'.format(forename, surname)

def get_person(who):
    person = soup.find(attrs={'xml:id':who[1:]})
    return person

def get_party_id(who):
    person = get_person(who)
    if not person:
        return None
    member_of = person.find(attrs={'role': 'member'})
    if not member_of:
        return None
    party_id = member_of.attrs['ref']
    return party_id

def get_party(who):
    party_id = get_party_id(who)
    if not party_id:
        return None
    party = soup.find(attrs={'xml:id':party_id[1:]}).find(attrs={'full': 'init'}).text
    return party

def get_party_full(who):
    party_id = get_party_id(who)
    if not party_id:
        return None
    party = soup.find(attrs={'xml:id':party_id[1:]}).find(attrs={'full': 'yes'}).text
    return party

class ParliamentNetherlandsRecent(ParliamentNetherlands, XMLCorpus):
    """ Corpus definition of recent Dutch parliamentary data,
    saved in ParlaMINT TEI xml format
    """
    data_directory = current_app.config['PP_NL_RECENT_DATA']
    tag_entry = 'u'
    tag_toplevel = 'TEI'
    es_index = current_app.config['PP_NL_INDEX']
    min_date = datetime(year=2015, month=1, day=1)
    max_date = datetime(year=2020, month=12, day=31)

    def sources(self, start, end):
        logger = logging.getLogger(__name__)
        for year in range(start.year, end.year+1):
            for xml_file in glob('{}/{}/*.xml'.format(self.data_directory, year)):
                yield xml_file

    country = field_defaults.country()
    country.extractor = Constant(
        value='Netherlands'
    )

    date = field_defaults.date()
    date.extractor = XML(
        tag=['teiHeader', 'fileDesc', 'sourceDesc','bibl', 'date'],
        toplevel=True
    )

    house = field_defaults.house()
    house.extractor = XML(
        tag=['teiHeader', 'fileDesc', 'sourceDesc','bibl','idno'],
        toplevel=True,
        transform=format_house
    )

    debate_title = field_defaults.debate_title()
    debate_title.extractor = XML(
        tag=['teiHeader', 'fileDesc', 'titleStmt', 'title'],
        multiple=True,
        toplevel=True,
        transform=lambda titles: titles[-2] if len(titles) else titles
    )

    debate_id = field_defaults.debate_id()
    debate_id.extractor = XML(
        tag=None,
        attribute='xml:id',
        toplevel=True,
    )

    topic = field_defaults.topic()
    topic.extractor = XML(
        tag=['note'],
        toplevel=True,
        recursive=True
    )

    party_id = field_defaults.party_id()
    party_id.extractor = XML(
        tag=None,
        attribute='who',
        transform=get_party_id
    )

    party = field_defaults.party()
    party.extractor = XML(
        tag=None,
        attribute='who',
        transform=get_party
    )

    speech = field_defaults.speech()
    speech.es_mapping = ParliamentNetherlands.speech.es_mapping
    speech.extractor = XML(
        tag=['seg'],
        multiple=True,
        flatten=True,
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = XML(
        tag=None,
        attribute='xml:id'
    )

    speaker = field_defaults.speaker()
    speaker.extractor = XML(
        tag=None,
        attribute='who',
        transform=get_speaker
    )

    speaker_id = field_defaults.speaker_id()
    speaker_id.extractor = XML(
        tag=None,
        attribute='who'
    )

    role = field_defaults.role()
    role.extractor = XML(
        tag=None,
        attribute='ana',
        transform=lambda x: x[1:].title()
    )

    party_full = field_defaults.party_full()
    party_full.extractor = XML(
        tag=None,
        attribute='who',
        transform=get_party_full
    )

    page = field_defaults.page()
