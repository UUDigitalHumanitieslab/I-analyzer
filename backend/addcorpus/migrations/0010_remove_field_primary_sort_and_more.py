# Generated by Django 4.2.10 on 2024-03-11 10:44

import addcorpus.validation.creation
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addcorpus', '0009_corpusconfiguration_citation_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='field',
            name='primary_sort',
        ),
        migrations.AddField(
            model_name='corpusconfiguration',
            name='default_sort',
            field=models.JSONField(blank=True, default=dict, help_text='default sort for search results without query text; if blank, results are presented in the order in which they are stored', validators=[addcorpus.validation.creation.validate_sort_configuration]),
        ),
    ]
