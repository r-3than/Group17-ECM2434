# Generated by Django 4.1.6 on 2023-03-21 10:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projectGreen', '0009_storeitem_item_bytes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='storeitem',
            old_name='item_bytes',
            new_name='photo_bytes',
        ),
    ]