from addcorpus.models import Corpus, Field
from addcorpus.corpus import CorpusDefinition, FieldDefinition
from django.contrib.auth.models import Group
from django.conf import settings
import re
from os.path import abspath, dirname
from importlib import util
import logging
logger = logging.getLogger(__name__)


def corpus_path(corpus_name):
    return abspath(settings.CORPORA.get(corpus_name))

def corpus_dir(corpus_name):
    """Gets the absolute path to the corpus definition directory

    Arguments:
        corpus_name {str} -- Key of the corpus in CORPORA object in settings
    """
    return dirname(corpus_path(corpus_name))

def load_corpus(corpus_name):
    filepath = corpus_path(corpus_name)

    try:
        corpus_spec = util.spec_from_file_location(
            corpus_name,
            filepath)

        corpus_mod = util.module_from_spec(corpus_spec)
    except FileNotFoundError:
        logger.critical(
            'No module describing the corpus "{0}" found in the specified file path:\
            {1}'.format(corpus_name, filepath)
        )
        raise

    corpus_spec.loader.exec_module(corpus_mod)
    # assume the class name of the endpoint is the same as the corpus name,
    # allowing for differences in camel case vs. lower case
    regex = re.compile('[^a-zA-Z]')
    corpus_name = regex.sub('', corpus_name)
    endpoint = next((attr for attr in dir(corpus_mod)
                     if attr.lower() == corpus_name), None)
    corpus_class = getattr(corpus_mod, endpoint)
    return corpus_class()

def _save_corpus_in_database(corpus_name, corpus_definition: CorpusDefinition):
    '''
    Save a corpus in the SQL database if it is not saved already.

    Parameters:
    - `corpus_name`: key of the corpus in settings.CORPORA
    - `corpus_definition`: a corpus object, output of `load_corpus`
    '''
    corpus_db, _ = Corpus.objects.get_or_create(name=corpus_name)
    corpus_db.description = corpus_definition.description
    _save_corpus_fields_in_database(corpus_definition, corpus_db)
    corpus_db.save()

def _save_corpus_fields_in_database(corpus_definition: CorpusDefinition, corpus_db: Corpus):
    # clear all fields and re-parse
    corpus_db.fields.all().delete()

    fields = corpus_db.fields.all()

    for field in corpus_definition.fields:
        _save_field_in_database(field, corpus_db)

def _save_field_in_database(field_definition: FieldDefinition, corpus: Corpus):
    attributes_to_copy = [
        'name', 'display_name', 'description',
        'results_overview',
        'csv_core', 'search_field_core',
        'visualizations', 'visualization_sort',
        'es_mapping', 'indexed', 'hidden',
        'required', 'sortable', 'primary_sort',
        'searchable', 'downloadable'
    ]

    get = lambda attr: field_definition.__getattribute__(attr)
    has_attribute = lambda attr: attr in dir(field_definition) and get(attr) != None

    copy_attributes = {
        attr: get(attr)
        for attr in attributes_to_copy
        if has_attribute(attr)
    }

    filter_definition = None #field_definition.search_filter.serialize() if field_definition.search_filter else None

    field = Field(
        corpus=corpus,
        search_filter=filter_definition,
        **copy_attributes,
    )

    field.save()
    return field

def _try_loading_corpus(corpus_name):
    try:
        return load_corpus(corpus_name)
    except Exception as e:
        message = 'Could not load corpus {}: {}'.format(corpus_name, e)
        logger.error(message)


def load_all_corpora():
    '''
    Return a dict with corpus names and corpus definition objects.
    '''
    corpus_definitions_unfiltered = {
        corpus_name: _try_loading_corpus(corpus_name)
        for corpus_name in settings.CORPORA.keys()
    }

    # filter any corpora without a valid definition
    corpus_definitions = {
        name: definition
        for name, definition in corpus_definitions_unfiltered.items()
        if definition
    }

    for corpus_name, corpus_definition in corpus_definitions.items():
        _save_corpus_in_database(corpus_name, corpus_definition)

    return corpus_definitions
