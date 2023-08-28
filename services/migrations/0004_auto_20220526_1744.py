# Generated by Django 2.2.10 on 2022-05-26 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_auto_20220526_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicecase',
            name='slug',
            field=models.SlugField(default='', editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='servicecase',
            name='url',
            field=models.CharField(default='', max_length=500),
        ),
    ]
