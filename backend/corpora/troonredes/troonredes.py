'''
Collect corpus-specific information, that is, data structures and file
locations.
'''

import logging
logger = logging.getLogger(__name__)
import os
from os.path import join, splitext
from datetime import datetime
from ianalyzer_readers.xml_tag import Tag

from django.conf import settings

from addcorpus.python_corpora import extract
from addcorpus.python_corpora import filters
from addcorpus.python_corpora.corpus import XMLCorpusDefinition, FieldDefinition

from addcorpus.es_mappings import keyword_mapping, main_content_mapping
from addcorpus.es_settings import es_settings

# Source files ################################################################
MONARCHS = ['Willem I', 'Willem II', 'Willem III', 'Emma',
            'Wilhelmina', 'Juliana', 'Beatrix', 'Willem-Alexander']

SPEECH_TYPES = ['openingsrede', 'troonrede',
                'inhuldigingsrede', 'abdicatierede', 'other']


class Troonredes(XMLCorpusDefinition):
    title = "Troonredes"
    description = "Speeches by Dutch monarchs"
    min_date = datetime(year=1814, month=1, day=1)
    max_date = datetime(year=2023, month=12, day=31)
    data_directory = settings.TROONREDES_DATA
    es_index = getattr(settings, 'TROONREDES_ES_INDEX', 'troonredes')
    image = 'troon.jpg'
    word_model_path = getattr(settings, 'TROONREDES_WM', None)
    languages = ['nl']
    category = 'oration'
    description_page = 'troonredes.md'
    citation_page = 'citation.md'
    wordmodels_page = 'documentation.md'

    @property
    def es_settings(self):
        return es_settings(self.languages[:1], stopword_analysis=True, stemming_analysis=True)

    tag_toplevel = Tag('doc')
    tag_entry = Tag('entry')

    non_xml_msg = 'Skipping non-XML file {}'

    def sources(self, start=min_date, end=max_date):
        logger = logging.getLogger(__name__)
        for directory, _, filenames in os.walk(self.data_directory):
            for filename in filenames:
                if filename != '.DS_Store':
                    name, extension = splitext(filename)
                    full_path = join(directory, filename)
                    if extension != '.xml':
                        logger.debug(self.non_xml_msg.format(full_path))
                        continue
                    yield full_path, {'id': name}

    fields = [
        FieldDefinition(
            name='date',
            display_name='Date',
            description='Date of the speech',
            extractor=extract.XML(Tag('date')),
            es_mapping={'type': 'date', 'format': 'yyyy-MM-dd'},
            results_overview=True,
            csv_core=True,
            search_filter=filters.DateFilter(
                description=(
                    'Accept only speeches given between these dates.'
                )
            ),
            sortable=True
        ),
        FieldDefinition(
            name='id',
            display_name='ID',
            description='Unique identifier of the entry.',
            es_mapping=keyword_mapping(),
            extractor=extract.Metadata('id')
        ),
        FieldDefinition(
            name='title',
            display_name='Title',
            description='title.',
            extractor=extract.XML(Tag('title')),
            results_overview=True,
            search_field_core=True,
            language='nl',
        ),
        FieldDefinition(
            name='monarch',
            display_name='Monarch',
            description='Monarch that gave the speech.',
            extractor=extract.XML(Tag('monarch')),
            es_mapping={'type': 'keyword'},
            results_overview=True,
            csv_core=True,
            visualizations=['resultscount', 'termfrequency'],
            search_filter=filters.MultipleChoiceFilter(
                description=(
                    'Accept only speeches given by '
                    'the relevant monarch.'
                ),
                option_count=len(MONARCHS)
            ),
        ),
        FieldDefinition(
            name='speech_type',
            display_name='Speech type',
            description='Type of speech.',
            extractor=extract.XML(Tag('speech_type')),
            es_mapping={'type': 'keyword'},
            results_overview=True,
            csv_core=True,
            visualizations=['resultscount', 'termfrequency'],
            search_filter=filters.MultipleChoiceFilter(
                description=(
                    'Accept only speeches of '
                    'the relevant type.'
                ),
                option_count=len(SPEECH_TYPES)
            ),
        ),
        FieldDefinition(
            name='content',
            display_name='Content',
            display_type='text_content',
            description='Text content.',
            es_mapping=main_content_mapping(True, True, True, 'nl'),
            results_overview=True,
            search_field_core=True,
            visualizations=['wordcloud', 'ngram'],
            extractor=extract.XML(Tag('content')),
            language='nl',
        ),
    ]
