# Generated by Django 4.1.5 on 2023-03-13 15:46

from django.db import migrations
from api.migration_utils.query_model_to_es_query import query_model_to_es_query
from api.migration_utils.es_query_to_query_model import es_query_to_query_model

def convert_query_format_to_es_query(apps, schema_editor):
    Query = apps.get_model('api', 'Query')
    queries = Query.objects.all()
    for query in queries:
        query.query_json = query_model_to_es_query(query.query_json)
        query.save()

def convert_query_format_to_query_model(apps, schema_editor):
    Query = apps.get_model('api', 'Query')
    queries = Query.objects.all()
    for query in queries:
        query.query_json = es_query_to_query_model(query.query_json)
        query.save()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_query_started'),
    ]

    operations = [
        migrations.RunPython(
            code=convert_query_format_to_es_query,
            reverse_code=convert_query_format_to_query_model,
        )
    ]
