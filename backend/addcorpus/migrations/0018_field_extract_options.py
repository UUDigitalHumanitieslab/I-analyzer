# Generated by Django 4.2.11 on 2024-04-10 13:58

import addcorpus.validation.creation
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addcorpus', '0017_source_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='extract_options',
            field=models.JSONField(blank=True, default=dict, help_text='options related to source data extraction', validators=[addcorpus.validation.creation.validate_field_extract_options]),
        ),
    ]