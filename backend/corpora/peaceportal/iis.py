from copy import copy
from os.path import join, split
from ianalyzer_readers.xml_tag import Tag
from typing import Optional
from django.conf import settings

from addcorpus.python_corpora.corpus import XMLCorpusDefinition
from addcorpus.python_corpora.extract import Combined, Constant, ExternalFile, XML
from addcorpus.serializers import LanguageField
from corpora.peaceportal.peaceportal import PeacePortal, categorize_material, clean_newline_characters, \
    clean_commentary, join_commentaries, get_text_in_language, \
    transform_to_date, transform_to_date_range
from corpora.utils.exclude_fields import exclude_fields_without_extractor


class PeaceportalIIS(PeacePortal, XMLCorpusDefinition):
    data_directory = settings.PEACEPORTAL_IIS_DATA
    es_index = getattr(settings, 'PEACEPORTAL_IIS_ES_INDEX', 'peaceportal-iis')

    def add_metadata(self, filename):
        return {
            'associated_file': join(self.external_file_folder, split(filename)[1])
        }

    def __init__(self):
        super().__init__()
        self.external_file_folder = settings.PEACEPORTAL_IIS_TXT_DATA
        self.source_database.extractor = Constant(
            value='Inscriptions of Israel/Palestine (Brown University)'
        )

        self._id.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('msIdentifier'), Tag('idno'),
            flatten=True,
            transform=lambda x: ''.join(x.lower().split())
        )

        self.url.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('msIdentifier'), Tag('idno'),
            flatten=True,
            transform=lambda x: 'https://library.brown.edu/iip/viewinscr/{}'.format(
                ''.join(x.lower().split()))
        )

        # quick and dirty for now: extract value for 'notBefore'
        self.year.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('history'), Tag('origin'), Tag('date'),
            attribute='notBefore',
        )

        self.not_before.extractor = not_before_extractor()

        self.not_after.extractor = not_after_extractor()

        self.date.extractor = Combined(
            not_before_extractor(),
            not_after_extractor(),
            transform=lambda dates: transform_to_date_range(*dates)
        )

        self.transcription.extractor = ExternalFile(
            stream_handler=_extract_transcript
        )

        self.transcription_english.extractor = XML(
            Tag('div', type='translation'), Tag('p', limit=1),
            toplevel=True,
            flatten=True,
            transform=lambda x: ' '.join(x.split()) if x else None
        )

        # is not present in IIS data
        # self.names.extractor = XML(
        #     tag=['teiHeader', 'profileDesc',
        #          'particDesc', 'listPerson', 'person'],
        #     flatten=True,
        #     multiple=True,
        #     toplevel=False,
        # )

        self.iconography.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('physDesc'), Tag('decoDesc'), Tag('decoNote'),
            multiple=True,
            flatten=True,
            transform='\n'.join,
        )

        # is not present in IIS data
        self.sex.extractor = Constant(
            value='Unknown'
        )

        self.country.extractor = Constant(
            value='Israel/Palestine'
        )

        self.region.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('history'), Tag('origin'), Tag('placeName'), Tag('region'),
            flatten=True,
        )

        self.settlement.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('history'), Tag('origin'), Tag('placeName'), Tag('settlement'),
            flatten=True
        )

        self.location_details.extractor = Combined(
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('history'), Tag('origin'), Tag('placeName'),
                flatten=True
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('history'), Tag('origin'), Tag('p'),
                flatten=True
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('history'), Tag('provenance'),
                flatten=True
            )
        )

        self.material.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('physDesc'), Tag('objectDesc'), Tag('supportDesc'),
            attribute='ana',
            flatten=True,
            transform=lambda x: categorize_material(x)
        )

        self.material_details.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('physDesc'), Tag('objectDesc'), Tag('supportDesc'),
            attribute='ana',
            flatten=True
        )

        self.language.extractor = Combined(
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('msContents'), Tag('textLang'),
                attribute='mainLang',
                transform=lambda x: normalize_language(x)
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('msContents'), Tag('textLang'),
                attribute='otherLangs',
                transform=lambda x: normalize_language(x)
            )
        )
        self.language_code.extractor = Combined(
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('msContents'), Tag('textLang'),
                attribute='mainLang',
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('msContents'), Tag('textLang'),
                attribute='otherLangs',
            )
        )

        self.comments.extractor = Combined(
            XML(
                Tag('text'), Tag('div', type='commentary'), Tag('p', limit=1),
                flatten=True,
                transform=lambda x: clean_commentary(x) if x else None
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('physDesc'), Tag('objectDesc'), Tag('supportDesc'), Tag('condition'),
                extract_soup_func=_extract_condition,
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('physDesc'), Tag('objectDesc'), Tag('layoutDesc'), Tag('layout'), Tag('p'),
                toplevel=False,
                transform=lambda x: f'LAYOUT:\n{clean_commentary(x)}\n\n' if x else None
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('physDesc'), Tag('objectDesc'),
                attribute='ana',
                transform=lambda x: f'OBJECTTYPE:\n{x[1:]}\n\n' if x else None
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('physDesc'), Tag('objectDesc'), Tag('supportDesc'), Tag('support'),
                Tag('dimensions'),
                extract_soup_func=_extract_dimensions,
                transform=lambda x: f'DIMENSIONS:\n{x}\n\n' if x else None
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('physDesc'), Tag('objectDesc'), Tag('supportDesc'), Tag('support'),
                Tag('p'),
                flatten=True,
                transform=lambda x: f'SUPPORT:\n{clean_commentary(x)}\n\n' if x else None
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('physDesc'), Tag('handDesc'), Tag('handNote'),
                extract_soup_func=_extract_handnotes
            ),
            transform=lambda x: join_commentaries(x)
        )

        self.bibliography.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('msIdentifier'), Tag('publications'), Tag('publication'),
            multiple=True
        )

        self.transcription_hebrew.extractor = Combined(
            self.transcription.extractor,
            Constant('he'),
            transform=lambda x: get_text_in_language(x)
        )

        self.transcription_latin.extractor = Combined(
            self.transcription.extractor,
            Constant('la'),
            transform=lambda x: get_text_in_language(x)
        )

        self.transcription_greek.extractor = Combined(
            self.transcription.extractor,
            Constant('el'),
            transform=lambda x: get_text_in_language(x)
        )

        self.fields = exclude_fields_without_extractor(self.fields)


def _extract_transcript(filestream):
    text = filestream.read().strip()
    filestream.close()
    # remove the tabs and spaces inherited from xml
    text = clean_newline_characters(text)
    if text:
        text = text.replace('\t', '')
    return text


def _extract_attribute_and_child_p(soup, field_header) -> Optional[str]:
    '''
    Extract value for 'ana' attribute from soup,
    as well as the text from a <p> child. Will be returned
    in as a string
    in the following format `textcontent (attrivubtevalue)`
    '''
    result = ''
    text = ''
    ana = None
    if 'ana' in soup.attrs:
        ana = soup['ana']
    p = soup.find('p')
    if p:
        text = p.get_text()
        if text:
            result = clean_commentary(text)
    if ana:
        result = '{} ({})'.format(result, ana)

    if result:
        cloned_soup = copy(soup)
        cloned_soup.clear()
        return '{}:\n{}\n\n'.format(field_header, result)


def _extract_condition(soup):
    return _extract_attribute_and_child_p(soup, 'CONDITION')


def _extract_handnotes(soup):
    return _extract_attribute_and_child_p(soup, 'HANDNOTES')


def _extract_dimensions(soup) -> str:
    result = ''
    height_elem = soup.find('height')
    if height_elem:
        height = height_elem.get_text()
        if height:
            result = "H: {} ".format(height)

    width_elem = soup.find('width')
    if width_elem:
        width = width_elem.get_text()
        if width:
            result = "{}W: {}".format(result, width)

    depth_elem = soup.find('depth')
    if depth_elem:
        depth = depth_elem.get_text()
        if depth:
            result = "{} D: {}".format(result, depth)

    return result


def normalize_language(text):
    serializer = LanguageField()
    return serializer.to_representation(text)

    # excluded (for now):
    # revision history

    # MISSING (i.e. present in Epidat and Fiji)
    # person(s) - names (profileDesc is completely missing)


def not_after_extractor():
    ''' iis misses the enclosing <origDate> tag '''
    return XML(
        Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
        Tag('history'), Tag('origin'), Tag('date'),
        attribute='notAfter',
        transform=lambda x: transform_to_date(x, 'upper')
    )


def not_before_extractor():
    ''' iis misses the enclosing <origDate> tag '''
    return XML(
        Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
        Tag('history'), Tag('origin'), Tag('date'),
        attribute='notBefore',
        transform=lambda x: transform_to_date(x, 'lower')
    )
