import re
from copy import copy
from ianalyzer_readers.xml_tag import Tag, TransformTag
from typing import Iterable, Optional
import bs4

from django.conf import settings

from addcorpus.python_corpora.corpus import XMLCorpusDefinition
from addcorpus.es_mappings import date_mapping
from addcorpus.python_corpora.extract import XML, Constant, Combined, Pass
from corpora.peaceportal.peaceportal import PeacePortal, categorize_material, \
    clean_newline_characters, clean_commentary, join_commentaries, get_text_in_language, \
    not_before_extractor

from corpora.utils.exclude_fields import exclude_fields_without_extractor


class PeaceportalEpidat(PeacePortal, XMLCorpusDefinition):

    data_directory = settings.PEACEPORTAL_EPIDAT_DATA
    es_index = getattr(
        settings, 'PEACEPORTAL_EPIDAT_ES_INDEX', 'peaceportal-epidat')

    languages = ['de', 'he', 'en', 'nl']

    def __init__(self):
        super().__init__()
        self.source_database.extractor = Constant(
            value='Epidat (Steinheim Institute)'
        )

        self._id.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('msIdentifier'), Tag('idno'),
            flatten=True
        )

        self.url.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('publicationStmt'), Tag('idno', type='url'),
            flatten=True,
        )

        self.year.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('history'), Tag('origin'), Tag('origDate'), Tag('date'),
            transform=lambda x: get_year(x),
        )

        self.not_before.extractor = not_before_extractor()

        # the dataset of the Steinheim institute is from the 19th/20th century and has accurate dates
        self.date.es_mapping = date_mapping()
        self.date.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('history'), Tag('origin'), Tag('origDate'), Tag('date'),
        )
        self.transcription.extractor = Pass(
            XML(
                Tag('text'), Tag('body'), Tag('div', type='edition'), Tag('ab'),
                multiple=True,
                flatten=True,
                transform='\n'.join,
            ),
            transform=lambda x: clean_newline_characters(x),
        )

        self.transcription_german.extractor = Pass(
            XML(
                Tag('text'), Tag('body'), Tag('div', type='translation'), Tag('ab'),
                multiple=True,
                flatten=True,
                transform='\n'.join
            ),
            transform=lambda x: clean_newline_characters(x),
        )

        self.names.extractor = XML(
            Tag('teiHeader'), Tag('profileDesc'), Tag('particDesc'),
            Tag('listPerson'), Tag('person'),
            flatten=True,
            multiple=True,
            transform=' '.join,
        )

        self.sex.extractor = XML(
            Tag('teiHeader'), Tag('profileDesc'), Tag('particDesc'),
            Tag('listPerson'), Tag('person'),
            attribute='sex',
            multiple=True,
            transform=lambda x: convert_sex(x)
        )

        self.dates_of_death.extractor = XML(
            Tag('teiHeader'), Tag('profileDesc'), Tag('particDesc'),
            Tag('listPerson'), Tag('death'),
            attribute='when',
            multiple=True,
        )

        self.country.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('history'), Tag('origin'), Tag('origPlace'), Tag('country'),
            TransformTag(_extract_country),
            transform=lambda x: clean_country(x),
            flatten=True,
        )

        self.region.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('history'), Tag('origin'), Tag('origPlace'), Tag('country'),
            Tag('region'),
            flatten=True
        )

        self.settlement.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('history'), Tag('origin'), Tag('origPlace'), Tag('settlement'),
            TransformTag(_extract_settlement),
            flatten=True,
        )

        self.location_details.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('history'), Tag('origin'), Tag('origPlace'), Tag('settlement'),
            Tag('geogName'), TransformTag(_extract_location_details),
            flatten=True,
        )

        self.material.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('physDesc'), Tag('objectDesc'), Tag('supportDesc'), Tag('support'),
            Tag('p'), Tag('material'),
            flatten=True,
            transform=lambda x: categorize_material(x)
        )

        self.material_details.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('physDesc'), Tag('objectDesc'), Tag('supportDesc'), Tag('support'),
            Tag('p'), Tag('material'),
            flatten=True,
        )

        self.language.extractor = XML(
            Tag('teiHeader'), Tag('profileDesc'), Tag('langUsage'), Tag('language'),
            multiple=True,
            transform=lambda x: get_language(x)
        )

        self.comments.extractor = Combined(
            XML(
                Tag('text'), Tag('body'), Tag('div', type='commentary'),
                multiple=True,
                extract_soup_func=_extract_commentary,
                transform=lambda found: "\n".join(found) if len(found) > 1 else None
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('physDesc'), Tag('objectDesc'), Tag('supportDesc'), Tag('condition'),
                flatten=True,
                transform=lambda x: f'CONDITION:\n{x}\n' if x else x
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('physDesc'), Tag('objectDesc'), Tag('supportDesc'), Tag('support'),
                Tag('p'),
                extract_soup_func=_extract_support_comments,
            ),
            transform=lambda x: join_commentaries(x)
        )

        self.images.extractor = XML(
            Tag('facsimile'), Tag('graphic'),
            multiple=True,
            attribute='url',
        )

        self.coordinates.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('history'), Tag('origin'), Tag('origPlace'), Tag('settlement'),
            Tag('geogName'), Tag('geo'),
            flatten=True,
        )

        self.iconography.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('physDesc'), Tag('decoDesc'), Tag('decoNote'),
        )

        self.bibliography.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('msIdentifier'), Tag('publications'), Tag('publication'),
            multiple=True,
            transform=lambda x: x if x else None
        )

        self.transcription_hebrew.extractor = Combined(
            self.transcription.extractor,
            Constant('he'),
            transform=lambda x: get_text_in_language(x)
        )

        self.transcription_english.extractor = Combined(
            self.transcription.extractor,
            Constant('en'),
            transform=lambda x: get_text_in_language(x)
        )

        self.transcription_dutch.extractor = Combined(
            self.transcription.extractor,
            Constant('nl'),
            transform=lambda x: get_text_in_language(x)
        )

        self.fields = exclude_fields_without_extractor(self.fields)


def convert_sex(values):
    if not values:
        return ['Unknown']
    result = []
    for value in values:
        if value == '1':
            result.append('M')
        elif value == '2':
            result.append('F')
        else:
            result.append('Unknown')
    return result


def clean_country(text):
    if not text:
        return 'Unknown'
    if text.lower().strip() == 'tobedone':
        return 'Unknown'
    return text


def get_year(text):
    if not text or text == '--':
        return
    matches = re.search('[1-2]{0,1}[0-9]{3}', text)
    if matches:
        return matches[0]


def get_language(values):
    if not values:
        return ['Unknown']
    if 'German in Hebrew letters' in values:
        return ['German (transliterated)', 'Hebrew']
    return values


def _extract_commentary(commentary: bs4.PageElement) -> Optional[str]:
    '''
    Helper function to extract all commentaries from the <body> tag.
    A single element will be returned with the commentaries found as text content.
    '''
    if commentary['subtype'] in ['Zitate', 'Zeilenkommentar', 'Prosopographie', 'Abkürzung', 'Endkommentar', 'Stilmittel']:
        p = commentary.find('p')
        if p:
            text = p.get_text()
            if text:
                text = clean_commentary(text)
                return '{}:\n{}\n'.format(
                    commentary['subtype'].strip().upper(), text)


def _extract_support_comments(soup: bs4.PageElement) -> str:
    cloned_soup = copy(soup)
    cloned_soup.clear()

    commentaries = _add_support_comment(soup, '', 'dim', 'DIMENSIONS')
    commentaries = _add_support_comment(
        soup, commentaries, 'objectType', 'OBJECTTYPE')

    # add any additional text from the <p> element,
    # i.e. if there is text it is the very last node
    contents = soup.contents
    text = contents[len(contents) - 1].strip()
    if text:
        text = clean_commentary(text)
        commentaries = '{}{}:\n{}\n'.format(commentaries, 'SUPPORT', text)

    return commentaries


def _add_support_comment(soup: bs4.PageElement, existing_commentaries: str, elem_name, commentary_name) -> str:
    elem = soup.find(elem_name)
    if elem:
        text = elem.get_text()
        if text:
            text = clean_commentary(text)
            return '{}{}:\n{}\n\n'.format(existing_commentaries, commentary_name, text)
    return existing_commentaries



def _extract_country(soup) -> Iterable[bs4.PageElement]:
    '''
    Helper function to extract country.
    This is needed because the output of `flatten` would otherwise include the text contents
    of the `<region>`.
    '''
    return _clone_soup_extract_child(soup, 'region')


def _extract_settlement(soup) -> Iterable[bs4.PageElement]:
    return _clone_soup_extract_child(soup, 'geogName')


def _extract_location_details(soup) -> Iterable[bs4.PageElement]:
    return _clone_soup_extract_child(soup, 'geo')


def _clone_soup_extract_child(soup, to_extract) -> Iterable[bs4.PageElement]:
    '''
    Helper function to clone the soup and extract a child element.
    This is useful when the output of `flatten` would otherwise include the text contents
    of the child.
    '''
    cloned_soup = copy(soup)
    child = cloned_soup.find(to_extract)
    if child:
        child.extract()
    return [cloned_soup]

    # TODO: add field

    # TODO: move to a comments field:

    # excluded (for now):
    # title
    # organization (incl details, e.g. address)
    # licence
    # taxonomy (i.e. things like foto1, foto2 -> no working links to actual images)
