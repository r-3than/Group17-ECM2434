from django.db import models
from django.contrib.auth.models import User

USERNAME_MAX_LENGTH = 20
PATH_TO_SUBMISSIONS_FOLDER = 'photos'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    verbose_name = 'Profile'
    verbose_name_plural = 'Profiles'
    class Meta:
        db_table = 'Profiles'

class Friends(models.Model):
    self_username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    friend_username = models.CharField(max_length=USERNAME_MAX_LENGTH)

class Challenge(models.Model):
    id = models.IntegerField(primary_key=True) # challenge_id
    description = models.CharField(max_length=200)
    time_for_challenge = models.IntegerField(default=0)
    verbose_name = 'Challenge'
    verbose_name_plural = 'Challenges'
    class Meta:
        db_table = 'Challenges'

class ActiveChallenge(models.Model):
    challenge_date = models.DateTimeField('Challenge Date', primary_key=True)
    challenge = models.ForeignKey(Challenge, models.CASCADE, null=True)
    is_expired = models.BooleanField(default=False)
    verbose_name = 'ActiveChallenge'
    verbose_name_plural = 'ActiveChallenges'
    class Meta:
        db_table = 'ActiveChallenges'

class Submission(models.Model):
    id = models.IntegerField(primary_key=True) # submission_id
    username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    challenge = models.ForeignKey(Challenge, models.CASCADE, null=True)
    minutes_late = models.IntegerField(default=0)
    # add photo field here

    verbose_name = 'Submission'
    verbose_name_plural = 'Submissions'
    class Meta:
        db_table = 'Submissions'

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
    submission = models.ForeignKey(Submission, models.CASCADE, null=True)
    #submission_username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    #submission_date = models.DateTimeField('challenge date')
    voter_username = models.CharField(max_length=USERNAME_MAX_LENGTH)

    verbose_name = 'Upvote'
    verbose_name_plural = 'Upvotes'
    class Meta:
        db_table = 'Upvotes'