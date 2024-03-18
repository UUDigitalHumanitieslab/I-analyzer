from django.db import transaction
from addcorpus.python_corpora.corpus import CorpusDefinition, FieldDefinition
from addcorpus.models import Corpus, CorpusConfiguration, Field
from addcorpus.python_corpora.load_corpus import load_all_corpus_definitions
import sys

def _configuration_pk(corpus: Corpus):
    if corpus.has_configuration:
        return corpus.configuration.pk

def _save_corpus_configuration(corpus: Corpus, corpus_definition: CorpusDefinition):
    '''
    Save a corpus configuration in the SQL database.

    Parameters:
        corpus: a Corpus database object
        corpus_definition: a corpus object, output of `load_corpus`

    If the corpus already has a CorpusConfiguration, its contents will be overwritten
    based on the python definitions. If not, a new configuration will be created.

    This function is idempotent: a given corpus definition will always create the same
    configuration, regardless of what is currently saved in the database.
    '''

    # create a clean CorpusConfiguration object, but use the existing PK if possible
    configuration = CorpusConfiguration(pk=_configuration_pk(corpus), corpus=corpus)
    _copy_corpus_attributes(corpus_definition, configuration)
    configuration.save()
    configuration.full_clean()

    _save_corpus_fields_in_database(corpus_definition, configuration)

def get_defined_attributes(object, attributes):
    get = lambda attr: object.__getattribute__(attr)
    has_attribute = lambda attr: attr in dir(object) and get(attr) != None

    return {
        attr: get(attr)
        for attr in attributes
        if has_attribute(attr)
    }

def _copy_corpus_attributes(corpus_definition: CorpusDefinition, configuration: CorpusConfiguration):
    attributes_to_copy = [
        'description',
        'allow_image_download',
        'category',
        'description_page',
        'citation_page',
        'document_context',
        'es_alias',
        'es_index',
        'image',
        'languages',
        'min_date',
        'max_date',
        'scan_image_type',
        'title',
        'word_models_present',
        'default_sort',
        'language_field',
    ]

    try:
        defined = get_defined_attributes(corpus_definition, attributes_to_copy)
    except Exception as e:
        raise e

    for attr, value in defined.items():
        configuration.__setattr__(attr, value)

def _save_corpus_fields_in_database(corpus_definition: CorpusDefinition, configuration: CorpusConfiguration):
    for field in corpus_definition.fields:
        _save_field_in_database(field, configuration)

    for field in configuration.fields.exclude(name__in=corpus_definition.fieldnames):
        field.delete()

def _field_pk(name: str, configuration: CorpusConfiguration):
    if Field.objects.filter(corpus_configuration=configuration, name=name).exists():
        field = Field.objects.get(corpus_configuration=configuration, name=name)
        return field.pk

def _save_field_in_database(field_definition: FieldDefinition, configuration: CorpusConfiguration):
    attributes_to_copy = [
        'name', 'display_name', 'display_type',
        'description', 'results_overview',
        'csv_core', 'search_field_core',
        'visualizations', 'visualization_sort',
        'es_mapping', 'indexed', 'hidden',
        'required', 'sortable',
        'searchable', 'downloadable',
        'language',
    ]

    copy_attributes = get_defined_attributes(field_definition, attributes_to_copy)

    filter_definition = field_definition.search_filter.serialize() if field_definition.search_filter else {}

    field = Field(
        pk=_field_pk(field_definition.name, configuration),
        corpus_configuration=configuration,
        search_filter=filter_definition,
        **copy_attributes,
    )

    field.save()
    field.full_clean()
    return field

def _prepare_for_import(corpus):
    corpus.has_python_definition = True
    corpus.active = False
    corpus.save()

def _activate_if_ready(corpus):
    '''
    Check if the corpus passes ready_to_publish() check and set active property
    accordingly.
    '''
    corpus.active = corpus.ready_to_publish()
    corpus.save()

def _deactivate(corpus):
    corpus.active = False
    corpus.save()

def _clear_python_definition(corpus):
    '''
    Mark a corpus as one without a python definition deactivate it.
    '''
    corpus.has_python_definition = False
    corpus.active = False
    corpus.save()


def _save_or_skip_corpus(corpus_name, corpus_definition, verbose=False, stdout=sys.stdout, stderr=sys.stderr):
    '''
    Try saving a corpus definition to the database.

    This will create a new CorpusConfiguration object or replace an existing one.
    Changes are rolled back on failure.
    '''

    corpus, _ = Corpus.objects.get_or_create(name=corpus_name)

    try:
        with transaction.atomic():
            _prepare_for_import(corpus)
            _save_corpus_configuration(corpus, corpus_definition)
            _activate_if_ready(corpus)
        if verbose:
            print(f'Saved corpus: {corpus_name}',  file=stdout)
    except Exception as e:
        _deactivate(corpus)
        print(f'Failed saving corpus: {corpus_name}', file=stderr)
        print(f'Error: {e}', file=stderr)


def load_and_save_all_corpora(verbose=False, stdout=sys.stdout, stderr=sys.stderr):
    '''
    load all python corpus definitions and save them to the database
    '''

    corpus_definitions = load_all_corpus_definitions(stderr=stderr)

    for corpus_name, corpus_definition in corpus_definitions.items():
        _save_or_skip_corpus(corpus_name, corpus_definition, verbose=verbose, stdout=stdout, stderr=stderr)

    not_included = Corpus.objects.filter(has_python_definition=True).exclude(name__in=corpus_definitions.keys())
    for corpus in not_included:
        _clear_python_definition(corpus)
