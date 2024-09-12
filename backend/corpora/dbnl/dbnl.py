from datetime import datetime
import os
import re
from tqdm import tqdm
from ianalyzer_readers.xml_tag import Tag, CurrentTag, TransformTag

from django.conf import settings
from addcorpus.python_corpora.corpus import XMLCorpusDefinition, FieldDefinition
from addcorpus.python_corpora.extract import Metadata, XML, Pass, Order, Backup, Combined
import corpora.dbnl.utils as utils
from addcorpus.es_mappings import *
from addcorpus.python_corpora.filters import RangeFilter, MultipleChoiceFilter, BooleanFilter
from corpora.dbnl.dbnl_metadata import DBNLMetadata

class DBNL(XMLCorpusDefinition):
    title = 'DBNL'
    description = 'Digital Library for Dutch Literature'
    data_directory = settings.DBNL_DATA
    min_date = datetime(year=1200, month=1, day=1)
    max_date = datetime(year=1890, month=12, day=31)
    es_index = getattr(settings, 'DBNL_ES_INDEX', 'dbnl')
    image = 'dbnl.png'
    description_page = 'dbnl.md'
    citation_page = 'citation.md'

    languages = ['nl', 'dum', 'fr', 'la', 'fy', 'lat', 'en', 'nds', 'de', 'af']
    category = 'book'

    tag_toplevel = Tag('TEI.2')
    tag_entry = Tag('div', type='chapter')

    document_context = {
        'context_fields': ['title_id'],
        'sort_field': 'chapter_index',
        'sort_direction': 'asc',
        'context_display_name': 'book'
    }

    language_field = 'language_code'

    def sources(self, start = None, end = None):
        metadata_corpus = DBNLMetadata()
        all_metadata = utils.index_by_id(metadata_corpus.documents())

        print('Extracting XML files...')
        for id, path in tqdm(list(self._xml_files())):
            metadata_id, *_ = re.split(r'_(?=\d+$)', id)
            csv_metadata = all_metadata.pop(metadata_id)
            metadata = {
                'id': id,
                'has_xml': True,
                **csv_metadata
            }

            year = int(metadata['year'])
            if utils.between_years(year, start, end):
                yield path, metadata

        # we popped metadata while going through the XMLs
        # now add data for the remaining records (without text)

        print('Extracting metadata-only records...')
        with utils.BlankXML(self.data_directory) as blank_file:
            for id in tqdm(all_metadata):
                csv_metadata = all_metadata[id]
                metadata = {
                    'id': id,
                    'has_xml': False,
                    **csv_metadata
                }
                year = int(metadata['year'])
                if utils.between_years(year, start, end):
                    yield blank_file, metadata

    def _xml_files(self):
        xml_dir = os.path.join(self.data_directory, 'xml_pd')
        for filename in os.listdir(xml_dir):
           if filename.endswith('.xml'):
               id, _ = os.path.splitext(filename)
               path = os.path.join(xml_dir, filename)
               yield id, path

    title_field = FieldDefinition(
        name='title',
        display_name='Title',
        description='Title of the book',
        results_overview=True,
        search_field_core=True,
        csv_core=True,
        extractor=Metadata('title'),
        es_mapping=text_mapping(),
        visualizations=['wordcloud']
    )

    title_id = FieldDefinition(
        name='title_id',
        display_name='Title ID',
        description='ID of the book',
        extractor = Metadata('id'),
        es_mapping=keyword_mapping()
    )

    id = FieldDefinition(
        name='id',
        es_mapping=keyword_mapping(),
        extractor=Combined(
            Metadata('id'),
            Order(transform=lambda i: str(i).zfill(4)),
            transform='_'.join,
        )
    )

    volumes = FieldDefinition(
        name='volumes',
        display_name='Volumes',
        description='Number of volumes in which this book was published',
        extractor=Metadata('volumes'),
        es_mapping=text_mapping(),
    )

    # text version of the year, can include things like 'ca. 1500', '14e eeuw'
    year_full = FieldDefinition(
        name='year_full',
        display_name='Publication year',
        description='Year of publication in text format. May describe a range.',
        results_overview=True,
        csv_core=True,
        extractor=Metadata('year_full'),
        es_mapping=text_mapping(),
    )

    # version of the year that is always a number
    year_int = FieldDefinition(
        name='year',
        display_name='Publication year (est.)',
        description='Year of publication as a number. May not be an estimate.',
        extractor=Metadata('year'),
        es_mapping=int_mapping(),
        search_filter=RangeFilter(
            description='Select books by publication year',
        ),
        visualizations=['resultscount', 'termfrequency'],
        sortable=True,
        visualization_sort='key',
    )

    edition = FieldDefinition(
        name='edition',
        display_name='Edition',
        description='Edition of the book',
        extractor=Metadata('edition'),
        es_mapping=text_mapping(),
    )

    periodical = FieldDefinition(
        name='periodical',
        display_name='Periodical',
        description='Periodical in which the text appeared',
        extractor=Metadata('periodical'),
        es_mapping=keyword_mapping(),
        search_filter=MultipleChoiceFilter(
            description='Select texts from periodicals',
        ),
        visualizations=['resultscount', 'termfrequency'],
    )

    author = FieldDefinition(
        name='author',
        display_name='Author',
        description='Name(s) of the author(s)',
        results_overview=True,
        search_field_core=True,
        csv_core=True,
        extractor=Metadata('author_name'),
        es_mapping=keyword_mapping(enable_full_text_search=True),
        visualizations=['resultscount', 'termfrequency'],
    )

    author_id = FieldDefinition(
        name='author_id',
        display_name='Author ID',
        description='ID(s) of the author(s)',
        extractor=Metadata('author_id'),
        es_mapping=keyword_mapping(),
    )

    author_year_of_birth = FieldDefinition(
        name='author_year_of_birth',
        display_name='Author year of birth',
        description='Year in which the author(s) was(/were) born',
        extractor=Metadata('author_year_of_birth'),
        es_mapping=text_mapping(),
    )

    author_year_of_death = FieldDefinition(
        name='author_year_of_death',
        display_name='Author year of death',
        description='Year in which the author(s) died',
        extractor=Metadata('author_year_of_death'),
        es_mapping=text_mapping(),
    )

    # the above fields are also given as proper dates in geb_datum / overl_datum
    # but implementing them as date fields requires support for multiple values

    author_place_of_birth = FieldDefinition(
        name='author_place_of_birth',
        display_name='Author place of birth',
        description='Place the author(s) was(/were) born',
        extractor=Metadata('author_place_of_birth'),
        es_mapping=keyword_mapping(),
    )

    author_place_of_death = FieldDefinition(
        name='author_place_of_death',
        display_name='Author place of death',
        description='Place where the author(s) died',
        extractor=Metadata('author_place_of_death'),
        es_mapping=keyword_mapping(),
    )

    author_gender = FieldDefinition(
        name='author_gender',
        display_name='Author gender',
        description='Gender of the author(s)',
        extractor=Metadata('author_gender'),
        es_mapping=keyword_mapping(),
        search_filter=MultipleChoiceFilter(
            description='Select books based on the gender of the author(s)',
        ),
        visualizations=['resultscount', 'termfrequency'],
    )

    url = FieldDefinition(
        name='url',
        display_name='Source URL',
        display_type='url',
        description='Link to the book\'s page in DBNL',
        extractor=Metadata('url'),
        es_mapping=keyword_mapping(),
    )

    genre = FieldDefinition(
        name='genre',
        display_name='Genre',
        description='Genre of the book',
        extractor=Metadata('genre'),
        es_mapping=keyword_mapping(),
        search_filter=MultipleChoiceFilter(
            description='Select books in these genres',
        ),
        visualizations=['resultscount', 'termfrequency'],
    )

    language = FieldDefinition(
        name='language',
        display_name='Language',
        description='Language in which the book is written',
        # this extractor is similar to language_code below,
        # but designed to accept multiple values in case of uncertainty
        extractor=Pass(
            Pass(
                Backup(
                    XML( # get the language on chapter-level if available
                        CurrentTag(),
                        attribute='lang',
                        transform=lambda value: [value] if value else None,
                    ),
                    XML( # look for section-level codes
                        Tag('div', type='section'),
                        attribute='lang',
                        multiple=True,
                    ),
                    XML( # look in the top-level metadata
                        Tag('language'),
                        toplevel=True,
                        multiple=True,
                        attribute='id'
                    ),
                    transform = lambda codes: map(utils.language_name, codes) if codes else None,
                ),
                transform=utils.sorted_and_unique,
            ),
            transform=utils.join_values,
        ),
        es_mapping=keyword_mapping(),
        search_filter=MultipleChoiceFilter(
            description='Select books in these languages',
            option_count=20,
        ),
        visualizations=['resultscount', 'termfrequency'],
    )

    language_code = FieldDefinition(
        name='language_code',
        display_name='Language code',
        description='ISO code of the text\'s language',
        # as this may be used to set the HTML lang attribute, it forces a single value
        extractor=Pass(
            Backup(
                XML( # get the language on chapter-level if available
                    CurrentTag(),
                    attribute='lang',
                ),
                XML( # look for section-level code
                    Tag('div', type='section'),
                    attribute='lang'
                ),
                XML( #otherwise, get the (first) language for the book
                    Tag('language'),
                    attribute='id',
                    toplevel=True,
                ),
                transform=utils.single_language_code,
            ),
            transform=utils.standardize_language_code,
        ),
        es_mapping=keyword_mapping(),
    )

    chapter_title = FieldDefinition(
        name='chapter_title',
        display_name='Chapter',
        extractor=Backup(
            XML(
                Tag('head'),
                flatten=True,
            ),
            XML(
                Tag(utils.LINE_TAG),
                flatten=True,
            )
        ),
        results_overview=True,
        search_field_core=True,
        csv_core=True,
        visualizations=['wordcloud'],
    )

    chapter_index = FieldDefinition(
        name='chapter_index',
        display_name='Chapter index',
        description='Order of this chapter within the book',
        extractor=Order(
            transform=lambda x : x + 1,
            applicable=lambda metadata: metadata['has_xml']
        ),
        es_mapping=int_mapping(),
        sortable=True,
    )

    content = FieldDefinition(
        name='content',
        display_name='Content',
        description='Text in this chapter',
        display_type='text_content',
        results_overview=True,
        search_field_core=True,
        csv_core=True,
        extractor=XML(
            Tag(utils.LINE_TAG),
            TransformTag(utils.pad_content),
            TransformTag(utils.replace_notes_with_ref),
            multiple=True,
            flatten=True,
            transform=utils.join_paragraphs,
        ),
        es_mapping=main_content_mapping(token_counts=True),
        visualizations=['wordcloud'],
        language='dynamic',
    )

    notes = FieldDefinition(
        name='notes',
        display_name='Notes',
        description='Notes (e.g. footnotes) added to the content',
        display_type='text_content',
        results_overview=False,
        search_field_core=True,
        csv_core=True,
        extractor=XML(
            Tag('note'),
            TransformTag(utils.pad_content),
            TransformTag(utils.insert_ref),
            multiple=True,
            flatten=True,
            transform=utils.join_paragraphs,
        ),
        es_mapping=main_content_mapping(token_counts=True),
        visualizations=['wordcloud'],
        language='dynamic',
    )

    has_content = FieldDefinition(
        name='has_content',
        display_name='Content available',
        description='Whether the contents of this book are available on I-analyzer',
        extractor=Metadata('has_xml'),
        es_mapping=bool_mapping(),
        search_filter=BooleanFilter(
            description='Select books with text available on I-analyzer, or metadata-only books',
            true='Content available',
            false='Metadata only'
        ),
    )

    is_primary = FieldDefinition(
        name='is_primary',
        display_name='Primary',
        description='Whether this is the primary document for this book - each book has only one primary document',
        extractor=Order(transform = lambda index : index == 0),
        es_mapping=bool_mapping(),
        search_filter=BooleanFilter(
            true='Primary',
            false='Other',
            description='Select only primary documents - i.e. only one result per book',
        )
    )

    fields = [
        title_field,
        title_id,
        id,
        volumes,
        edition,
        periodical,
        year_full,
        year_int,
        author,
        author_id,
        author_year_of_birth,
        author_place_of_birth,
        author_year_of_death,
        author_place_of_death,
        author_gender,
        url,
        genre,
        language,
        language_code,
        chapter_title,
        chapter_index,
        content,
        notes,
        has_content,
        is_primary,
    ]
