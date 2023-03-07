from django.db import models
from django.contrib.auth.models import User
from projectGreen.points import SCORES, add_points, upvote_callback, remove_upvote, submission_callback, remove_submission

import base64

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
    photo_bytes = models.BinaryField(null=True)
    # bytestring is untested

    @classmethod # @ethan please check this
    def from_base64(cls, username, challenge, minutes_late, photo_base64):
        photo_bytestring = base64.encodebytes(photo_base64)
        return cls(username=username, challenge=challenge, minutes_late=minutes_late, photo_bytes=photo_bytestring)

    def report_submission(self):
        '''
        Marks a submission as reported - it will not be
        displayed in the feed while reported == True
        A post cannot be re-reported
        Points are updated accordingly
        '''
        if self.reviewed:
            date = self.active_challenge.date.strftime('%Y-%m-%d')
            print('{username}\'s post on {date} has already been reviewed.'.format(self.username, date))
        else:
            self.reported = True
            self.save()
            for u in self.get_upvotes():
                # removes points from upvotes associated with this submission
                remove_upvote(u, False)
            remove_submission(self, False)

    def review_submission(self, is_suitable: bool):
        '''
        Sets reported to True if the post is deemed suitable
        Points are updated accordingly
        '''
        self.reported = is_suitable
        self.reviewed = True
        if is_suitable:
            # reinstate points
            for u in self.get_upvotes():
                upvote_callback(self, u.voter_username, False)
            submission_callback(self.username, self.active_challenge, self.minutes_late, False)

    def get_upvotes(self):
        '''
        Gets list of Upvotes for this submission
        '''
        return Upvote.objects.filter(submission=self)

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