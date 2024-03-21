'''
Collect information from the Guardian-Observer corpus: the articles are contained in
separate xml-files, zipped.
'''

import logging
logger = logging.getLogger(__name__)
import re
from pathlib import Path # needed for Python 3.4, as glob does not support recursive argument
from os.path import join, getsize
from datetime import datetime
from zipfile import ZipFile
from io import BytesIO

from django.conf import settings

from es.es_update import update_document
from addcorpus.python_corpora import extract
from addcorpus.python_corpora import filters
from addcorpus.python_corpora.corpus import XMLCorpusDefinition, FieldDefinition, until, after, string_contains, consolidate_start_end_years
from media.image_processing import sizeof_fmt
from media.media_url import media_url

from addcorpus.es_mappings import keyword_mapping, main_content_mapping
from addcorpus.es_settings import es_settings

PROCESSED = "corpora/guardianobserver/processed.txt"

# Source files ################################################################


class GuardianObserver(XMLCorpusDefinition):
    title = "Guardian-Observer"
    description = "Newspaper archive, 1791-2003"
    description_page = 'guardianobserver.md'
    min_date = datetime(year=1791, month=1, day=1)
    max_date = datetime(year=2003, month=12, day=31)
    data_directory = settings.GO_DATA
    es_index = getattr(settings, 'GO_ES_INDEX', 'guardianobserver')
    image = 'guardianobserver.jpg'
    scan_image_type = getattr(settings, 'GO_SCAN_IMAGE_TYPE', 'application/pdf')
    languages = ['en']
    category = 'periodical'

    @property
    def es_settings(self):
        return es_settings(self.languages[:1], stopword_analysis=True, stemming_analysis=True)

    tag_toplevel = 'Record'

    def sources(self, start=datetime.min, end=datetime.max):
        '''
        Obtain source files for the Guardian-Observer data.

        Specifically, return the data contained in an xml file within a zip archive.
        '''
        with open(PROCESSED, 'r') as f:
            processed = f.read().splitlines()
        for zfile in Path(self.data_directory).glob('**/GO_*.zip'):
            if str(zfile) in processed:
                continue
            xmls = ZipFile(str(zfile)).namelist()
            with ZipFile(str(zfile), mode='r') as zipped:
                for xml in xmls:
                    with zipped.open(xml) as xmlfile:
                        data = xmlfile.read()
                    yield data
            with open(PROCESSED, 'a') as f:
                f.write('{}\n'.format(str(zfile)))

    fields = [
        FieldDefinition(
            name='date',
            display_name='Publication Date',
            description='Publication date, parsed to yyyy-MM-dd format',
            es_mapping={'type': 'date', 'format': 'yyyy-MM-dd'},
            hidden=True,
            visualizations=['resultscount', 'termfrequency'],
            search_filter=filters.DateFilter(
                min_date,
                max_date,
                description=(
                    'Accept only articles with publication date in this range.'
                )
            ),
            extractor=extract.XML(
                tag='NumericPubDate', toplevel=True,
                transform=lambda x: '{y}-{m}-{d}'.format(y=x[:4],m=x[4:6],d=x[6:])
                )
        ),
        FieldDefinition(
            name='date-pub',
            es_mapping=keyword_mapping(),
            display_name='Publication Date',
            csv_core=True,
            results_overview=True,
            description='Publication date as full string, as found in source file',
            extractor=extract.XML(
                tag='AlphaPubDate', toplevel=True
            )
        ),
        FieldDefinition(
            name='id',
            es_mapping=keyword_mapping(),
            display_name='ID',
            description='Article identifier.',
            extractor=extract.XML(tag='RecordID', toplevel=True)
        ),
        FieldDefinition(
            name='pub_id',
            es_mapping=keyword_mapping(),
            display_name='Publication ID',
            description='Publication identifier',
            extractor=extract.XML(tag='PublicationID', toplevel=True, recursive=True)
        ),
        FieldDefinition(
            name='page',
            es_mapping=keyword_mapping(),
            display_name='Page',
            description='Start page label, from source (1, 2, 17A, ...).',
            extractor=extract.XML(tag='StartPage', toplevel=True)
        ),
        FieldDefinition(
            name='title',
            display_name='Title',
            search_field_core=True,
            visualizations=['wordcloud'],
            description='Article title.',
            extractor=extract.XML(tag='RecordTitle', toplevel=True)
        ),
        FieldDefinition(
            name='source-paper',
            es_mapping=keyword_mapping(True),
            display_name='Source paper',
            description='Credited as source.',
            extractor=extract.XML(tag='Title', toplevel=True, recursive=True),
            search_filter=filters.MultipleChoiceFilter(
                description='Accept only articles from these source papers.',
                option_count=5
            ),
        ),
        FieldDefinition(
            name='place',
            mapping=keyword_mapping(True),
            display_name='Place',
            description='Place in which the article was published',
            extractor=extract.XML(tag='Qualifier', toplevel=True, recursive=True)
        ),
        FieldDefinition(
            name='author',
            mapping=keyword_mapping(True),
            display_name='Author',
            description='Article author',
            extractor=extract.XML(tag='PersonName', toplevel=True, recursive=True)
        ),
        FieldDefinition(
            name='category',
            visualizations=['resultscount', 'termfrequency'],
            display_name='Category',
            description='Article subject categories.',
            es_mapping={'type': 'keyword'},
            search_filter=filters.MultipleChoiceFilter(
                description='Accept only articles in these categories.',
                option_count=19
            ),
            extractor=extract.XML(tag='ObjectType', toplevel=True),
            csv_core=True
        ),
        FieldDefinition(
            name='content',
            es_mapping=main_content_mapping(True, True, True, 'en'),
            display_name='Content',
            display_type='text_content',
            visualizations=['wordcloud'],
            description='Raw OCR\'ed text (content).',
            results_overview=True,
            search_field_core=True,
            extractor=extract.XML(tag='FullText', toplevel=True, flatten=True),
            language='en',
        )
    ]

    document_context = {
        'context_fields': ['pub_id'],
        'sort_field': 'page',
        'sort_direction': 'asc',
        'context_display_name': 'publication'
    }

    def request_media(self, document, corpus_name):
        field_vals = document['fieldValues']
        target_filename = "{}_{}_{}.pdf".format(
            field_vals['pub_id'],
            re.sub('-', '', field_vals['date']),
            field_vals['id']
        )
        image_path = None
        if 'image_path' in field_vals.keys():
            # we stored which of the zip archives holds the target file
            # applicable for post-1910 data
            image_path = field_vals['image_path']
            # define subdirectory in the zip archive
            filename = join(field_vals['image_path'].split('/')[2][:-10], target_filename)
        elif field_vals['date']<'1909-31-12':
            path = join('1791-1909', 'PDF', field_vals['pub_id'])
            zipname = "{}_{}.zip".format(*field_vals['date'].split("-")[:2])
            image_path = join(path, zipname)
            # pre-1910, the zip archives contain folders year -> month -> pdfs
            filename = join(zipname[:4], zipname[5:7], target_filename)
        else:
            path = join('1910-2003', 'PDF')
            global_path = join(self.data_directory, path)
            zipname_pattern = "{}_*_{}.zip".format(
                field_vals['date'][:4],
                field_vals['pub_id']
            )
            zipnames = Path(global_path).glob(zipname_pattern)
            for zipfile in zipnames:
                pdfs = ZipFile(str(zipfile)).namelist()
                correct_file = next((pdf for pdf in pdfs if pdf.split("/")[1]==target_filename), None)
                if correct_file:
                    image_path = join(path, zipfile.name)
                    update_body = {
                        "doc": {
                            "image_path": image_path
                        }
                    }
                    update_document(self.es_index, document, update_body)
                    # define subdirectory in the zip archive
                    filename = join(correct_file.split('/')[0], target_filename)
                    break
        if not image_path:
            return []
        image_urls = [media_url(
            corpus_name,
            image_path,
            filename=filename,
        )]
        pdf_info = {
            "pageNumbers": [1], #change from 0-indexed to real page
            "homePageIndex": 1, #change from 0-indexed to real page
            "fileName": filename,
            "fileSize": sizeof_fmt(getsize(join(self.data_directory, image_path)))
        }
        return {'media': image_urls, 'info': pdf_info}


    def get_media(self, request_args):
        '''
        Given the image path of the zipfile,
        and the filename of the pdf within the zipfile,
        retrieve the pdf.
        '''
        image_path = request_args['image_path']
        filename = request_args['filename']

        pdf_data = None
        with ZipFile(join(self.data_directory, image_path), mode='r') as zipped:
            zip_info = zipped.getinfo(filename)
            pdf_data = zipped.read(zip_info)
        if pdf_data:
            return BytesIO(pdf_data)
        else:
            return None
