# Generated by Django 4.1.7 on 2023-03-04 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectGreen', '0004_friend_delete_friends'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='reported',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='reviewed',
            field=models.BooleanField(default=False),
        ),
    ]