import pytest
import os
from bs4 import BeautifulSoup

from addcorpus.python_corpora.load_corpus import load_corpus_definition
from addcorpus.python_corpora.extract import XML
from corpora.dbnl.utils import append_to_tag, index_by_id, which_unique, language_name

here = os.path.abspath(os.path.dirname(__file__))

@pytest.fixture
def dbnl_corpus(settings):
    settings.DBNL_DATA = os.path.join(here, 'data')
    # for testing purposes, also add the metadata helper corpus
    settings.CORPORA = {
        'dbnl': os.path.join(here, '..', 'dbnl.py'),
        'dbnl_metadata': os.path.join(here, '..', 'dbnl_metadata.py'),
    }
    return 'dbnl'

language_name_testcases = [
    ('nl', 'Dutch'),
    ('la', 'Latin'),
    ('lat', 'Latin'),
    ('rus', 'Russian')
]

@pytest.mark.parametrize(['code', 'name'], language_name_testcases)
def test_language_names(code, name):
    assert language_name(code) == name

which_unique_testcases = [
    (['_ale002', '_ale002'], [True, False]),
    (['proza', 'poëzie', 'proza'], [True, True, False])
]

@pytest.mark.parametrize(['items', 'uniquenesses'], which_unique_testcases)
def test_which_unique(items, uniquenesses):
    result = list(which_unique(items))
    assert result == uniquenesses

def test_metadata_extraction(dbnl_corpus):
    corpus = load_corpus_definition('dbnl_metadata')
    data = index_by_id(corpus.documents())
    assert len(data) == 9

    item = data['maer005sing01']
    assert item['title'] == 'Het singende nachtegaeltje'
    assert item['author_name'] == 'Cornelis Maertsz.'

    multiple_authors = data['maer002spie00']
    assert multiple_authors['title'] == 'Spiegel historiael (5 delen)'
    assert multiple_authors['author_name'] == 'Jacob van Maerlant, Philip Utenbroecke, Lodewijk van Velthem'

append_testcases = [
    (
        '<row><cell>Vraeghje wie het meeste goedt.</cell><cell>107</cell></row>',
        'cell',
        ' ',
        'Vraeghje wie het meeste goedt.107',
        'Vraeghje wie het meeste goedt. 107',
    ),
    (
        '<l>Nu lokken schone Prenten<lb/>\nHun beider vrolijke ogen</l>',
        'lb',
        '\n',
        'Nu lokken schone Prenten Hun beider vrolijke ogen',
        'Nu lokken schone Prenten\nHun beider vrolijke ogen',
    ),
]

@pytest.mark.parametrize(['xml', 'tag', 'padding', 'original_output', 'new_output'], append_testcases)
def test_append_to_tag(xml, tag, padding, original_output, new_output):
    soup = BeautifulSoup(xml, 'lxml-xml')
    extractor = XML(flatten=True)
    assert extractor._flatten(soup) == original_output

    edited_soup = append_to_tag(soup, tag, padding)

    assert extractor._flatten(edited_soup) == new_output

expected_docs = [
    {
        'title_id': 'maer005sing01_01',
        'title': 'Het singende nachtegaeltje',
        'id': 'maer005sing01_01_0000',
        'volumes': None,
        'edition': '1ste druk',
        'periodical': None,
        'author_id': 'maer005',
        'author': 'Cornelis Maertsz.',
        'author_year_of_birth': None,
        'author_place_of_birth': 'Wervershoof',
        'author_year_of_death': 'na 1671',
        'author_place_of_death': None,
        'author_gender': 'man/unknown',
        'url': 'https://dbnl.org/tekst/maer005sing01_01',
        'year': '1671',
        'year_full': '1671',
        'genre': 'poëzie',
        'language': 'Dutch',
        'language_code': 'nl',
        'content': '\n'.join([
            'Het singende Nachtegaeltje',
            'Quelende soetelijck, tot stichtelijck vermaeck voor de Christelijck Ieught.',
            'Door.',
            'Cornelis Maertsz. tot Wervers hoof.',
            '\'t Amsterdam Voor Michiel de Groot, Boek-Verkooper op den Nieuwen Dijck, 1671.',
        ]),
        'chapter_title': None,
        'chapter_index': 1,
        'has_content': True,
        'is_primary': True,
    },
    {
        'content': '\n'.join([
            'Op De vermakelijke en stightelijke Liedekens van Cornelis Maarts',
            'SOo wort de schrand\'re Rey der vloeiende Poëten',
            'Door u, o waerde Vriend! vervult,',
            'Soo wort uw\' Naam met Eer vergult,',
            'En door de Lof-bazuin roem rughtigh uitgekreten,',
            'De Dight-kunst scheen wel eer in Amstel silte Plassen',
            'Alleen te sitten op haer throon,',
            'Maar ghy stelt in uw\' Dight ten toon',
            'Dat in ons Wervershoof nogh eed\'ler vrughten wassen.',
            'Want\'t baat niet dat men kan een yd\'le Pen beswang\'ren',
            'Met wonderlijck Gedight,',
            'Indienmen niet en stight,',
            'Maer met een Heydensch rot vervult de Mond der Sang\'ren.',
            'Ghy soeckt de Af-breuk van het Rijck des Helschen lagers.',
            'Dies ghy een Heiligh Ooghwit raakt,',
            'En onse Ieught sticht en vermaakt',
            'Soo volght ghy \'t saligh Spoor des Ioodschen Harpe-Slagers.',
            'Treet voort dien Eerbaan in, en laat geen Aardsch gewemel',
            'V hind\'ren in soo eed\'len Saak,',
            'Soo streckt uw \'Lands-lien tot een Baak',
            'En voert ons dart\'le Ieughd al singende ten Hemel.',
            'H. Vander Meer.',
        ]),
        'chapter_title': 'Op De vermakelijke en stightelijke Liedekens van Cornelis Maarts',
        'chapter_index': 2,
        'is_primary': False,
    }, {
        'chapter_title': 'Register der Liedekens.',
        'content': '\n'.join([
            'Register der Liedekens.',
            'A.',
            'ACh gesalfde van den Heer. Pag. 30',
            'Als Saul, en david den vyant in\'t velt. 41',
            'Als ick de Son verhoogen sie. 184',
            'Als hem de Son begeeft. 189',
            'Als ick den Herfst aenschou. 194',
            'Als in koelt, de nacht komt overkleeden 208',
            'Als van der meer op Eng\'le-vleug\'len vloog. 232',
        ])
    }, { # metadata-only book
        'title_id': 'maer002alex01',
        'title': 'Alexanders geesten',
        'year_full': '13de eeuw',
        'year': '1200',
        'author_id': 'maer002',
        'author': 'Jacob van Maerlant',
        'url': 'https://dbnl.org/tekst/maer002alex01_01',
        'content': None,
        'has_content': False,
        'is_primary': True,
    }, { # book with multiple authors
        'title_id': 'maer002spie00',
        'author_id': 'maer002, uten001, velt003',
        'author': 'Jacob van Maerlant, Philip Utenbroecke, Lodewijk van Velthem',
        'author_year_of_birth': 'ca. 1230, ?(13de eeuw), ca. 1270',
        'author_place_of_birth': None,
    }
] + [{}] * 3 + [
    { # periodical
        'title_id': 'will028belg00',
        'author_id': 'will028',
        'author': 'J.F. Willems',
        'periodical': 'Belgisch Museum',
    }, { #anonymous author
        'author': 'anoniem [Die hystorie vanden grooten Coninck Alexander]'
    }, { # periodical with multiple genres
        'author': None,
        'periodical': 'Gids, De'
    }
]

def test_dbnl_extraction(dbnl_corpus):
    corpus = load_corpus_definition(dbnl_corpus)
    docs = list(corpus.documents())

    assert len(docs) == 3 + 8 # 3 chapters + 7 metadata-only books

    for actual, expected in zip(docs, expected_docs):
        # assert that actual is a superset of expected
        for key in expected:
            if expected[key] != actual[key]:
                print(key)
            assert expected[key] == actual[key]
        assert expected.items() <= actual.items()


