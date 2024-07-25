from datetime import datetime
import os
import re

from django.conf import settings
from rdflib import Graph, URIRef
from rdflib.namespace import RDF
from ianalyzer_readers.readers.rdf import RDFReader
from ianalyzer_readers.extract import Backup, Combined, RDF

from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults


def get_id(input):
    return os.path.split(input)[1]


def extract_party_name(input):
    ''' extract the party name, which, if given,
    is stated in brackets after the name of the speaker
    '''
    speaker_info = input.split(' ')
    if len(speaker_info) == 2:
        return speaker_info[1][1:-1]

def get_speech_index(input):
    speeches, speech = input
    return speeches.index(speech)

def get_speech_text(input):
    ''' Extract the speech text, discarding the potential
    source language indication
    '''
    if input and input.startswith('('):
        return ' '.join(input.split(' ')[1:])
    return input


class ParliamentEurope(Parliament, RDFReader):
    """
    Example XML reader for testing
    """
    title = 'People & Parliament (European Parliament)'
    description = "Speeches from the European Parliament (EP)"
    min_date = datetime(year=1999, month=7, day=20)
    max_data = datetime(year=2017, month=7, day=6)
    data_directory = settings.PP_EUPARL_DATA
    es_index = getattr(settings, 'PP_EUPARL_INDEX', 'parliament-euparl')
    languages = ['en']
    description_page = 'euparl.md'
    image = 'euparl.jpeg'

    def sources(self, **kwargs):
        yield os.path.join(self.data_directory, 'EUParl.ttl')

    def document_subjects(self, graph: Graph):
        return graph.subjects(RDF.type, URIRef('http://purl.org/linkedpolitics/vocabulary/speech'))

    debate_id = field_defaults.debate_id()
    debate_id.extractor = RDF(
        URIRef('http://purl.org/dc/terms/isPartOf')
    )

    debate_title = field_defaults.debate_title()
    debate_title.extractor = RDF(
        URIRef('http://purl.org/dc/terms/isPartOf'),
        URIRef('http://purl.org/dc/terms/title')
    )

    date = field_defaults.date()
    date.extractor = RDF(
        URIRef('http://purl.org/dc/terms/date')
    )

    speaker = field_defaults.speaker()
    speaker.extractor = RDF(
        URIRef('http://purl.org/linkedpolitics/vocabulary/speaker'),
        URIRef('http://xmlns.com/foaf/0.1/name')
    )

    party = field_defaults.party()
    party.extractor = RDF(
        URIRef('http://purl.org/linkedpolitics/vocabulary/unclassifiedMetadata'),
        transform=extract_party_name
    )

    sequence = field_defaults.sequence()
    sequence.extractor = (
        Combined(
            RDF(
                URIRef('http://purl.org/linkedpolitics/eu/plenary/')
            ),
            RDF(
                URIRef('http://purl.org/dc/terms/isPartOf'),
                URIRef('http://purl.org/dc/terms/hasPart'),
                multiple=True
            ),
            transform=get_speech_index
        )
    )

    source_language = field_defaults.language()
    source_language.display_name = 'Source language'
    source_language.description = 'Original language of the speech'
    source_language.search_filter.description = 'Search only in speeches in the selected source languages',
    source_language.extractor = RDF(
        URIRef('http://purl.org/dc/terms/language')
    )


    speech = field_defaults.speech(language='en')
    speech.extractor = Backup(
        RDF(
            URIRef('http://purl.org/linkedpolitics/vocabulary/translatedText'),
            transform=get_speech_text,
        ),
        RDF(
            URIRef('http://purl.org/linkedpolitics/vocabulary/spokenText'),
            transform=get_speech_text
        )
    )


    speech_id = field_defaults.speech_id()
    speech_id.extractor = RDF(
        URIRef('http://purl.org/linkedpolitics/eu/plenary/'),
        node_type='subject',
        transform=get_id
    )

    url = field_defaults.url()
    url.extractor = RDF(
        URIRef('http://purl.org/linkedpolitics/eu/plenary/'),
        node_type='subject',
        transform=lambda x: str(x)
    )

    def __init__(self):
        self.fields = [
            self.date,
            self.debate_id,
            self.debate_title,
            self.party,
            self.sequence,
            self.speaker,
            self.speech, self.speech_id,
            self.url
        ]

    fields = [date, speaker, party, speech, speech_id, source_language, url]
