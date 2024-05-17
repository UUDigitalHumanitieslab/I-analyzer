import os
import pytest

from addcorpus.python_corpora.load_corpus import load_corpus_definition
from addcorpus.python_corpora.save_corpus import load_and_save_all_corpora
from addcorpus.models import Corpus

from corpora.peaceportal.peaceportal import transform_to_date_range, zero_pad_year

CORPUS_TEST_DATA = [
    {
        'name': 'peaceportal-epidat',
        'docs': [{
            "id": "blr-4",
            "url": "http://www.steinheim-institut.de:80/cgi-bin/epidat?id=blr-4",
            "year": "1865",
            "not_before": "1865-02-28",
            "date": '1865-02-28',
            "source_database": "Epidat (Steinheim Institute)",
            "transcription": """Hier ruhet
der Kaufmann
Nathan Schönfeld
geb. d. 4. April 1812
gest. d. [28.] Februar 1865
‎‏פ״נ‏‎
‎‏איש חמדות יקר רוח אוהב‏‎
‎‏צדק ופועל טוב כ״ה נתן‏‎
‎‏שאנפעלד נולד ח׳ של פסח‏‎
‎‏תקע״ב ונפטר בשם טוב יום ג׳‏‎
‎‏ב׳ אדר תרכ״ה לפ״ק‏‎
‎‏תנצב״ה‏‎""",
            "names": "Natan Schönfeld (Nathan Schönfeld)",
            "sex": [
                "M"
            ],
            "dates_of_death": [
                "1865-02-28"
            ],
            "country": "Germany",
            "region": "Thuringa",
            "settlement": "Bleicherode",
            "location_details": "Jewish Cemetery",
            "language": [
                "Hebrew",
                "German"
            ],
            "iconography": None,
            "images": [
                "http://steinheim-institut.de/daten/picsblr/xl/0004_blr_2012.jpg",
                "http://steinheim-institut.de/daten/picsblr/xl/0004rblr_2012.jpg",
                "http://steinheim-institut.de/daten/picsblr/xl/0004dblr_2012.jpg"
            ],
            "coordinates": "51.434387 10.571183",
            "material": [
                "Stone"
            ],
            "material_details": "stone",
            "bibliography": None,
            "comments": """OBJECTTYPE:
sepulchral monument

""",
            "transcription_de": None,
            "transcription_he": "‎‏פ״נ‏‎ ‎‏איש חמדות יקר רוח אוהב‏‎ ‎‏צדק ופועל טוב כ״ה נתן‏‎ ‎‏שאנפעלד נולד ח׳ של פסח‏‎ ‎‏תקע״ב ונפטר בשם טוב יום ג׳‏‎ ‎‏ב׳ אדר תרכ״ה לפ״ק‏‎ ‎‏תנצב״ה‏‎",
            "transcription_en": "",
            "transcription_nl": "Hier ruhet"
        }],
        'n_documents': 2
    },
    {
        'name': 'peaceportal-iis',
        'docs': [{
            "id": "akld0002",
            "url": "https://library.brown.edu/iip/viewinscr/akld0002",
            "year": "0001",
            "not_before": "0001-01-01",
            "not_after": "0100-12-31",
            "date": transform_to_date_range('0001-01-01', '0100-12-31'),
            "source_database": "Inscriptions of Israel/Palestine (Brown University)",
            "transcription": """Χάρητος
Χάρητος
Χάρητος
Χάρητος""",
            "sex": "Unknown",
            "country": "Israel/Palestine",
            "region": "Judaea",
            "settlement": "Jerusalem",
            "location_details": (
                "Judaea Jerusalem Akeldama Cave 2 chamber B",
                "",
                ""
            ),
            "language": (
                "Ancient Greek",
                "Unknown"
            ),
            "iconography": "Painted Red",
            "material": [
                "Limestone",
                "Stone"
            ],
            "material_details": "#limestone",
            "bibliography": [
                "Shadmi, T. (1996). The Ossuaries and the Sarcophagus. In G. Avni & Z. Greenhut (Eds.), The Akeldama Tombs: Three Burial Caves in the Kidron Valley, Jerusalem (pp. 41–55). Jerusalem: Israel Antiquities Authority. (page 52)",
                "Ilan, T. (1996). The Ossuary and Sarcophagus Inscriptions. In G. Avni & Z. Greenhut (Eds.), The Akeldama Tombs: Three Burial Caves in the Kidron Valley, Jerusalem (pp. 57–72). Jerusalem: Israel Antiquities Authority. (page 58)"
            ],
            "comments": """CONDITION:
 (#complete.intact)


LAYOUT:
once on each side


OBJECTTYPE:
ossuary


DIMENSIONS:
H: 64 W: 29 D: 35


HANDNOTES:
 (#impressed.inscribed)

""",
            "transcription_he": "",
            "transcription_la": "",
            "transcription_el": "Χάρητος Χάρητος Χάρητος Χάρητος",
            "transcription_en": "of Chares"
        }],
        'n_documents': 3
    },
    {
        'name': 'peaceportal-fiji',
        'docs': [{
            "id": "299",
            "source_database": "Funerary Inscriptions of Jews from Italy (Utrecht University)",
            "transcription": "Φη<λ>ικίσσιμα Ἠμαράντῳ ἐποίησεν.",
            "names": "Felicissima ( the commemorator) Emarantus ( the decaesed) (Φη<λ>ικίσσιμα Ἠμαράντῳ)",
            "sex": [
                "M",
                "F"
            ],
            "age": None,
            "country": "Italy",
            "settlement": "Rome, Monteverde",
            "location_details": "Museo Vaticano, lapidario ebraico ex-Lateranense; inv.no.30762",
            "language": [
                "Greek"
            ],
            "iconography": "none",
            "material": [
                "Stone",
                "Marble"
            ],
            "bibliography": [
                "Noy 1995, p. 69-70 (83)"
            ],
            "comments": """Found on the 3rd of December 1904 in Cub.XL. The lower third of the plaque was left unused. There are poits between the syllables. Ferrua thought it might be pagan.
DATE:
Uncertain

AGE:
not mentioned
""",
            "transcription_he": "",
            "transcription_la": "",
            "transcription_el": "Φη<λ>ικίσσιμα Ἠμαράντῳ ἐποίησεν."
        }],
        'n_documents': 3
    },
    {
        'name': 'peaceportal-tol',
        'docs': [{
            "id": "tol-11",
            "url": "http://www.steinheim-institut.de:80/cgi-bin/epidat?id=tol-11",
            "year": None,
            "not_before": None,
            "not_after": None,
            "source_database": "Medieval funerary inscriptions from Toledo",
            "transcription": """‎‏מִקְנֶה הַשַׂ#[05בּצּ]דֶה וְהַמְּעָרָה אֲשֶׁר בּוֹ לְאֲחֻזַת קֶבֶר‏‎
‎‏לָאִישׁ מְצָאהוּ שׁוֹד וָשֶׁבֶר‏‎
‎‏עַל מוֹת לַבֵּן בָּחוּר וָטוֹב‏‎
‎‏כְּגַן רָטוֹב‏‎
‎‏קָם עָלָיו כַּזְּדוֹנִים‏‎
‎‏גּוֹי עַז פָּנִים‏‎
‎‏הִשְׁקֵהוּ מֵי רוֹשׁ‏‎
‎‏בָּא עַד הָרֹאשׁ‏‎
‎‏וַיַּכֵּהוּ בִצְדִיָּה‏‎
‎‏מַכָּה טְרִיָּה‏‎
‎‏לָאָרֶץ חַיְתוֹ דִכָּה‏‎
‎‏וַיִּצֶק דַּם הַמַּכָּה‏‎
‎‏נַתַּנְהוּ בְדַמּוֹ מִתְגָּאֵל‏‎
‎‏נַעַר יִשְׂרָאֵל‏‎
‎‏הוּא ר׳ יִשְׂרָאֵל בר׳ מֹשֶה‏‎
‎‏בֶּן יִשְׂרָאֵל, דַמּוֹ יְחַשֵּׁב כְּדַם קָרְבָּן אִשֶׁ#[05בּצּ]ה‏‎
‎‏הַצְּבִי יִשְׂרָאֵל חָלָל‏‎
‎‏בִּשְׁנַת עַל בָּמוֹתֶיךָ חֻלָל‏‎
‎‏אֹי נִיסָן [נֵס לָקַחְהוּ חֲבָל ?]‏‎
‎‏וְרֹאשׁ לֹא נִשָּׂא מִיּוֹם נְפַלוֹ‏‎
‎‏עַד בָּא הַמַּשְׁחִית אֶל בֵּיתוֹ‏‎
‎‏בְּפֶסַח וַיָּמֶת אוֹתוֹ‏‎
‎‏תְּהִי מִיתָתוֹ כַפָּרָה לְנִשְׁמָתוֹ‏‎
‎‏וַיֵּאָסֵף אֶל עַמּוֹ‏‎
‎‏תִּהְיֶה נַפְשׁוֹ בְסוֹד נְקִיִּים‏‎
‎‏צְרוּרָה בִּצְרוֹר הַחַיִּים‏‎
‎‏יִפְרוֹשׁ כְּנָפָיו עָלָיו הָאֵל‏‎
‎‏אֱלֹהֵי יִשְׂרָאֵל‏‎""",
            "names": None,
            "sex": [
                "Unknown"
            ],
            "dates_of_death": None,
            "country": "Spain",
            "region": None,
            "settlement": "Toledo",
            "location_details": "Jewish Cemetery",
            "language": [
                "Hebrew"
            ],
            "iconography": None,
            "images": None,
            "coordinates": "39.871036 -4.022968",
            "material": [
                "Stone"
            ],
            "material_details": "stone (material not specified)",
            "bibliography": None,
            "comments": """OBJECTTYPE:
sepulchral monument

""",
            "transcription_he": "‎‏מִקְנֶה הַשַׂ#[05בּצּ]דֶה וְהַמְּעָרָה אֲשֶׁר בּוֹ לְאֲחֻזַת קֶבֶר‏‎ ‎‏לָאִישׁ מְצָאהוּ שׁוֹד וָשֶׁבֶר‏‎ ‎‏עַל מוֹת לַבֵּן בָּחוּר וָטוֹב‏‎ ‎‏כְּגַן רָטוֹב‏‎ ‎‏קָם עָלָיו כַּזְּדוֹנִים‏‎ ‎‏גּוֹי עַז פָּנִים‏‎ ‎‏הִשְׁקֵהוּ מֵי רוֹשׁ‏‎ ‎‏בָּא עַד הָרֹאשׁ‏‎ ‎‏וַיַּכֵּהוּ בִצְדִיָּה‏‎ ‎‏מַכָּה טְרִיָּה‏‎ ‎‏לָאָרֶץ חַיְתוֹ דִכָּה‏‎ ‎‏וַיִּצֶק דַּם הַמַּכָּה‏‎ ‎‏נַתַּנְהוּ בְדַמּוֹ מִתְגָּאֵל‏‎ ‎‏נַעַר יִשְׂרָאֵל‏‎ ‎‏הוּא ר׳ יִשְׂרָאֵל בר׳ מֹשֶה‏‎ ‎‏בֶּן יִשְׂרָאֵל, דַמּוֹ יְחַשֵּׁב כְּדַם קָרְבָּן אִשֶׁ#[05בּצּ]ה‏‎ ‎‏הַצְּבִי יִשְׂרָאֵל חָלָל‏‎ ‎‏בִּשְׁנַת עַל בָּמוֹתֶיךָ חֻלָל‏‎ ‎‏אֹי נִיסָן [נֵס לָקַחְהוּ חֲבָל ?]‏‎ ‎‏וְרֹאשׁ לֹא נִשָּׂא מִיּוֹם נְפַלוֹ‏‎ ‎‏עַד בָּא הַמַּשְׁחִית אֶל בֵּיתוֹ‏‎ ‎‏בְּפֶסַח וַיָּמֶת אוֹתוֹ‏‎ ‎‏תְּהִי מִיתָתוֹ כַפָּרָה לְנִשְׁמָתוֹ‏‎ ‎‏וַיֵּאָסֵף אֶל עַמּוֹ‏‎ ‎‏תִּהְיֶה נַפְשׁוֹ בְסוֹד נְקִיִּים‏‎ ‎‏צְרוּרָה בִּצְרוֹר הַחַיִּים‏‎ ‎‏יִפְרוֹשׁ כְּנָפָיו עָלָיו הָאֵל‏‎ ‎‏אֱלֹהֵי יִשְׂרָאֵל‏‎",
            "transcription_en": "",
            "transcription_nl": ""
        }],
        'n_documents': 3
    }
]


def corpus_test_name(corpus_spec):
    return corpus_spec['name']


@pytest.mark.xfail()
@pytest.mark.parametrize("corpus_object", CORPUS_TEST_DATA, ids=corpus_test_name)
def test_peace_imports(peace_test_settings, corpus_object):
    parent_corpus = load_corpus_definition('peaceportal')
    corpus = load_corpus_definition(corpus_object.get('name'))
    assert len(os.listdir(os.path.abspath(corpus.data_directory))) != 0
    fully_specified = ['peaceportal-iis', 'peaceportal-tol']
    if corpus_object.get('name') not in fully_specified:
        # only IIS / TOL have all fields
        assert len(corpus.fields) != len(parent_corpus.fields)

    start = corpus_object['start'] if 'start' in corpus_object else corpus.min_date
    end = corpus_object['end'] if 'end' in corpus_object else corpus.max_date

    tested_fields = set()
    resulted_fields = set()

    docs = get_documents(corpus, start, end)
    sorted_docs = (doc for doc in sorted(docs, key=lambda doc: doc['id']))

    for target in corpus_object.get('docs'):
        doc = next(sorted_docs)
        for key in target:
            tested_fields.add(key)
            assert key in doc
            if doc[key] != target[key]:
                compare = doc[key], target[key]
                print(key)
            assert doc[key] == target[key]

        for key in doc:
            resulted_fields.add(key)

    docs = get_documents(corpus, start, end)
    assert len(list(docs)) == corpus_object.get('n_documents')


def get_documents(corpus, start, end):
    sources = corpus.sources(
        start=start,
        end=end
    )
    return corpus.documents(sources)

def test_peaceportal_validation(db, peace_test_settings):
    load_and_save_all_corpora()
    corpus_names = [case['name'] for case in CORPUS_TEST_DATA]
    for corpus_name in corpus_names:
        corpus = Corpus.objects.get(name=corpus_name)
        assert corpus.ready_to_publish()


def test_zero_pad_year():
    assert zero_pad_year(2014) == '2014'
    assert zero_pad_year(898) == '0898'
    assert zero_pad_year(65) == '0065'
    assert zero_pad_year(1) == '0001'
