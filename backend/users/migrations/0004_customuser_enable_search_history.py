# Generated by Django 4.1.9 on 2023-07-18 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_sitedomain'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='enable_search_history',
            field=models.BooleanField(default=True),
        ),
    ]