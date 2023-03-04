from django.db import models
from django.contrib.auth.models import User

USERNAME_MAX_LENGTH = 20
#PATH_TO_SUBMISSIONS_FOLDER = 'photos'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    verbose_name = 'Profile'
    verbose_name_plural = 'Profiles'
    class Meta:
        db_table = 'Profiles'

class Friend(models.Model):
    left_username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    right_username = models.CharField(max_length=USERNAME_MAX_LENGTH)

    def get_friend_usernames(username: str) -> list[str]:
        friends_left = Friend.objects.filter(left_username=username)
        friends = [friend.right_username for friend in friends_left]
        friends_right = Friend.objects.filter(right_username=username)
        all_friends = friends + [friend.left_username for friend in friends_right]
        return all_friends

    verbose_name = 'Friend'
    verbose_name_plural = 'Friends'
    class Meta:
        db_table = 'Friends'

class Challenge(models.Model):
    description = models.CharField(max_length=200)
    time_for_challenge = models.IntegerField(default=0)

    verbose_name = 'Challenge'
    verbose_name_plural = 'Challenges'
    class Meta:
        db_table = 'Challenges'

class ActiveChallenge(models.Model):
    date = models.DateTimeField('Challenge Date', primary_key=True)
    challenge = models.ForeignKey(Challenge, models.CASCADE, null=True)
    is_expired = models.BooleanField(default=False)

    verbose_name = 'ActiveChallenge'
    verbose_name_plural = 'ActiveChallenges'
    class Meta:
        db_table = 'ActiveChallenges'

class Submission(models.Model):
    username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    active_challenge = models.ForeignKey(ActiveChallenge, models.CASCADE, null=True)
    minutes_late = models.IntegerField(default=0)
    reported = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    # TODO add base 64 photo field here

    def report_submission(self):
        '''
        Marks a submission as reported - it will not be
        displayed in the feed while reported == True
        A post cannot be re-reported
        '''
        if self.reviewed:
            date = self.active_challenge.date.strftime('%Y-%m-%d')
            print('{username}\'s post on {date} has already been reviewed.'.format(self.username, date))
        else:
            self.reported = True
            self.save()

    def review_submission(self, is_suitable: bool):
        '''
        Sets reported to True if the post is deemed suitable
        '''
        self.reported = is_suitable
        self.reviewed = True

    verbose_name = 'Submission'
    verbose_name_plural = 'Submissions'
    class Meta:
        db_table = 'Submissions'
    
class Upvote(models.Model):
    submission = models.ForeignKey(Submission, models.CASCADE, null=True)
    voter_username = models.CharField(max_length=USERNAME_MAX_LENGTH)

    verbose_name = 'Upvote'
    verbose_name_plural = 'Upvotes'
    class Meta:
        db_table = 'Upvotes'