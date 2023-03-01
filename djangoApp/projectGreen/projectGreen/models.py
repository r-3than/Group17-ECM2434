from datetime import datetime as dt

from django.db import models
from django.contrib.auth.models import User

from projectGreen.settings import MICROSOFT
DOMAIN = MICROSOFT['valid_email_domains'][0]
# this is the primary domain; if multiple domains exist, then domain
# suffixes will be used in usernames not in the primary domain

def username_to_email(username: str) -> str:
    if '@' in username:
        return username
    else:
        return username + '@' + DOMAIN

def email_to_username(email: str) -> str:
    return email.strip('@'+DOMAIN)

USERNAME_MAX_LENGTH = 20
PATH_TO_SUBMISSIONS_FOLDER = 'photos'

'''
class User(models.Model):
    email = models.CharField(max_length=USERNAME_MAX_LENGTH, primary_key=True)
    username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    display_name = models.CharField(max_length=200)
    is_superuser = models.BooleanField()
    verbose_name = 'User'
    verbose_name_plural = 'Users'
    class Meta:
        db_table = 'Users'
        '''

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField()

    verbose_name = 'Profile'
    verbose_name_plural = 'Profiles'
    class Meta:
        db_table = 'Profiles'

class Friends(models.Model):
    self_username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    friend_username = models.CharField(max_length=USERNAME_MAX_LENGTH)

class Challenge(models.Model):
    challenge_id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=200)
    verbose_name = 'Challenge'
    verbose_name_plural = 'Challenges'
    class Meta:
        db_table = 'Challenges'

class ActiveChallenge(models.Model):
    challenge_date = models.DateTimeField('challenge-date', primary_key=True)
    # FOLLOWING LINE CAUSES AN ERROR
    #challenge_id = models.ForeignKey(Challenge, models.CASCADE)
    challenge_id = models.IntegerField() # TEMPORARY SOLUTION (TO CHANGE)
    is_expired = models.BooleanField(default=False)
    verbose_name = 'ActiveChallenge'
    verbose_name_plural = 'ActiveChallenges'
    class Meta:
        db_table = 'ActiveChallenges'

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
    submission_path = models.ForeignKey(Submission, models.CASCADE)
    username = models.CharField(max_length=USERNAME_MAX_LENGTH)