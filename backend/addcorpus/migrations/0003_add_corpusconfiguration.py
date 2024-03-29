# Generated by Django 4.1.9 on 2023-08-08 14:03

import addcorpus.validation.creation
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('addcorpus', '0002_alter_corpus_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='CorpusConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allow_image_download', models.BooleanField(default=False, help_text='whether users can download document scans')),
                ('category', models.CharField(choices=[('newspaper', 'Newspapers'), ('parliament', 'Parliamentary debates'), ('periodical', 'Periodicals'), ('finance', 'Financial reports'), ('ruling', 'Court rulings'), ('review', 'Online reviews'), ('inscription', 'Funerary inscriptions'), ('oration', 'Orations'), ('book', 'Books')], help_text='category/medium of documents in this dataset', max_length=64)),
                ('description_page', models.CharField(blank=True, help_text='filename of the markdown documentation file for this corpus', max_length=128)),
                ('description', models.CharField(blank=True, help_text='short description of the corpus', max_length=254)),
                ('document_context', models.JSONField(help_text='specification of how documents are grouped into collections', null=True)),
                ('es_alias', models.SlugField(blank=True, help_text='alias assigned to the corpus index in elasticsearch', max_length=126)),
                ('es_index', models.SlugField(help_text='name of the corpus index in elasticsearch', max_length=126)),
                ('image', models.CharField(help_text='filename of the corpus image', max_length=126)),
                ('languages', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=8, validators=[addcorpus.validation.creation.validate_language_code]), help_text='languages used in the content of the corpus (from most to least frequent)', size=None)),
                ('min_date', models.DateField(help_text='earliest date for the data in the corpus')),
                ('max_date', models.DateField(help_text='latest date for the data in the corpus')),
                ('scan_image_type', models.CharField(blank=True, help_text='MIME type of scan images', max_length=64)),
                ('title', models.CharField(help_text='title of the corpus in the interface', max_length=256)),
                ('word_models_present', models.BooleanField(default=False, help_text='whether this corpus has word models')),
            ],
        ),
        migrations.RemoveField(
            model_name='corpus',
            name='description',
        ),
        migrations.AlterField(
            model_name='corpus',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='groups that have access to this corpus', related_name='corpora', to='auth.group'),
        ),
        migrations.AlterField(
            model_name='corpus',
            name='name',
            field=models.SlugField(help_text='internal name of the corpus', max_length=126, unique=True),
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(help_text='internal name for the field', max_length=126)),
                ('display_name', models.CharField(help_text='name that is displayed in the interface', max_length=256)),
                ('display_type', models.CharField(choices=[('text_content', 'text content'), ('text', 'text'), ('keyword', 'keyword'), ('date', 'date'), ('integer', 'integer'), ('float', 'float'), ('boolean', 'boolean')], help_text='as what type of data this field is rendered in the interface', max_length=16)),
                ('description', models.CharField(blank=True, help_text='explanatory text to be shown in the interface', max_length=254)),
                ('search_filter', models.JSONField(blank=True, help_text='specification of the search filter for this field (if any)')),
                ('results_overview', models.BooleanField(default=False, help_text='whether this field is shown in document previews in search results')),
                ('csv_core', models.BooleanField(default=False, help_text='whether this field is included in search results downloads by default')),
                ('search_field_core', models.BooleanField(default=False, help_text='whether this field is pre-selected when choosing search fields')),
                ('visualizations', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('resultscount', 'Number of results'), ('termfrequency', 'Frequency of the search term'), ('ngram', 'Neighbouring words'), ('wordcloud', 'Most frequent words')], max_length=16), blank=True, default=list, help_text='visualisations for this field', size=None)),
                ('visualization_sort', models.CharField(blank=True, choices=[('key', 'By the value of the field'), ('value', 'By frequency')], help_text='if the field has results/term frequency charts: how is the x-axis sorted?', max_length=8)),
                ('es_mapping', models.JSONField(help_text='specification of the elasticsearch mapping of this field')),
                ('indexed', models.BooleanField(default=True, help_text='whether this field is indexed in elasticsearch')),
                ('hidden', models.BooleanField(default=False, help_text='whether this field is hidden in the interface')),
                ('required', models.BooleanField(default=False, help_text='whether this field is required')),
                ('sortable', models.BooleanField(default=False, help_text='whether search results can be sorted on this field')),
                ('primary_sort', models.BooleanField(default=False, help_text='if sortable: whether this is the default method of sorting search results')),
                ('searchable', models.BooleanField(default=False, help_text='whether this field is listed when selecting search fields')),
                ('downloadable', models.BooleanField(default=True, help_text='whether this field can be included in search results downloads')),
                ('corpus_configuration', models.ForeignKey(help_text='corpus configuration that this field belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='addcorpus.corpusconfiguration')),
            ],
        ),
        migrations.AddField(
            model_name='corpusconfiguration',
            name='corpus',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='configuration', to='addcorpus.corpus'),
        ),
        migrations.AddConstraint(
            model_name='field',
            constraint=models.UniqueConstraint(fields=('corpus_configuration', 'name'), name='unique_name_for_corpus'),
        ),
    ]
