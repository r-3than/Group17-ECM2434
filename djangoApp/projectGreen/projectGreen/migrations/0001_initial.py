# Generated by Django 4.1.7 on 2023-03-01 21:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveChallenge',
            fields=[
                ('challenge_date', models.DateTimeField(primary_key=True, serialize=False, verbose_name='challenge-date')),
                ('challenge_id', models.IntegerField(default=0)),
                ('is_expired', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'ActiveChallenges',
            },
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('challenge_id', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('time_for_challenge', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'Challenges',
            },
        ),
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('self_username', models.CharField(max_length=20)),
                ('friend_username', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20)),
                ('challenge_date', models.DateTimeField(verbose_name='challenge date')),
                ('minutes_late', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Upvote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_username', models.CharField(max_length=20)),
                ('submission_date', models.DateTimeField(verbose_name='challenge date')),
                ('voter_username', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Profiles',
            },
        ),
    ]
