from datetime import datetime as dt

from django.db import models

USERNAME_MAX_LENGTH = 20
PATH_TO_SUBMISSIONS_FOLDER = 'photos'

class User(models.Model):
    username = models.CharField(max_length=USERNAME_MAX_LENGTH, primary_key=True)
    display_name = models.CharField(max_length=200)
    is_superuser = models.BooleanField()

class Friends(models.Model):
    self_username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    friend_username = models.CharField(max_length=USERNAME_MAX_LENGTH)

class Challenges(models.Model):
    challenge_id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=200)

class ActiveChallenges(models.Model):
    challenge_date = models.DateTimeField('challenge-date')
    challenge_id = models.ForeignKey(Challenges)
    is_expired = models.BooleanField()

''' COMPOUND KEYS NOT SUPPORTED BY django.models
class Submission(models.Model):
    username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    challenge_date = models.DateTimeField('challenge-date')
    models.UniqueConstraint(fields=['username', 'challenge_date'], name='user_and_date')

    def get_path(self):
        date = self.challenge_date.strtime('%Y-%m-%d')
        return 'photos\\{date}\\{username}.png'.format(date, self.username)
    
    def get_from_path(self, path):
        path = path.split('\\')
        cd = dt.strptime(path[1], '%Y-%m-%d')
        un = path[2].strip('.png')
        Submission.objects.get(username=un, challenge_date=cd)
'''

## Version using single path key, which can be decomposed into component keys

class Submission(models.Model):
    path = models.CharField(max_length=200, primary_key=True)

    def get_username(self):
        p = self.path.split('\\')
        username = p[2].strip('.png')
        return username
    
    def get_challenge_date(self):
        path = path.split('\\')
        challenge_date = dt.strptime(path[1], '%Y-%m-%d')
        return challenge_date

    def generate_path(username:str, challenge_date: dt):
        date = challenge_date.strtime('%Y-%m-%d')
        return '{path}\\{date}\\{username}.png'.format(path=PATH_TO_SUBMISSIONS_FOLDER,
                                                       date=date, username=username)

class Upvote(models.Model):
    submission_path = models.ForeignKey(Submission)
    username = models.CharField(max_length=USERNAME_MAX_LENGTH)