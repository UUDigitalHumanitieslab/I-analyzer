from glob import glob
import datetime
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from ianalyzer_readers.xml_tag import Tag

from django.conf import settings

from addcorpus.python_corpora.corpus import ParentCorpusDefinition
from addcorpus.python_corpora.extract import XML
from addcorpus.es_settings import es_settings
from corpora.peaceportal.utils import field_defaults

class PeacePortal(ParentCorpusDefinition):
    '''
    Base class for corpora in the PEACE portal.

    This supplies the frontend with the information it needs.
    Child corpora should only provide extractors for each field.
    Consequently, create indices (with alias 'peaceportal') from
    the corpora specific definitions, and point the application
    to this base corpus.
    '''

    title = "PEACE Portal"
    description = "A collection of inscriptions on Jewish burial sites"
    # store min_year as int, since datetime does not support BCE dates
    min_year = -530
    max_date = datetime.datetime(year=1950, month=12, day=31)
    visualize = []
    es_index = getattr(settings, 'PEACEPORTAL_ALIAS', 'peaceportal')
    es_alias = getattr(settings, 'PEACEPORTAL_ALIAS', 'peaceportal')
    scan_image_type = 'image/png'
    # fields below are required by code but not actually used
    min_date = datetime.datetime(year=746, month=1, day=1)
    category = 'inscription'

    tag_entry = Tag('TEI')

    # overwrite below in child class if you need to extract the (converted) transcription
    # from external files. See README.
    # el stands for modern Greek (1500-)
    languages = ['en', 'de', 'nl', 'he', 'la', 'el']

    @property
    def es_settings(self):
        return es_settings(self.languages, stopword_analysis=True,
                           stemming_analysis=True)

    def sources(self, start, end):
        for filename in sorted(glob('{}/**/*.xml'.format(self.data_directory),
                                    recursive=True)):
            metadata = self.add_metadata(filename)
            yield filename, metadata

    def add_metadata(self, filename):
        return {}

    def request_media(self, document):
        images = document['fieldValues']['images']
        if not images:
            images = []
        return {'media': images}

    def __init__(self):
        self.source_database = field_defaults.source_database()
        self._id = field_defaults.id()
        self.url = field_defaults.url()
        self.year = field_defaults.year(self.min_year, self.max_date.year)
        self.not_before = field_defaults.not_before()
        self.not_after = field_defaults.not_after()
        self.date = field_defaults.date(self.min_date, self.max_date)
        self.transcription = field_defaults.transcription()
        self.transcription_german = field_defaults.transcription_german()
        self.transcription_english = field_defaults.transcription_english()
        self.transcription_hebrew = field_defaults.transcription_hebrew()
        self.transcription_latin = field_defaults.transcription_latin()
        self.transcription_greek = field_defaults.transcription_greek()
        self.transcription_dutch = field_defaults.transcription_dutch()
        self.age = field_defaults.age()
        self.names = field_defaults.names()
        self.sex = field_defaults.sex()
        self.country = field_defaults.country()
        self.settlement = field_defaults.settlement()
        self.region = field_defaults.region()
        self.location_details = field_defaults.location_details()
        self.material = field_defaults.material()
        self.material_details = field_defaults.material_details()
        self.language = field_defaults.language()
        self.language_code = field_defaults.language_code()
        self.bibliography = field_defaults.bibliography()
        self.comments = field_defaults.comments()
        self.images = field_defaults.images()
        self.coordinates = field_defaults.coordinates()
        self.iconography = field_defaults.iconography()
        self.dates_of_death = field_defaults.dates_of_death()

        self.fields = [
            self._id,
            self.url,
            self.year,
            self.not_before,
            self.not_after,
            self.date,
            self.source_database,
            self.transcription,
            self.names,
            self.sex,
            self.dates_of_death,
            self.age,
            self.country,
            self.region,
            self.settlement,
            self.location_details,
            self.language,
            self.language_code,
            self.iconography,
            self.images,
            self.coordinates,
            self.material,
            self.material_details,
            self.bibliography,
            self.comments,
            self.transcription_german,
            self.transcription_hebrew,
            self.transcription_latin,
            self.transcription_greek,
            self.transcription_english,
            self.transcription_dutch
        ]


def clean_newline_characters(text):
    '''
    Remove all spaces surrounding newlines in `text`.
    Also removes multiple newline characters in a row.
    '''
    if not text:
        return
    parts = text.split('\n')
    cleaned = []
    for part in parts:
        if not '\n' in part:
            stripped = part.strip()
            if stripped:
                cleaned.append(part.strip())
    return '\n'.join(cleaned)


def clean_commentary(commentary):
    '''
    Clean a commentary by removing all whitespaces characters between words,
    except for one space.
    '''
    return ' '.join(commentary.split())


def join_commentaries(commentaries) -> str:
    '''
    Helper function to join the result of a Combined extractor
    into one string, separating items by a newline
    '''
    results = filter(None, commentaries)
    return "\n".join(results)


def categorize_material(text):
    '''
    Helper function to (significantly) reduce the material field to a set of categories.
    The Epidat corpus in particular has mainly descriptions of the material.
    Returns a list of categories, i.e. those that appear in `text`.
    '''
    if not text:
        return ['Unknown']

    categories = ['Sandstein', 'Kalkstein', 'Stein', 'Granit', 'Kunststein',
                  'Lavatuff', 'Marmor', 'Kalk', 'Syenit', 'Labrador', 'Basalt', 'Beton',
                  'Glas', 'Rosenquarz', 'Gabbro', 'Diorit', 'Bronze',
                  # below from FIJI and IIS
                  'Limestone', 'Stone', 'Clay', 'Plaster', 'Glass', 'Kurkar', 'Granite',
                  'Marble', 'Metal', 'Bone', 'Lead']
    result = []
    ltext = text.lower()

    for c in categories:
        if c.lower() in ltext:
            result.append(translate_category(c))

    if len(result) == 0:
        # reduce unknown, other and ? to Unknown
        # 'schrifttafel' removes some clutter from Epidat
        if 'unknown' in ltext or 'other' in ltext or '?' in ltext or 'schrifttafel':
            result.append('Unknown')
        else:
            result.append(text)

    return result


def translate_category(category):
    '''
    Helper function to translate non-English categories of material into English
    '''
    pairs = {
        'Sandstein': 'Sandstone',
        'Kalkstein': 'Limestone',
        'Stein': 'Stone',
        'Granit': 'Granite',
        'Kunststein': 'Artificial stone',
        'Lavatuff': 'Tufa',
        'Marmor': 'Marble',
        'Kalk': 'Limestone',
        'Syenit': 'Syenite',
        'Labrador': 'Labradorite',
        'Beton': 'Concrete',
        'Glas': 'Glass',
        'Rosenquarz': 'Rose quartz',
        'Diorit': 'Diorite'
    }

    for original, translation in pairs.items():
        if category == original:
            return translation
    return category


def get_text_in_language(_input):
    '''
    Get all the lines from a transcription that are in a certain language
    (according to the `langdetect` package). Note that `transcription` will
    be split on newlines to create lines that will be fed to langdetect one by one.
    All lines that are in `language_code` will be collected and returned as one string,
    i.e. they will be joined with a space (no newlines!).

    Parameters:
        _input -- A tuple or list with (transcription, language_code). Will typically be the output
        of a Combined extractor, i.e. one for the transcript and a Constant extractor with the language code.
        For a list of language codes detected by langdetect, see https://pypi.org/project/langdetect/
    '''
    results = []
    if len(_input) != 2 or not _input[0]:
        return results
    lines = _input[0].split('\n')
    language_code = _input[1]

    for line in lines:
        if not line:
            continue
        detected_code = None
        try:
            # note that Aramaic is detected as Hebrew
            detected_code = detect(line)
        except LangDetectException:
            # sometimes langdetect isn't happy with some stuff like
            # very short strings with mainly numbers in it
            pass
        if detected_code and detected_code == language_code:
            results.append(line)
    return ' '.join(results)


def transform_to_date(input, margin):
    try:
        datetime.date.fromisoformat(input)
        return input
    except:
        if not input:
            return None
        if int(input) < 1:
            raise Exception(
                'Years smaller than 1 cannot be transformed to dates')
        if len(input) < 4:
            input = zero_pad_year(input)
        if margin == 'upper':
            return '{}-12-31'.format(input)
        elif margin == 'lower':
            return '{}-01-01'.format(input)
        else:
            raise Exception("margin argument must be 'upper' or 'lower'")


def zero_pad_year(input):
    return ('0' * (4 - len(str(input)))) + str(input)


def transform_to_date_range(earliest, latest):
    if not earliest:
        earliest = PeacePortal.min_date
    if not latest:
        latest = PeacePortal.max_date
    return {
        'gte': earliest,
        'lte': latest
    }


def not_after_extractor(transform=True):
    ''' extractor for standard epidat format '''
    return XML(
        Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
        Tag('history'), Tag('origin'), Tag('origDate'), Tag('date'),
        attribute='notAfter',
        transform=lambda x: transform_to_date(x, 'upper') if transform else x
    )


def not_before_extractor(transform=True):
    ''' extractor for standard epidat format '''
    return XML(
        Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
        Tag('history'), Tag('origin'), Tag('origDate'), Tag('date'),
        attribute='notBefore',
        transform=lambda x: transform_to_date(x, 'lower') if transform else x
    )
