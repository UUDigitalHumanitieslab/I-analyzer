'''
Collect corpus-specific information, that is, data structures and file
locations.
'''
import os
from os.path import join, dirname, isfile, split, splitext
from datetime import datetime, timedelta
import logging
import re
from io import BytesIO

from flask import current_app, url_for

from addcorpus.extract import Combined, Metadata, XML
from addcorpus import filters
from addcorpus.corpus import XMLCorpus, Field, consolidate_start_end_years, string_contains
from addcorpus.image_processing import retrieve_pdf


# Source files ################################################################


class Ecco(XMLCorpus):
    title = "Eighteenth Century Collections Online"
    description = "Digital collection of books published in Great Britain during the 18th century."
    min_date = datetime(year=1700, month=1, day=1)
    max_date = datetime(year=1800, month=12, day=31)

    data_directory = current_app.config['ECCO_DATA']
    es_index = current_app.config['ECCO_ES_INDEX']
    es_doctype = current_app.config['ECCO_ES_DOCTYPE']
    image = current_app.config['ECCO_IMAGE']
    scan_image_type = current_app.config['ECCO_SCAN_IMAGE_TYPE']
    es_settings = None

    tag_toplevel = 'pageContent'
    tag_entry = 'page'

    meta_pattern = re.compile('^\d+\_DocMetadata\.xml$')

    def sources(self, start=min_date, end=max_date):
        logging.basicConfig(filename='ecco.log', level=logging.INFO)

        for directory, subdirs, filenames in os.walk(self.data_directory):
            _body, tail = split(directory)
            if tail.startswith('.'):
                subdirs[:] = []
                continue
            elif tail.startswith('ECCOI'):
                category = tail[6:]

            for filename in filenames:
                if not filename.startswith('.'):
                    name, extension = splitext(filename)
                    full_path = join(directory, filename)
                    if extension != '.xml':
                        # TODO: change to logger
                        #logging.debug(self.non_xml_msg.format(full_path))
                        continue

                    # text_match = self.text_pattern.match(filename)
                    meta_match = self.meta_pattern.match(filename)

                    if meta_match:
                        record_id = name.split('_')[0]
                        text_filepath = join(
                            directory, '{}_PageText.xml'.format(record_id))
                        if not isfile(text_filepath):
                            logging.warning(
                                '{} is not a file'.format(text_filepath))
                            continue

                        meta_tags = [
                            'collation',
                            {'tag': 'author', 'subtag': 'composed'},
                            'fullTitle',
                            'imprintFull',
                            'libraryName',
                            'ocr',
                            'pubDateStart',
                            'publicationPlaceComposed',
                            'Volume'
                        ]

                        meta_dict = self.metadata_from_xml(
                            full_path, tags=meta_tags)
                        meta_dict['id'] = record_id
                        meta_dict['category'] = category
                        parts = directory.split('/')
                        image_dir = join('/', join(*parts[:-3]),'Images', parts[-1], parts[-2])
                        meta_dict['image_dir'] = image_dir

                        yield(text_filepath, meta_dict)

    @property
    def fields(self):
        return [
            Field(
            name='id',
            display_name='ID',
            description='Unique identifier of the entry.',
            extractor=Combined(Metadata('id'),
            XML(attribute='id'),
            transform=lambda x: '_'.join(x))
        ),
            Field(
                name='year',
                display_name='Year',
                description='Publication year.',
                es_mapping={'type': 'date', 'format': 'yyyy'},
                results_overview=True,
                csv_core=True,
                visualization_type='timeline',
                search_filter=filters.RangeFilter(
                    1700,
                    1800,
                    description=(
                        'Accept only book pages with publication year in this range.'
                    )
                ),
                extractor=Metadata('pubDateStart', transform=lambda x: x[:4])
            ),
            Field(
                name='title',
                display_name='Title',
                description='The title of the book',
                extractor=Metadata('fullTitle'),
                es_mapping={'type': 'keyword'},
                results_overview=True,
                search_field_core=True,
                csv_core=True,
                search_filter=filters.MultipleChoiceFilter(
                    description="Accept only pages from these books",
                    option_count=500
                )
            ),
            Field(
                name='content',
                display_name='Content',
                display_type='text_content',
                description='Text content.',
                results_overview=True,
                search_field_core=True,
                extractor=XML(tag='ocrText',
                              flatten=True),
                visualization_type="word_cloud"
            ),
            Field(
                name='ocr',
                display_name='OCR quality',
                description='Optical character recognition quality',
                extractor=Metadata('ocr'),
                es_mapping={'type': 'float'},
                search_filter=filters.RangeFilter(
                    0, 
                    100,
                    description=(
                        'Accept only book pages for which the Opitical Character Recognition '
                        'confidence indicator is in this range.'
                    )
                ),
            ),
            Field(
                name='author',
                display_name='Author',
                description='The author of the book',
                es_mapping={'type': 'keyword'},
                results_overview=True,
                csv_core=True,
                extractor=Metadata('author'),
                search_field_core=True,
                search_filter=filters.MultipleChoiceFilter(
                    description='Accept only book pages by these authors.',
                    option_count=25391
                )
            ),
            Field(
                name='page',
                display_name='Page number',
                description='Number of the page on which match was found',
                extractor=XML(attribute='id', transform=lambda x: int(int(x)/10))
            ),
            Field(
                name='pub_place',
                display_name='Publication place',
                description='Where the book was published',
                extractor=Metadata('publicationPlaceComposed')
            ),
            Field(
                name='collation',
                display_name='Collation',
                description='Information about the volume',
                extractor=Metadata('collation')
            ),
            Field(
                name='category',
                display_name='Category',
                description='Which category this book belongs to',
                extractor=Metadata('category'),
                es_mapping={'type': 'keyword'},
                search_filter=filters.MultipleChoiceFilter(
                description='Accept only book pages in these categories.',
                option_count=7
            ),
            ),
            Field(
                name='imprint',
                display_name='Printer',
                description='Information of the printer and publisher of the book',
                extractor=Metadata('imprintFull')
            ),
            Field(
                name='library',
                display_name='Holding library',
                description='The main holding library of the book',
                extractor=Metadata('libraryName')
            ),
            Field(
                name='volume',
                display_name='Volume',
                description='The book volume',
                extractor=Metadata('Volume')
            ),
            Field(
                name='image_path',
                hidden=True,
                extractor=Combined(Metadata('image_dir'), Metadata('id'), transform=lambda x: '/'.join(x))
            )
        ]


    def request_media(self, document):
        image_url = url_for('api.api_get_media', 
            corpus=self.es_index,
            image_path=document['fieldValues']['image_path'],
            page_no=document['fieldValues']['page'],
            _external=True
        )
        return [image_url]
    
    
    def get_media(self, request_args):
        image_path = request_args['image_path']
        filename = '{}.pdf'.format(split(image_path)[1])
        full_path = join(image_path, filename)
        page_no = request_args['page_no']
        pdf_data, pdf_stats = retrieve_pdf(full_path)
        pdf_info = {
            "pageNumbers": pdf_stats['all_pages'], #change from 0-indexed to real page
            "homePageIndex": page_no, #change from 0-indexed to real page
            "fileName": filename,
            "fileSize": pdf_stats['filesize']
        }
        with open(full_path, 'rb') as f:
            pdf_data = f.read()
        return BytesIO(pdf_data), pdf_info
