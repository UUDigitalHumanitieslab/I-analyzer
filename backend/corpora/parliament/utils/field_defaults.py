from datetime import datetime

from addcorpus.python_corpora.corpus import FieldDefinition
from addcorpus.python_corpora.filters import DateFilter, MultipleChoiceFilter
from corpora.parliament.utils.constants import MIN_DATE, MAX_DATE
from addcorpus.es_mappings import keyword_mapping, text_mapping, date_mapping, main_content_mapping

# For every field `foo` in the Parliament corpora, this file should have a function `foo()`
# which creates a default instance of the field. It does not include an extractor, since that
# depends on the corpus.

# Corpora that include a `foo` field should initialise it with `foo()` and then modify attributes as needed.

MIN_DATE = datetime(year=1800, month=1, day=1)
MAX_DATE = datetime(year=2022, month=12, day=31)


def book_id():
    """Unique ID of the book in which the speech was recorded"""
    return FieldDefinition(
        name='book_id',
        display_name='Book ID',
        description='Unique identifier of the book in which the speech was recorded',
        es_mapping=keyword_mapping(),
    )

def book_label():
    """Label of the book in which the speech was recorded"""
    return FieldDefinition(
        name='book_label',
        display_name='Book label',
        description='Label of the book in which the speech was recorded',
        es_mapping=text_mapping(),
    )

def chamber():
    "human-readable name of chamber (commons, senate, etc)"
    return FieldDefinition(
        name='chamber',
        display_name='Chamber',
        description='Chamber in which the debate took place',
        es_mapping=keyword_mapping(),
        search_filter = MultipleChoiceFilter(
            description='Search only in debates from the selected chamber(s)',
            option_count=2
        ),
        visualizations = ['resultscount', 'termfrequency']
    )

def committee():
    'Committee that held the debate.'
    return FieldDefinition(
        name = 'committee',
        display_name = 'Committee',
        description = 'Committee that held the debate',
        es_mapping = keyword_mapping(),
        search_filter = MultipleChoiceFilter(
            description='Search only in debates from the selected committee(s)',
        ),
        visualizations = ['resultscount', 'termfrequency']
    )

def country():
    "Country in which the debate took place"
    return FieldDefinition(
        name='country',
        display_name='Country',
        description='Country in which the debate took place',
        es_mapping=keyword_mapping(),
    )

def date():
    "The date on which the debate took place."
    return FieldDefinition(
        name='date',
        display_name='Date',
        description='The date on which the debate took place.',
        es_mapping=date_mapping(),
        results_overview=True,
        search_filter=DateFilter(
            MIN_DATE,
            MAX_DATE,
            description='Search only within this time range.'
        ),
        visualizations=['resultscount', 'termfrequency'],
        csv_core=True,
    )

def date_is_estimate():
    """Wether the date field is an estimate. Boolean value."""
    return FieldDefinition(
        name='date_is_estimate',
        display_name='Date is estimate',
        description='Whether the recorded date is an estimate',
        es_mapping={'type':'boolean'}
    )


def date_earliest():
    "The earliest date on which the debate may have taken place"
    return FieldDefinition(
        name='date_earliest',
        display_name='Earliest date',
        description='The date on which the debate took place.',
        es_mapping=date_mapping(),
        results_overview=True,
        search_filter=DateFilter(
            MIN_DATE,
            MAX_DATE,
            description='Search only debates with the earliest possible date in this time range'
        ),
        visualizations=['resultscount', 'termfrequency'],
        csv_core=True,
    )

def date_latest():
    "The latest date on which the debate may have taken place"
    return FieldDefinition(
        name='date_latest',
        display_name='Latest date',
        description='The date on which the debate took place.',
        es_mapping=date_mapping(),
        results_overview=True,
        search_filter=DateFilter(
            MIN_DATE,
            MAX_DATE,
            description='Search only debates with the latest possible date in this time range'
        ),
        visualizations=['resultscount', 'termfrequency'],
        csv_core=True,
    )

def era(include_aggregations = True):
    if include_aggregations:
        return FieldDefinition(
            name='era',
            es_mapping=keyword_mapping(),
            display_name='Era',
            description='The parliamentary era in which the speech or debate was held',
            visualizations=['resultscount', 'termfrequency'],
            search_filter = MultipleChoiceFilter(
                description='Search only in debates from the selected era(s)',
                option_count=10
            ),
        )
    else:
        return FieldDefinition(
            name = 'era',
            display_name='Era',
            description='The parliamentary era in which the speech or debate was held',
        )


def chamber():
    "human-readable name of house (commons, senate, etc)"
    return FieldDefinition(
        name='chamber',
        display_name='Chamber',
        description='Chamber in which the debate took place',
        es_mapping=keyword_mapping(),
        search_filter = MultipleChoiceFilter(
            description='Search only in debates from the selected chamber(s)',
            option_count=2
        ),
        visualizations = ['resultscount', 'termfrequency']
    )

def column():
    "column number or range (used in UK data) (string)"
    return FieldDefinition(
        name='column',
        display_name='Column(s)',
        description='Column(s) of the speech in the original document',
        es_mapping=keyword_mapping(),
        searchable=False,
    )

def debate_type():
    "Type of debate in which the speech occurred"
    return FieldDefinition(
        name='debate_type',
        display_name='Debate type',
        description='Type of debate in which the speech occurred',
        es_mapping=keyword_mapping(),
    )

def debate_title():
    "Title of the debate in which the speech was held"
    return FieldDefinition(
        name='debate_title',
        display_name='Debate title',
        description='Title of the debate in which the speech was held',
        es_mapping=text_mapping(),
        search_field_core=True,
    )

def debate_id():
    "unique ID for the debate"
    return FieldDefinition(
        name='debate_id',
        display_name='Debate ID',
        description='Unique identifier of the debate in which the speech was held',
        es_mapping=keyword_mapping(),
    )

def language():
    return FieldDefinition(
        name='language',
        display_name='Language',
        description='Language of the speech',
        es_mapping=keyword_mapping(),
        search_filter = MultipleChoiceFilter(
            description='Search only in speeches in the selected languages',
            option_count=50
        ),
        visualizations = ['resultscount', 'termfrequency']
    )

def legislature():
    ""
    return FieldDefinition(
        name='legislature',
        display_name='Legislature',
        description='Title of individuals elected to parliament',
        es_mapping=keyword_mapping(),
        visualizations=['resultscount', 'termfrequency'],
        search_filter = MultipleChoiceFilter(
            description='Search only in debates from the selected era(s)',
            option_count=10
        ),
    )

def topic():
    "if debates are divided into topics, they are specified here"
    return FieldDefinition(
        name='topic',
        display_name='Topic',
        description='Topic of the debate in which the speech was held',
        es_mapping=text_mapping(),
        search_field_core=True,
    )

def subtopic():
    "further division of topics into subtopics"
    return FieldDefinition(
        name='subtopic',
        display_name='Subtopic',
        description='Subtopic of the debate in which the speech was held',
        es_mapping=text_mapping(),
    )

def sequence():
    "integer index of the speech in a debate"
    return FieldDefinition(
        name='sequence',
        display_name='Sequence',
        description='Index of the sequence of speeches in a debate',
        es_mapping={'type': 'integer'},
        sortable=True,
        searchable=False,
    )


def source_archive():
    """
    A field which can be used to (internally) keep track of the source
    of the specific dataset
    """
    return FieldDefinition(
        name='source_archive',
        es_mapping=keyword_mapping(),
        hidden=True
    )


def speech(language=None):
    """
    speech is a multifield with subfields clean (lowercase, stopwords, no numbers) and stemmed (as clean, but also stemmed)
    stopword and stemmer filter need to be defined for each language
    """
    has_language = language != None
    return FieldDefinition(
        name='speech',
        display_name='Speech',
        description='The transcribed speech',
        # each index has its own definition of the 'clean' and 'stemmed' analyzer, based on language
        es_mapping = main_content_mapping(
            token_counts=True,
            stopword_analysis=has_language,
            stemming_analysis=has_language,
            language=language,
            updated_highlighting=True
        ),
        results_overview=True,
        search_field_core=True,
        display_type='text_content',
        visualizations=['wordcloud', 'ngram'],
        csv_core=True,
        language=language,
    )

def speech_id():
    "unique (corpus-level) ID for the speech"
    return FieldDefinition(
        name='id',
        display_name='Speech ID',
        description='Unique identifier of the speech',
        es_mapping=keyword_mapping(),
        csv_core=True,
    )

def speaker():
    "name of the speaker"
    return FieldDefinition(
        name='speaker',
        display_name='Speaker',
        description='The speaker of the transcribed speech',
        es_mapping=keyword_mapping(enable_full_text_search=True),
        results_overview=True,
        search_field_core=True,
        visualizations=['resultscount', 'termfrequency'],
        csv_core=True,
    )

def speech_type():
    "type of speech, e.g. question, answer, interjection, point of order"
    return FieldDefinition(
        name='speech_type',
        display_name='Speech type',
        description='The type of speech',
        es_mapping=keyword_mapping(),
    )

def speaker_id():
    "unique (corpus level) ID for the speaker"
    return FieldDefinition(
        name='speaker_id',
        display_name='Speaker ID',
        description='Unique identifier of the speaker',
        es_mapping=keyword_mapping(),
    )

def speaker_constituency():
    "Constituency represented by the speaker"
    return FieldDefinition(
        name='speaker_constituency',
        display_name='Speaker constituency',
        description='Constituency represented by the speaker',
        es_mapping=keyword_mapping(),
        visualizations=['resultscount', 'termfrequency']
    )

def speaker_birthplace():
    """Birthplace of the speaker (string)"""
    return FieldDefinition(
        name='speaker_birthplace',
        display_name='Speaker place of birth',
        description='Birthplace of the speaker',
        es_mapping=keyword_mapping(),
    )

def speaker_birth_country():
    """Birth country of the speaker (string)"""
    return FieldDefinition(
        name='speaker_birth_country',
        display_name='Speaker country of birth',
        description='Country in which the speaker was born',
        es_mapping=keyword_mapping(),
    )

def speaker_birth_year():
    """Year in which the speaker was born (int)"""
    return FieldDefinition(
        name='speaker_birth_year',
        display_name='Speaker year of birth',
        description='Year in which the speaker was born',
        es_mapping={'type': 'integer'}
    )

def speaker_death_year():
    """Year in which the speaker died (int)"""
    return FieldDefinition(
        name='speaker_death_year',
        display_name='Speaker year of death',
        description='Year in which the speaker died',
        es_mapping={'type': 'integer'},
    )

def speaker_gender():
    """Gender of the speaker."""
    return FieldDefinition(
        name='speaker_gender',
        display_name='Speaker gender',
        description='Gender of the speaker',
        es_mapping=keyword_mapping(),
        visualizations=['resultscount', 'termfrequency'],
    )

def speaker_profession():
    """Profession of the speaker."""
    return FieldDefinition(
        name='speaker_profession',
        display_name='Speaker profession',
        description='Profession of the speaker',
        es_mapping=keyword_mapping(),
    )

def speaker_aristocracy():
    """Whether the speaker is a member of the aristocracy"""
    return FieldDefinition(
        name='speaker_aristocracy',
        display_name='Speaker aristocracy',
        description='Aristocratic title of the speaker',
        es_mapping=keyword_mapping(),
    )

def speaker_academic_title():
    """Academic title of the speaker"""
    return FieldDefinition(
        name='speaker_academic_title',
        display_name='Speaker academic title',
        description='Academic title of the speaker',
        es_mapping=keyword_mapping(),
    )


def parliamentary_role():
    "parliamentary role of the speaker (speaker, chair, MP, etc...)"
    return FieldDefinition(
        name='role',
        display_name='Parliamentary role',
        description='Role of the speaker in parliament',
        es_mapping=keyword_mapping(),
        search_filter=MultipleChoiceFilter(
            description='Search for speeches by speakers with the selected roles',
        ),
        visualizations=['resultscount', 'termfrequency'],
    )

def ministerial_role():
    'Ministerial role of the speaker (minister of such-and-such, etc.)'
    return FieldDefinition(
        name='ministerial_role',
        display_name='Ministerial role',
        description='Ministerial role of the speaker',
        es_mapping=keyword_mapping(),
        search_filter=MultipleChoiceFilter(
            description='Search for speeches by speakers with the selected ministerial roles',
        ),
        visualizations=['resultscount', 'termfrequency'],
    )

def role_long():
    """Expanded description of the value for `role`."""
    return FieldDefinition(
        name='role_long',
        display_name='Role (long)',
        description='Expanded description of role of the speaker in the debate',
        es_mapping=text_mapping(),
    )

def party():
    "name of the political party of the speaker"
    return FieldDefinition(
        name='party',
        display_name='Party',
        description='Political party that the speaker belongs to',
        es_mapping=keyword_mapping(),
        search_filter= MultipleChoiceFilter(
            description='Search in speeches from the selected parties',
            option_count=50
        ),
        visualizations=['resultscount', 'termfrequency']
    )

def party_id():
    "unique ID of the party"
    return FieldDefinition(
        name='party_id',
        display_name='Party ID',
        description='Unique identifier of the political party the speaker belongs to',
        es_mapping=keyword_mapping(),
    )

def party_full():
    "human-readable name of the party"
    return FieldDefinition(
        name='party_full',
        display_name='Party (full name)',
        description='Full name of the political party that the speaker belongs to',
        es_mapping=text_mapping(),
    )

def party_role():
    """
    Role of the speaker's party in parliament (opposition, coalition, cabinet, etc.)
    """
    return FieldDefinition(
        name='party_role',
        display_name='Party role',
        description='Role of the speaker\'s political party in parliament at the time of speaking',
        es_mapping=keyword_mapping(),
        search_filter= MultipleChoiceFilter(
            description='Search in speeches from the selected parties',
            option_count=10
        ),
        visualizations=['resultscount', 'termfrequency']
    )

def page():
    "page number or range (string)"
    return FieldDefinition(
        name='page',
        display_name='Page(s)',
        description='Page(s) of the speech in the original document',
        es_mapping=keyword_mapping(),
        searchable=False,
    )

def page_source():
    "page number in source document (can contain letters)"
    return FieldDefinition(
        name='page_source',
        display_name='Source page number',
        description='Page number in source document',
        es_mapping=keyword_mapping()
    )


def subject():
    """subject of the speech. Unlike topics, which usually indicate the specific agenda item,
    subjects are general (e.g. agriculture, education). Also unlike topic, this is keyword field."""
    return FieldDefinition(
        name='subject',
        display_name='Subject',
        description='Subject that the speech is concerned with',
        es_mapping=keyword_mapping(),
        search_filter = MultipleChoiceFilter(
            description='Search only in speeches about the selected subjects',
            option_count=50
        ),
        visualizations = ['resultscount', 'termfrequency']
    )

def url():
    """url of the source file"""
    return FieldDefinition(
        name='url',
        display_name='Source URL',
        display_type='url',
        description='URL to source file of this speech',
        es_mapping=keyword_mapping(),
        searchable=False,
    )
