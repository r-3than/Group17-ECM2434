from django.db import models
from django.contrib.auth.models import User
from projectGreen.points import upvote_callback, remove_upvote, submission_callback, remove_submission

USERNAME_MAX_LENGTH = 20

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    number_of_submissions_removed = models.IntegerField(default=0)

    verbose_name = 'Profile'
    verbose_name_plural = 'Profiles'
    class Meta:
        db_table = 'Profiles'

class Friend(models.Model):
    left_username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    right_username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    pending = models.BooleanField(default=True)

    def create_friend_request(from_username: str, to_username: str):
        '''
        Creates a pending pair such that the left is the user sending the request
        and the right is the user recieving the request
        '''
        f = Friend(left_username=from_username, right_username=to_username, pending=True)
        f.save()

    def get_pending_friend_usernames(username: str) -> list[str]:
        '''
        Fetchs all friend connections to a user flagged as pending
        i.e. outstanding friend requests
        '''
        friend_requests = Friend.objects.filter(right_username=username)
        return [f.left_username for f in friend_requests]

    def get_friend_usernames(username: str) -> list[str]:
        '''
        Gets a list of usernames of all friends of a user
        '''
        friends_left = Friend.objects.filter(left_username=username, pending=False)
        friends = [friend.right_username for friend in friends_left]
        friends_right = Friend.objects.filter(right_username=username, pending=False)
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

    def report_submission(self):
        '''
        Marks a submission as reported - it will not be
        displayed in the feed while reported == True
        A post cannot be re-reported (once reviewed)
        Points are updated accordingly
        '''
        date = self.active_challenge.date.strftime('%Y-%m-%d')
        if self.reported:
            print('{username}\'s post on {date} has already been reported.'.format(self.username, date))
        elif self.reviewed:
            print('{username}\'s post on {date} has been reviewed.'.format(self.username, date))
        else:
            self.reported = True
            self.save()
            for u in self.get_upvotes():
                remove_upvote(u, False)
            remove_submission(self, False)

    def review_submission(self, is_suitable: bool):
        '''
        Sets reported to True if the post is deemed suitable and points are reinstated
        Otherwise, the submission is deleted, and their "removed submissions" count is incremented
        '''
        if self.reviewed:
            date = self.active_challenge.date.strftime('%Y-%m-%d')
            print('{username}\'s post on {date} has already been reviewed.'.format(self.username, date))
        self.reported = is_suitable
        self.reviewed = True
        if is_suitable:
            for u in self.get_upvotes():
                upvote_callback(self, u.voter_username, False)
            submission_callback(self.username, self.active_challenge, self.minutes_late, False)
        else:
            u = User.objects.get(username=self.username)
            try:
                p = Profile.objects.get(user=u)
                p.number_of_submissions_removed += 1
            except Profile.DoesNotExist:
                p = Profile(user=u, number_of_submissions_removed=1)
            p.save()
            self.delete()

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