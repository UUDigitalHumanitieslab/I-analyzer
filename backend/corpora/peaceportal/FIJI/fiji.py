import re
import os
import os.path as op
import logging
from ianalyzer_readers.xml_tag import Tag

from django.conf import settings

from addcorpus.python_corpora.corpus import XMLCorpusDefinition
from addcorpus.python_corpora.extract import XML, Constant, Combined
from corpora.peaceportal.peaceportal import PeacePortal, categorize_material, join_commentaries, get_text_in_language
from corpora.utils.exclude_fields import exclude_fields_without_extractor

class PeaceportalFIJI(PeacePortal, XMLCorpusDefinition):
    '''
    This is a fresh version of Ortal-Paz Saar's 'Funerary Inscriptions of Jews from Italy' corpus,
    updated to align with the PEACE portal index. This mostly implies that there are fewer fields
    than in the earlier version (i.e. the one under corpora/jewishinscriptions).
    '''

    data_directory = settings.PEACEPORTAL_FIJI_DATA
    es_index = getattr(settings, 'PEACEPORTAL_FIJI_ES_INDEX', 'peaceportal-fiji')
    filename_pattern = re.compile(r'\d+')

    def sources(self, start, end):
        logger = logging.getLogger(__name__)
        for directory, _, filenames in os.walk(self.data_directory):
            for filename in filenames:
                name, extension = op.splitext(filename)
                full_path = op.join(directory, filename)
                if extension != '.xml':
                    logger.debug(self.non_xml_msg.format(full_path))
                    continue
                match = self.filename_pattern.match(name)
                if not match:
                    logger.warning(self.non_match_msg.format(full_path))
                    continue
                inscriptionID = match.groups()
                yield full_path, {
                    'inscriptionID': inscriptionID
                }

    def __init__(self):
        super().__init__()
        self.source_database.extractor = Constant(
            value='Funerary Inscriptions of Jews from Italy (Utrecht University)'
        )

        self._id.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('titleStmt'), Tag('title'),
        )

        self.url.extractor = Constant(
            value=None
        )

        # the year is commented out: need to have not before / not after fields
        # this is advisable since often we only roughly know the century
        # self.year.extractor = XML(
        #     tag=['teiHeader', 'fileDesc', 'sourceDesc',
        #          'msDesc', 'history', 'origin', 'origDate'],
        #     toplevel=False
        # )

        self.transcription.extractor = XML(
            Tag('text'), Tag('body'), Tag('transcription'),
            flatten=True
        )

        self.names.extractor = XML(
            Tag('teiHeader'), Tag('profileDesc'), Tag('particDesc'), Tag('listPerson'),
            Tag('person'),
            flatten=True,
            multiple=True,
            transform=lambda result: ' '.join(result).strip(),
        )

        self.sex.extractor = XML(
            Tag('teiHeader'), Tag('profileDesc'), Tag('particDesc'), Tag('listPerson'),
            Tag('person'),
            attribute='sex',
            multiple=True,
        )

        self.age.extractor = XML(
            Tag('text'), Tag('body'), Tag('age'),
            transform=lambda age: transform_age_integer(age)
        )

        self.country.extractor = Constant(
            value='Italy'
        )

        self.settlement.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('history'), Tag('origin'), Tag('provenance'),
        )

        self.material.extractor = XML(
            Tag('text'), Tag('body'), Tag('material'),
            transform=lambda x: categorize_material(x)
        )

        self.material_details = XML(
            Tag('text'), Tag('body'), Tag('material'),
        )

        self.language.extractor = XML(
            Tag('teiHeader'), Tag('profileDesc'), Tag('langUsage'), Tag('language'),
            multiple=True,
            transform=lambda x: normalize_language(x)
        )

        self.comments.extractor = Combined(
            XML(
                Tag('text'), Tag('body'), Tag('commentary'),
                transform=str.strip,
            ),
            XML(
                Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
                Tag('history'), Tag('origin'), Tag('remarksOnDate'),
                transform=lambda x: 'DATE:\n{}\n'.format(x) if x else x
            ),
            XML(
                Tag('text'), Tag('body'), Tag('ageComments'),
                transform=lambda x: 'AGE:\n{}\n'.format(x) if x else x
            ),
            XML(
                Tag('text'), Tag('body'), Tag('iconographyDescription'),
                transform=lambda x: 'ICONOGRAPHY:\n{}\n'.format(x) if x else x
            ),
            transform=lambda x: join_commentaries(x)
        )


        self.bibliography.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('msIdentifier'), Tag('publications'), Tag('publication'),
            multiple=True,
        )

        self.location_details.extractor = XML(
            Tag('teiHeader'), Tag('fileDesc'), Tag('sourceDesc'), Tag('msDesc'),
            Tag('msIdentifier'), Tag('location'),
        )

        self.iconography.extractor = XML(
            Tag('text'), Tag('body'), Tag('iconographyType'),
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


def transform_age_integer(age):
    try:
        return int(age)
    except:
        return None


def normalize_language(languages):
    results = []
    for lang in languages:
        if not lang:
            results.append('Unknown')
            continue

        ltext = lang.lower().strip()
        if 'greek' in ltext or 'greeek' in ltext:
            results.append(select_greek(lang))
        if 'latin' in ltext:
            results.append(select_latin(lang))
        if 'hebrew' in ltext:
            results.append(select_hebrew(lang))
        if ltext == 'aramaic' or ltext == 'samaritan':
            return lang
        if '?' in ltext or ltext == 'x' or ltext == 'none':
            results.append('Unknown')
    return results


def select_greek(text):
    text = text.strip()
    if text in [
        "Greek", "Greek (?)", "Greeek",
        "Greek (some Latin characters)",
        "Latin (some Greek characters)",
        "Greek or Latin", "Latin and Greek (?)",
        "Latin in Greek characters"
        "Greek (transliterated Latin?)",
        "Greek with transliterated Latin (?)",
        "Greek with transliterated Latin formula",
    ]:
        return 'Greek'
    if text in [
        "Greek (in Hebrew characters)",
        "Greek in Latin characters (?)",
        "Latin (including transliterated Greek)",
        "transliterated Greek"
    ]:
        return 'Greek (transliterated)'

def select_latin(text):
    text = text.strip()
    if text in [
        "Latin", "Latin (?)",
        "Greek (some Latin characters)",
        "Latin (some Greek characters)",
        "Latin (including transliterated Greek)",
        "Greek or Latin", "Latin and Greek (?)",
        "Latin (transliterated Hebrew)"
    ]:
        return "Latin"

    if text in [
        "Latin in Greek characters",
        "Greek (transliterated Latin?)",
        "Greek with transliterated Latin (?)",
        "Greek with transliterated Latin formula",
    ]:
        return "Latin (transliterated)"


def select_hebrew(text):
    text = text.strip()

    if text in [
        "Hebrew", "Hebrew (?)"
    ]:
        return "Hebrew"

    if text in [
        "Latin (transliterated Hebrew)",
        "Hebrew (transliterated)",
    ]:
        return "Hebrew (transliterated)"




        # TODO: new fields

        # TODO: move to a comments field:



        # excluded (for now):
        # 3D_image
        # inscription_type

        # TODO: discuss
        # fascimile
        # photos_leonard
