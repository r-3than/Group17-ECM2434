# Generated by Django 4.1.7 on 2023-03-02 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projectGreen', '0002_rename_challenge_date_activechallenge_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submission',
            old_name='challenge',
            new_name='active_challenge',
        ),
    ]
