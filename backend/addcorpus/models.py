from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import Group
from django.contrib import admin
from django.core.exceptions import ValidationError
import warnings

from addcorpus.constants import CATEGORIES, MappingType, VisualizationType
from addcorpus.validation.creation import validate_language_code, \
    validate_image_filename_extension, validate_markdown_filename_extension, \
    validate_es_mapping, validate_mimetype, validate_search_filter, \
    validate_name_is_not_a_route_parameter, validate_search_filter_with_mapping, \
    validate_searchable_field_has_full_text_search, \
    validate_visualizations_with_mapping, validate_implication, \
    validate_sort_configuration, validate_field_language
from addcorpus.validation.indexing import validate_has_configuration, \
    validate_essential_fields, validate_language_field
from addcorpus.validation.publishing import validate_ngram_has_date_field,  \
    validate_default_sort

MAX_LENGTH_NAME = 126
MAX_LENGTH_DESCRIPTION = 254
MAX_LENGTH_TITLE = 256


class Corpus(models.Model):
    name = models.SlugField(
        max_length=MAX_LENGTH_NAME,
        unique=True,
        help_text='internal name of the corpus',
    )
    groups = models.ManyToManyField(
        Group,
        related_name='corpora',
        blank=True,
        help_text='groups that have access to this corpus',
    )
    active = models.BooleanField(
        default=False,
        help_text='an inactive corpus is hidden from the search interface',
    )
    has_python_definition = models.BooleanField(
        default=False,
        help_text='whether the configuration of this corpus is determined by a Python '
            'module (some features are only available for Python-based corpora)',
    )

    @property
    def has_configuration(self):
        try:
            self.configuration
            return True
        except:
            return False

    class Meta:
        verbose_name_plural = 'corpora'

    def __str__(self):
        return self.name

    @admin.display()
    def ready_to_index(self) -> bool:
        '''
        Checks whether the corpus is ready for indexing.

        Runs a try/except around `self.validate_ready_to_index()` and returns a
        boolean; `True` means the validation completed without errors.

        If you want to see validation error messages, use the validation method
        directly.
        '''
        try:
            self.validate_ready_to_index()
            return True
        except:
            return False

    def validate_ready_to_index(self) -> None:
        '''
        Validation that should be carried out before indexing.

        Raises:
            CorpusNotIndexableError: the corpus is not meeting requirements for making
                an index.
        '''

        validate_has_configuration(self)

        config = self.configuration
        fields = config.fields.all()

        validate_essential_fields(fields)
        validate_language_field(self)


    @admin.display()
    def ready_to_publish(self) -> bool:
        '''
        Checks whether the corpus is ready to be made public.
        '''
        try:
            self.validate_ready_to_publish()
            return True
        except:
            return False

    def validate_ready_to_publish(self) -> None:
        '''
        Validation that should be carried out before making the corpus public.

        Raises:
            CorpusNotIndexableError: the corpus is not meeting requirements for indexing.
            CorpusNotPublishableError: interface options are improperly configured.
        '''

        self.validate_ready_to_index()
        validate_ngram_has_date_field(self)
        validate_default_sort(self)

    def clean(self):
        if self.active:
            try:
                self.validate_ready_to_publish()
            except Exception as e:
                raise ValidationError([
                    'Corpus is set to "active" but does not meet requirements for publication.',
                    e
                ])

class CorpusConfiguration(models.Model):
    '''
    The configuration of the corpus as set by the definition file.

    Corpora require a CorpusConfiguration to function, but while the
    Corpus object should be preserved as a reference point for relationships,
    the CorpusConfiguration can safely be removed and re-initialised when
    parsing corpus definitions.
    '''

    corpus = models.OneToOneField(
        to=Corpus,
        on_delete=models.CASCADE,
        related_name='configuration',
    )
    allow_image_download = models.BooleanField(
        default=False,
        help_text='whether users can download document scans',
    )
    category = models.CharField(
        max_length=64,
        choices=CATEGORIES,
        help_text='category/medium of documents in this dataset',
    )
    description_page = models.CharField(
        max_length=128,
        blank=True,
        validators=[validate_markdown_filename_extension],
        help_text='filename of the markdown documentation file for this corpus',
    )
    citation_page = models.CharField(
        max_length=128,
        blank=True,
        validators=[validate_markdown_filename_extension],
        help_text='filename of the citation specification (in markdown) for this corpus',
    )
    description = models.CharField(
        max_length=MAX_LENGTH_DESCRIPTION,
        blank=True,
        help_text='short description of the corpus',
    )
    document_context = models.JSONField(
        null=True,
        help_text='specification of how documents are grouped into collections',
    )
    es_alias = models.SlugField(
        max_length=MAX_LENGTH_NAME,
        blank=True,
        help_text='alias assigned to the corpus index in elasticsearch',
    )
    es_index = models.SlugField(
        max_length=MAX_LENGTH_NAME,
        help_text='name of the corpus index in elasticsearch'
    )
    image = models.CharField(
        max_length=126,
        validators=[validate_image_filename_extension],
        help_text='filename of the corpus image',
    )
    languages = ArrayField(
        models.CharField(
            max_length=8,
            validators=[validate_language_code],
            blank=True,
        ),
        help_text='languages used in the content of the corpus (from most to least frequent)',
    )
    min_date = models.DateField(
        help_text='earliest date for the data in the corpus',
    )
    max_date = models.DateField(
        help_text='latest date for the data in the corpus',
    )
    scan_image_type = models.CharField(
        max_length=64,
        blank=True,
        validators=[validate_mimetype],
        help_text='MIME type of scan images',
    )
    title = models.CharField(
        max_length=MAX_LENGTH_TITLE,
        help_text='title of the corpus in the interface',
    )
    word_models_present = models.BooleanField(
        default=False,
        help_text='whether this corpus has word models',
    )
    default_sort = models.JSONField(
        blank=True,
        validators=[validate_sort_configuration],
        default=dict,
        help_text='default sort for search results without query text; '
            'if blank, results are presented in the order in which they are stored',
    )
    language_field = models.CharField(
        blank=True,
        help_text='name of the field that specifies the language of documents (if any);'
            'required to use "dynamic" language on fields',
    )

    def __str__(self):
        return f'Configuration of <{self.corpus.name}>'

    def clean(self):
        if self.corpus.active:
            try:
                self.corpus.validate_ready_to_publish()
            except Exception as e:
                raise ValidationError([
                    'Corpus configuration is not valid for an active corpus. Deactivate '
                    'the corpus or correct the following errors.',
                    e
                ])


FIELD_DISPLAY_TYPES = [
    ('text_content', 'text content'),
    (MappingType.TEXT.value, 'text'),
    (MappingType.KEYWORD.value, 'keyword'),
    (MappingType.DATE.value, 'date'),
    (MappingType.DATE_RANGE.value, 'date_range'),
    (MappingType.INTEGER.value, 'integer'),
    (MappingType.FLOAT.value, 'float'),
    (MappingType.BOOLEAN.value, 'boolean'),
    (MappingType.GEO_POINT.value, 'geo_point')
]

FIELD_VISUALIZATIONS = [
    (VisualizationType.RESULTS_COUNT.value, 'Number of results'),
    (VisualizationType.TERM_FREQUENCY.value, 'Frequency of the search term'),
    (VisualizationType.NGRAM.value, 'Neighbouring words'),
    (VisualizationType.WORDCLOUD.value, 'Most frequent words'),
]
'''Options for `visualizations` field'''

VISUALIZATION_SORT_OPTIONS = [
    ('key', 'By the value of the field'),
    ('value', 'By frequency')
]
'''Options for `visualization_sort` field'''


class Field(models.Model):
    name = models.SlugField(
        max_length=MAX_LENGTH_NAME,
        validators=[validate_name_is_not_a_route_parameter],
        help_text='internal name for the field',
    )
    corpus_configuration = models.ForeignKey(
        to=CorpusConfiguration,
        on_delete=models.CASCADE,
        related_name='fields',
        help_text='corpus configuration that this field belongs to',
    )
    display_name = models.CharField(
        max_length=MAX_LENGTH_TITLE,
        help_text='name that is displayed in the interface',
    )
    display_type = models.CharField(
        max_length=16,
        choices=FIELD_DISPLAY_TYPES,
        help_text='as what type of data this field is rendered in the interface',
    )
    description = models.CharField(
        max_length=MAX_LENGTH_DESCRIPTION,
        blank=True,
        help_text='explanatory text to be shown in the interface',
    )
    search_filter = models.JSONField(
        blank=True,
        validators=[validate_search_filter],
        help_text='specification of the search filter for this field (if any)',
    )
    results_overview = models.BooleanField(
        default=False,
        help_text='whether this field is shown in document previews in search results',
    )
    csv_core = models.BooleanField(
        default=False,
        help_text='whether this field is included in search results downloads by default',
    )
    search_field_core = models.BooleanField(
        default=False,
        help_text='whether this field is pre-selected when choosing search fields',
    )
    visualizations = ArrayField(
            models.CharField(
            max_length=16,
            choices=FIELD_VISUALIZATIONS,
        ),
        blank=True,
        default=list,
        help_text='visualisations for this field',
    )
    visualization_sort = models.CharField(
        max_length=8,
        choices=VISUALIZATION_SORT_OPTIONS,
        blank=True,
        help_text='if the field has results/term frequency charts: how is the x-axis sorted?',
    )
    es_mapping = models.JSONField(
        validators=[validate_es_mapping],
        help_text='specification of the elasticsearch mapping of this field',
    )
    indexed = models.BooleanField(
        default=True,
        help_text='whether this field is indexed in elasticsearch',
    )
    hidden = models.BooleanField(
        default=False,
        help_text='whether this field is hidden in the interface',
    )
    required = models.BooleanField(
        default=False,
        help_text='whether this field is required',
    )
    sortable = models.BooleanField(
        default=False,
        help_text='whether search results can be sorted on this field',
    )
    searchable = models.BooleanField(
        default=False,
        help_text='whether this field is listed when selecting search fields',
    )
    downloadable = models.BooleanField(
        default=True,
        help_text='whether this field can be included in search results downloads',
    )
    language = models.CharField(
        max_length=64,
        blank=True,
        null=False,
        validators=[validate_field_language],
        help_text='specification for the language of this field; can be blank, an IETF '
            'tag, or "dynamic"; "dynamic" means the language is determined by the '
            'language_field of the corpus configuration',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['corpus_configuration', 'name'],
                                name='unique_name_for_corpus')
        ]

    @property
    def is_main_content(self) -> bool:
        return self.display_type == 'text_content'

    def __str__(self) -> str:
        return f'{self.name} ({self.corpus_configuration.corpus.name})'

    def clean(self):
        validate_searchable_field_has_full_text_search(self.es_mapping, self.searchable)

        if self.search_filter:
            validate_search_filter_with_mapping(self.es_mapping, self.search_filter)

        if self.visualizations:
            validate_visualizations_with_mapping(self.es_mapping, self.visualizations)

        validate_implication(self.csv_core, self.downloadable, "Core download fields must be downloadable")

        # core search fields must searchable
        # not a hard requirement because it is not currently satisfied in all corpora
        try:
            validate_implication(self.search_field_core, self.searchable, "Core search fields must be searchable")
        except ValidationError as e:
            warnings.warn(e.message)

        if self.corpus_configuration.corpus.active:
            try:
                self.corpus_configuration.corpus.validate_ready_to_publish()
            except Exception as e:
                raise ValidationError([
                    'Field configuration is not valid in an active corpus. Deactivate '
                    'the corpus or correct the following errors.',
                    e
                ])
