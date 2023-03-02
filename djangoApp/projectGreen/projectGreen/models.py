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
    time_for_challenge = models.IntegerField(default=0)
    verbose_name = 'Challenge'
    verbose_name_plural = 'Challenges'
    class Meta:
        db_table = 'Challenges'

class ActiveChallenge(models.Model):
    challenge_date = models.DateTimeField('challenge-date', primary_key=True)
    # FOLLOWING LINE CAUSES AN ERROR
    #challenge_id = models.ForeignKey(Challenge, models.CASCADE)
    challenge_id = models.IntegerField(default=0) # TEMPORARY SOLUTION (TO CHANGE)
    is_expired = models.BooleanField(default=False)
    verbose_name = 'ActiveChallenge'
    verbose_name_plural = 'ActiveChallenges'
    class Meta:
        db_table = 'ActiveChallenges'

class Submission(models.Model):
    username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    challenge_date = models.DateTimeField('challenge date')
    minutes_late = models.IntegerField()
    #models.UniqueConstraint(fields=['username', 'challenge_date'], name='user_and_date')

    '''
    def get_path(self):
        date = self.challenge_date.strtime('%Y-%m-%d')
        return 'photos\\{date}\\{username}.png'.format(date, self.username)
    
    def get_from_path(self, path):
        path = path.split('\\')
        cd = dt.strptime(path[1], '%Y-%m-%d')
        un = path[2].strip('.png')
        Submission.objects.get(username=un, challenge_date=cd)
    '''
    
class Upvote(models.Model):
    #submission_path = models.ForeignKey(Submission, models.CASCADE)
    submission_username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    submission_date = models.DateTimeField('challenge date')
    voter_username = models.CharField(max_length=USERNAME_MAX_LENGTH)