# Generated by Django 4.1.7 on 2023-03-22 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projectGreen', '0018_comment_blank'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='blank',
        ),
    ]