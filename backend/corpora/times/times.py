'''
Collect corpus-specific information, that is, data structures and file
locations.

Until 1985, the XML structure of Times-data is described by `LTO_issue.dtd`.
After 1985, it is described by `GALENP.dtd`.
'''

import logging
import os
import os.path
from datetime import datetime, timedelta

from addcorpus.python_corpora import extract
from addcorpus.python_corpora.corpus import (FieldDefinition, XMLCorpusDefinition, after,
                              consolidate_start_end_years, string_contains,
                              until)
from addcorpus.es_mappings import keyword_mapping, main_content_mapping
from addcorpus.es_settings import es_settings
from addcorpus.python_corpora import filters
from corpora.times.times_scans import compose_absolute_image_path
from django.conf import settings
from media.media_url import media_url

logger = logging.getLogger(__name__)


class Times(XMLCorpusDefinition):
    title = "Times"
    description = "Newspaper archive, 1785-2010"
    min_date = datetime(year=1785, month=1, day=1)
    max_date = datetime(year=2010, month=12, day=31)
    data_directory = settings.TIMES_DATA
    es_index = getattr(settings, 'TIMES_ES_INDEX', 'times')
    image = 'times.jpg'
    scan_image_type = getattr(settings, 'TIMES_SCAN_IMAGE_TYPE', 'image/png')
    description_page = 'times.md'
    languages = ['en']
    category = 'periodical'

    @property
    def es_settings(self):
        return es_settings(self.languages[:1], stopword_analysis=True, stemming_analysis=True)

    tag_toplevel = 'issue'
    tag_entry = 'article'

    def sources(self, start=datetime.min, end=datetime.max):
        '''
        Obtain source files for the Times data, relevant to the given timespan.

        Specifically, returns an iterator of tuples that each contain a string
        filename and a dictionary of metadata (in this case, the date).
        '''
        consolidate_start_end_years(start, end, self.min_date, self.max_date)
        date = start
        delta = timedelta(days=1)
        while date <= end:

            # Construct the tag to the correct directory
            xmldir = os.path.join(*[
                self.data_directory,
                'TDA_GDA'
            ] + (
                ['TDA_2010']
                if date.year == 2010 else
                ['TDA_GDA_1785-2009', date.strftime('%Y')]
            ))

            # Skip this year if its directory doesn't exist
            if not os.path.isdir(xmldir):
                logger.warning('Directory {} does not exist'.format(xmldir))
                date = datetime(year=date.year + 1, month=1, day=1)
                continue

            # Construct the full tag
            xmlfile = os.path.join(
                xmldir,
                date.strftime('%Y%m%d'),
                date.strftime('0FFO-%Y-%m%d.xml')
                if date.year > 1985 else
                date.strftime('0FFO-%Y-%b%d').upper() + '.xml'
            )

            # Yield file and metadata if the desired file is present
            if os.path.isfile(xmlfile):
                yield (xmlfile, {'date': date})
            else:
                logger.warning('XML file {} does not exist'.format(xmlfile))

            date += delta

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
            extractor=extract.Metadata('date',
                                       transform=lambda x: x.strftime(
                                           '%Y-%m-%d')
                                       )
        ),
        FieldDefinition(
            name='source',
            display_name='Source',
            description='Library where the microfilm is sourced',
            es_mapping=keyword_mapping(),
            extractor=extract.XML(
                tag=['metadatainfo', 'sourceLibrary'], toplevel=True,
                applicable=after(1985)
            )
        ),
        FieldDefinition(
            name='edition',
            display_name='Edition',
            es_mapping=keyword_mapping(),
            extractor=extract.Choice(
                extract.XML(
                    tag='ed', toplevel=True,
                    applicable=until(1985)
                ),
                extract.XML(
                    tag='ed', toplevel=True, multiple=True,
                    applicable=after(1985)
                )
            ),
            csv_core=True
        ),
        FieldDefinition(
            name='issue',
            display_name='Issue number',
            es_mapping={'type': 'integer'},
            description='Source issue number.',
            extractor=extract.XML(
                tag='is', toplevel=True,
                # Hardcoded to ignore one particular issue with source data
                transform=lambda x: (62226 if x == "6222662226" else int(x))
            ),
            sortable=True,
            csv_core=True
        ),
        FieldDefinition(
            name='volume',
            display_name='Volume',
            description='Volume number.',
            es_mapping=keyword_mapping(),
            extractor=extract.XML(
                tag='volNum', toplevel=True,
                applicable=after(1985)
            ),
            csv_core=True
        ),
        FieldDefinition(
            name='date-pub',
            display_name='Publication Date',
            es_mapping=keyword_mapping(),
            csv_core=True,
            results_overview=True,
            sortable=True,
            description='Publication date as full string, as found in source file',
            extractor=extract.XML(
                tag='da', toplevel=True
            )
        ),
        FieldDefinition(
            name='ocr',
            display_name='OCR confidence',
            description='OCR confidence level.',
            es_mapping={'type': 'float'},
            search_filter=filters.RangeFilter(0, 100,
                                              description=(
                                                  'Accept only articles for which the Opitical Character Recognition confidence '
                                                  'indicator is in this range.'
                                              )
                                              ),
            extractor=extract.XML(tag='ocr', transform=float),
            sortable=True
        ),
        FieldDefinition(
            name='date-end',
            display_name='Ending date',
            es_mapping=keyword_mapping(),
            description=(
                'Ending date of publication. '
                'For issues that span more than 1 day.'
            ),
            extractor=extract.XML(
                tag='tdate', toplevel=True,
                applicable=after(1985)
            )
        ),
        FieldDefinition(
            name='page-count',
            display_name='Image count',
            description='Page count: number of images present in the issue.',
            es_mapping={'type': 'integer'},
            extractor=extract.XML(
                tag='ip', toplevel=True, transform=int
            ),
            sortable=True
        ),
        FieldDefinition(
            name='page-type',
            display_name='Page type',
            description='Supplement in which article occurs.',
            es_mapping={'type': 'keyword'},
            search_filter=filters.MultipleChoiceFilter(
                description=(
                    'Accept only articles that occur in the relevant '
                    'supplement. Only after 1985.'
                ),
                option_count=2
            ),
            extractor=extract.XML(
                tag=['..', 'pageid'], attribute='isPartOf',
                applicable=after(1985)
            )
        ),
        FieldDefinition(
            name='supplement-title',
            display_name='Supplement title',
            description='Supplement title.',
            extractor=extract.XML(
                tag=['..', 'pageid', 'supptitle'], multiple=True,
                applicable=after(1985)
            ),
        ),
        FieldDefinition(
            name='supplement-subtitle',
            display_name='Supplement subtitle',
            description='Supplement subtitle.',
            extractor=extract.XML(
                tag=['..', 'pageid', 'suppsubtitle'], multiple=True,
                applicable=after(1985)
            )
        ),
        # There are no datapoints where this is True, hence the outcomment
        # FieldDefinition(
        #     name='cover',
        #     display_name='On front page',
        #     description='Whether the article is on the front page.',
        #     es_mapping={'type': 'boolean'},
        #     search_filter=filters.BooleanFilter(
        #         true='Front page',
        #         false='Other',
        #         description=(
        #             'Accept only articles that are on the front page. '
        #             'From 1985.'
        #         )
        #     ),
        #     extractor=extract.XML(
        #         tag=['..', 'pageid'], attribute='pageType',
        #         transform=string_contains("body"),
        #         applicable=after(1985)
        #     )
        # ),
        FieldDefinition(
            name='id',
            display_name='ID',
            description='Article identifier.',
            es_mapping=keyword_mapping(),
            extractor=extract.XML(tag='id')
        ),
        FieldDefinition(
            name='ocr-relevant',
            display_name='OCR relevant',
            description='Whether OCR confidence level is relevant.',
            es_mapping={'type': 'boolean'},
            extractor=extract.XML(
                tag='ocr', attribute='relevant',
                transform=string_contains("yes"),
            )
        ),
        FieldDefinition(
            name='column',
            display_name='Column',
            description=(
                'Starting column: a string to label the column'
                'where article starts.'
            ),
            es_mapping=keyword_mapping(),
            extractor=extract.XML(tag='sc')
        ),
        FieldDefinition(
            name='page',
            display_name='Page',
            description='Start page label, from source (1, 2, 17A, ...).',
            es_mapping=keyword_mapping(),
            extractor=extract.Choice(
                extract.XML(tag='pa', applicable=until(1985)),
                extract.XML(tag=['..', 'pa'], applicable=after(1985))
            )
        ),
        FieldDefinition(
            name='pages',
            display_name='Page count',
            es_mapping={'type': 'integer'},
            description=(
                'Page count: total number of pages containing sections '
                'of the article.'
            ),
            extractor=extract.XML(
                tag='pc', transform=int
            ),
            sortable=True
        ),
        FieldDefinition(
            name='title',
            display_name='Title',
            results_overview=True,
            search_field_core=True,
            visualizations=['wordcloud'],
            description='Article title.',
            extractor=extract.XML(tag='ti')
        ),
        FieldDefinition(
            name='subtitle',
            display_name='Subtitle',
            description='Article subtitle.',
            extractor=extract.XML(tag='ta', multiple=True),
            search_field_core=True
        ),
        FieldDefinition(
            name='subheader',
            display_name='Subheader',
            description='Article subheader (product dependent field).',
            extractor=extract.XML(
                tag='subheader', multiple=True,
                applicable=after(1985)
            )
        ),
        FieldDefinition(
            name='author',
            display_name='Author',
            description='Article author.',
            es_mapping=keyword_mapping(True),
            extractor=extract.Choice(
                extract.XML(
                    tag='au', multiple=True,
                    applicable=until(1985)
                ),
                extract.XML(
                    tag='au_composed', multiple=True,
                    applicable=after(1985)
                )
            ),
            search_field_core=True,
            csv_core=True
        ),
        FieldDefinition(
            name='source-paper',
            display_name='Source paper',
            description='Credited as source.',
            es_mapping=keyword_mapping(True),
            extractor=extract.XML(
                tag='altSource', multiple=True
            )
        ),
        FieldDefinition(
            name='category',
            visualizations=['resultscount', 'termfrequency'],
            display_name='Category',
            description='Article subject categories.',
            es_mapping={'type': 'keyword'},
            search_filter=filters.MultipleChoiceFilter(
                description='Accept only articles in these categories.',
                option_count=25
            ),
            extractor=extract.XML(tag='ct', multiple=True),
            csv_core=True
        ),
        FieldDefinition(
            name='illustration',
            display_name='Illustration',
            description=(
                'Tables and other illustrations associated with the article.'
            ),
            es_mapping={'type': 'keyword'},
            visualizations=['resultscount', 'termfrequency'],
            search_filter=filters.MultipleChoiceFilter(
                description=(
                    'Accept only articles associated with these types '
                    'of illustrations.'),
                option_count=7
            ),
            extractor=extract.Choice(
                extract.XML(
                    tag='il', multiple=True,
                    applicable=until(1985)
                ),
                extract.XML(
                    tag='il', attribute='type', multiple=True,
                    applicable=after(1985)
                )
            ),
            csv_core=True
        ),
        FieldDefinition(
            name='content-preamble',
            display_name='Content preamble',
            description='Raw OCR\'ed text (preamble).',
            extractor=extract.XML(
                tag=['text', 'text.preamble'],
                flatten=True
            )
        ),
        FieldDefinition(
            name='content-heading',
            display_name='Content heading',
            description='Raw OCR\'ed text (header).',
            extractor=extract.XML(
                tag=['text', 'text.title'],
                flatten=True
            )
        ),
        FieldDefinition(
            name='content',
            display_name='Content',
            display_type='text_content',
            es_mapping=main_content_mapping(True, True, True, 'en'),
            visualizations=['wordcloud'],
            description='Raw OCR\'ed text (content).',
            results_overview=True,
            search_field_core=True,
            extractor=extract.XML(
                tag=['text', 'text.cr'], multiple=True,
                flatten=True
            ),
            language='en',
        ),
    ]

    document_context = {
        'context_fields': ['issue'],
        'sort_field': 'page',
        'sort_direction': 'asc',
        'context_display_name': 'issue'
    }

    def request_media(self, document, corpus_name):
        field_values = document['fieldValues']
        id = document.get('id')
        date = field_values.get('date')

        full_path = compose_absolute_image_path(
            self.data_directory, date, id)
        image_urls = [media_url(corpus_name, full_path)]
        return {'media': image_urls}
