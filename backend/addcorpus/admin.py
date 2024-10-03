from django.contrib import admin, messages
from .models import Corpus, CorpusConfiguration, CorpusDataFile, Field, CorpusDocumentationPage

def show_warning_message(request):
    '''
    Message to display when loading a form for a resource based on a python class
    '''

    messages.add_message(
        request,
        messages.WARNING,
        'This corpus configuration is specified in the source code; '
        'any changes here will be reset when the server is restarted.'
    )


class InlineDatafileAdmin(admin.StackedInline):
    model = CorpusDataFile
    fields = ['file', 'is_sample']
    show_change_link = True,
    extra = 0

class CorpusAdmin(admin.ModelAdmin):
    readonly_fields = ['configuration', 'ready_to_index', 'ready_to_publish']
    fields = ['name', 'groups', 'configuration', 'has_python_definition', 'ready_to_index', 'ready_to_publish', 'active']
    list_display = ['name', 'active']
    list_filter = ['groups', 'active']
    inlines = [InlineDatafileAdmin]

class InlineFieldAdmin(admin.StackedInline):
    model = Field
    fields = ['display_name', 'description']
    show_change_link = True
    extra = 0


class CorpusConfigurationAdmin(admin.ModelAdmin):
    readonly_fields = ['corpus']

    inlines = [
        InlineFieldAdmin
    ]

    fieldsets = [
        (
            None,
            {
                'fields': [
                    'corpus',
                    'title',
                    'description',
                    'image',
                ]
            }
        ), (
            'Source data extraction',
            {
                'fields': [
                    'data_directory',
                    'source_data_delimiter',
                ]
            }
        ), (
            'Content',
            {
                'fields': [
                    'category',
                    'languages',
                    'min_date',
                    'max_date',
                    'document_context',
                    'default_sort',
                ]
            }
        ), (
            'Elasticsearch',
            {
                'fields': [
                    'es_index',
                    'es_alias',
                ]
            }
        ), (
            'Scans',
            {
                'fields': [
                    'scan_image_type',
                    'allow_image_download',
                ]
            }
        ), (
            'Word models',
            {
                'fields': ['word_models_present']
            }
        )
    ]

    def get_form(self, request, obj=None, **kwargs):
        if obj and obj.corpus.has_python_definition:
            show_warning_message(request)
        return super().get_form(request, obj, **kwargs)


class FieldAdmin(admin.ModelAdmin):
    readonly_fields = ['corpus_configuration']
    list_filter = ['corpus_configuration']

    fieldsets = [
        (
            None,
            {
                'fields': [
                    'name',
                    'corpus_configuration',
                    'display_name',
                    'description',
                    'hidden',
                    'downloadable',
                ]
            }
        ),
        (
            'Source data extraction',
            {
                'fields': [
                    'extract_column',
                    'required',
                ]
            }
        ),
        (
            'Indexing options',
            {
                'fields': [
                    'es_mapping',
                    'indexed',
                ]
            }
        ), (
            'Search interface',
            {
                'fields': [
                    'search_filter',
                    'results_overview',
                    'searchable',
                    'search_field_core',
                    'sortable',
                ]
            }
        ), (
            'Visualisations',
            {
                'fields': [
                    'visualizations',
                    'visualization_sort',
                ]
            }
        )
    ]

    def get_form(self, request, obj=None, **kwargs):
        if obj and obj.corpus_configuration.corpus.has_python_definition:
            show_warning_message(request)
        return super().get_form(request, obj, **kwargs)


class CorpusDocumentationAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if obj and obj.corpus_configuration.corpus.has_python_definition:
            show_warning_message(request)
        return super().get_form(request, obj, **kwargs)

admin.site.register(Corpus, CorpusAdmin)
admin.site.register(CorpusConfiguration, CorpusConfigurationAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(CorpusDocumentationPage, CorpusDocumentationAdmin)
