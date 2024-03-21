import csv
import re
import os
import os.path as op
import logging
from datetime import datetime

from django.conf import settings

from addcorpus.python_corpora.extract import XML, Metadata, Combined
from addcorpus.python_corpora.filters import MultipleChoiceFilter, RangeFilter
from addcorpus.python_corpora.corpus import XMLCorpusDefinition, FieldDefinition
from media.image_processing import get_pdf_info, retrieve_pdf, pdf_pages, build_partial_pdf
from addcorpus.python_corpora.load_corpus import corpus_dir
from addcorpus.es_mappings import keyword_mapping, main_content_mapping
from addcorpus.es_settings import es_settings

from media.media_url import media_url

class DutchAnnualReports(XMLCorpusDefinition):
    """ Alto XML corpus of Dutch annual reports. """

    # Data overrides from .common.Corpus (fields at bottom of class)
    title = "Dutch Annual Reports"
    description = "Annual reports of Dutch financial and non-financial institutes"
    min_date = datetime(year=1957, month=1, day=1)
    max_date = datetime(year=2008, month=12, day=31)
    data_directory = settings.DUTCHANNUALREPORTS_DATA
    es_index = getattr(settings, 'DUTCHANNUALREPORTS_ES_INDEX', 'dutchannualreports')
    image = 'dutchannualreports.jpg'
    scan_image_type = getattr(settings, 'DUTCHANNUALREPORTS_SCAN_IMAGE_TYPE', 'application/pdf')
    description_page = 'dutchannualreports.md'
    allow_image_download = getattr(settings, 'DUTCHANNUALREPORTS_ALLOW_IMAGE_DOWNLOAD', True)
    word_model_path = getattr(settings, 'DUTCHANNUALREPORTS_WM', None)

    languages = ['nl']
    category = 'finance'

    mimetype = 'application/pdf'

    # Data overrides from .common.XMLCorpus
    tag_toplevel = 'alto'
    tag_entry = 'Page'

    # New data members
    non_xml_msg = 'Skipping non-XML file {}'
    non_match_msg = 'Skipping XML file with nonmatching name {}'

    dutchannualreports_map = {}

    @property
    def es_settings(self):
        return es_settings(self.languages[:1], stopword_analysis=True, stemming_analysis=True)

    with open(op.join(corpus_dir('dutchannualreports'), 'dutchannualreports_mapping.csv')) as f:
        reader = csv.DictReader(f)
        for line in reader:
            dutchannualreports_map[line['abbr']] = line['name']

    def sources(self, start=min_date, end=max_date):
         # make the mapping dictionary from the csv file defined in config
        logger = logging.getLogger(__name__)
        for directory, _, filenames in os.walk(self.data_directory):
            rel_dir = op.relpath(directory, self.data_directory)
            _, tail = op.split(directory)
            if tail == "Financials":
                company_type = "Financial"
            elif tail == "Non-Financials":
                company_type = "Non-Financial"
            for filename in filenames:
                name, extension = op.splitext(filename)
                full_path = op.join(directory, filename)
                file_path = op.join(rel_dir, filename)
                image_path = op.join(
                    rel_dir, name + '.' + self.scan_image_type)
                if extension != '.xml':
                    logger.debug(self.non_xml_msg.format(full_path))
                    continue
                information = re.split("_", name)
                # financial folders contain multiple xmls, ignore the abby files
                if information[-1] == "abby" or len(information[-1]) > 5:
                    continue
                company = information[0]
                if re.match("[a-zA-Z]+", information[1]):
                    # second part of file name is part of company name
                    company = "_".join([company, information[1]])
                # using first four-integer string in the file name as year
                years = re.compile("[0-9]{4}")
                year = next((info for info in information
                             if re.match(years, info)), None)
                if len(information) == 3:
                    serial = information[-1]
                    scan = "00001"
                else:
                    serial = information[-2]
                    scan = information[-1]
                # to do: what about year reports which are combined (e.g. "1969_1970" in filepath)
                # or which cover parts of two years ("br" in filepath)?
                if int(year) < start.year or end.year < int(year):
                    continue
                yield full_path, {
                    'file_path': file_path,
                    'image_path': image_path,
                    'company': company,
                    'company_type': company_type,
                    'year': year,
                    'serial': serial,
                    'scan': scan,
                }

    fields = [
        FieldDefinition(
            name='year',
            display_name='Year',
            description='Year of the financial report.',
            results_overview=True,
            visualizations=['resultscount', 'termfrequency'],
            es_mapping={'type': 'integer'},
            search_filter=RangeFilter(
                description='Restrict the years from which search results will be returned.',
                lower=min_date.year,
                upper=max_date.year,
            ),
            visualization_sort="key",
            extractor=Metadata(key='year', transform=int),
            csv_core=True,
            sortable=True
        ),
        FieldDefinition(
            name='company',
            display_name='Company',
            description='Company to which the report belongs.',
            results_overview=True,
            visualizations=['resultscount', 'termfrequency'],
            es_mapping={'type': 'keyword'},
            search_filter=MultipleChoiceFilter(
                description='Search only within these companies.',
                option_count=len(dutchannualreports_map.keys()),
            ),
            extractor=Metadata(
                key='company',
                transform=lambda x: dutchannualreports_map[x],
            ),
            csv_core=True
        ),
        FieldDefinition(
            name='company_type',
            display_name='Company Type',
            description='Financial or non-financial company?',
            es_mapping={'type': 'keyword'},
            search_filter=MultipleChoiceFilter(
                description=(
                    'Accept only financial / non-financial companies'
                ),
                option_count = 2,
            ),
            extractor=Metadata(key='company_type')
        ),
        FieldDefinition(
            name='page',
            display_name='Page Number',
            description='The number of the page in the scan',
            es_mapping={'type': 'integer'},
            extractor=XML(attribute='PHYSICAL_IMG_NR', transform=int),
            csv_core=True,
            sortable=True
        ),
        FieldDefinition(
            name='id',
            display_name='ID',
            es_mapping=keyword_mapping(),
            description='Unique identifier of the page.',
            extractor=Combined(
                Metadata(key='company'),
                Metadata(key='year'),
                XML(attribute='ID'),
                transform=lambda x: '_'.join(x),
            ),
            hidden=True,
        ),
        FieldDefinition(
            name='content',
            es_mapping=main_content_mapping(True, True, True, 'nl'),
            display_name='Content',
            display_type='text_content',
            visualizations=['wordcloud'],
            description='Text content of the page.',
            results_overview=True,
            extractor=XML(
                tag='String',
                attribute='CONTENT',
                recursive=True,
                multiple=True,
                transform=lambda x: ' '.join(x),
            ),
            search_field_core=True,
            language='nl',
        ),
        FieldDefinition(
            name='file_path',
            es_mapping=keyword_mapping(),
            display_name='File path',
            description='Filepath of the source file containing the document,\
            relative to the corpus data directory.',
            extractor=Metadata(key='file_path'),
            hidden=True,
        ),
        FieldDefinition(
            name='image_path',
            mapping=keyword_mapping(),
            display_name="Image path",
            description="Path of the source image corresponding to the document,\
            relative to the corpus data directory.",
            extractor=Metadata(key='image_path'),
            hidden=True,
        )
    ]

    document_context = {
        'context_fields': ['company', 'year'],
        'sort_field': 'page',
        'sort_direction': 'asc',
        'context_display_name': 'report'
    }

    def request_media(self, document, corpus_name):
        image_path = document['fieldValues']['image_path']
        pdf_info = get_pdf_info(op.join(self.data_directory, image_path))
        pages_returned = 5 #number of pages that is displayed. must be odd number.
         #the page corresponding to the document
        home_page = int(document['fieldValues']['page'])
        pages, home_page_index = pdf_pages(pdf_info['all_pages'], pages_returned, home_page)
        pdf_info = {
            "pageNumbers": [p for p in pages], #change from 0-indexed to real page
            "homePageIndex": home_page_index+1, #change from 0-indexed to real page
            "fileName": pdf_info['filename'],
            "fileSize": pdf_info['filesize']
        }
        image_url = media_url(
            corpus_name,
            image_path,
            start_page=pages[0]-1,
            end_page=pages[-1]
        )
        return {'media': [image_url], 'info': pdf_info}


    def get_media(self, request_args):
        '''
        Given the image path and page number of the search result,
        construct a new pdf which contains 2 pages before and after.
        '''
        image_path = request_args['image_path']
        start_page = int(request_args['start_page'])
        end_page = int(request_args['end_page'])
        absolute_path = op.join(self.data_directory, image_path)
        if not op.isfile(absolute_path):
            return None
        input_pdf = retrieve_pdf(absolute_path)
        pages = range(start_page, end_page)
        out = build_partial_pdf(pages, input_pdf)
        return out

