from django.db import models
from django.contrib.auth.models import User
from projectGreen.points import upvote_callback, remove_upvote, submission_callback, remove_submission

USERNAME_MAX_LENGTH = 20
SCORES = {'submission':10, 'upvote':{'given':1, 'recieved':2}}

def punctuality_scaling(time_for_challenge: int, minutes_late: int):
    '''
    Used to scale points based on "lateness" of submission
    max ~= sqrt(time_for_challenge); min = 1
    '''
    return round(math.sqrt(max(time_for_challenge-minutes_late, 0)+1))


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
    pending = models.BooleanField(default=True)

    @classmethod
    def create_friend_request(cls, from_username: str, to_username: str):
        '''
        Creates a pending pair such that the left is the user sending the request
        and the right is the user recieving the request
        '''
        f = Friend(left_username=from_username, right_username=to_username, pending=True)
        f.save()

    @classmethod
    def get_pending_friend_usernames(cls, username: str) -> list[str]:
        '''
        Fetchs all friend connections to a user flagged as pending
        i.e. outstanding friend requests
        '''
        friend_requests = Friend.objects.filter(right_username=username)
        return [f.left_username for f in friend_requests]

    @classmethod
    def get_friend_usernames(cls, username: str) -> list[str]:
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
class Friend(models.Model):
    left_username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    right_username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    pending = models.BooleanField(default=True)

    @classmethod
    def create_friend_request(cls, from_username: str, to_username: str):
        '''
        Creates a pending pair such that the left is the user sending the request
        and the right is the user recieving the request
        '''
        f = Friend(left_username=from_username, right_username=to_username, pending=True)
        f.save()

    @classmethod
    def get_pending_friend_usernames(cls, username: str) -> list[str]:
        '''
        Fetchs all friend connections to a user flagged as pending
        i.e. outstanding friend requests
        '''
        friend_requests = Friend.objects.filter(right_username=username)
        return [f.left_username for f in friend_requests]

    @classmethod
    def get_friend_usernames(cls, username: str) -> list[str]:
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
    submission_time = models.DateTimeField('Submission Time', null=True)
    reported = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    photo_bytes = models.BinaryField(null=True)

    def get_minutes_late(self) -> int:
        '''
        Calculates time from when the challenge was set to when the submission was made
        '''
        late = self.submission_time - self.active_challenge.date
        return late.total_seconds() // 60
    
    def get_punctuality_scaling(self) -> float:
        time_for_challenge = self.active_challenge.challenge.time_for_challenge
        return punctuality_scaling(time_for_challenge, self.get_minutes_late())

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
            self.remove_submission(False)
            self.reported = True
            self.save()
            for u in self.get_upvotes():
                remove_upvote(u, False)
            remove_submission(self, False)
            self.reported = True
            self.save()

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
    
    def get_upvote_count(self) -> int:
        '''
        Gets the number of Upvotes for a submission
        '''
        return len(self.get_upvotes())

    verbose_name = 'Submission'
    verbose_name_plural = 'Submissions'
    class Meta:
        db_table = 'Submissions'
    
class Upvote(models.Model):
    submission = models.ForeignKey(Submission, models.CASCADE, null=True)
    voter_username = models.CharField(max_length=USERNAME_MAX_LENGTH)

    def remove_upvote(self, delete_instance: bool=True):
        '''
        Removes upvote object in database (conditional flag) and syncronises points
        '''
        if not self.submission.reported:
            Profile.add_points(self.voter_username, -SCORES['upvote']['given'])
            Profile.add_points(self.submission.username, -SCORES['upvote']['recieved'])
        if delete_instance: self.delete()

    def reinstate_upvote(self): # TODO implement this fix
        '''
        Adds points from an upvote back (used after submission review)
        '''
        Profile.add_points(self.voter_username, SCORES['upvote']['given'])
        Profile.add_points(self.submission.username, SCORES['upvote']['recieved'])

    verbose_name = 'Upvote'
    verbose_name_plural = 'Upvotes'
    class Meta:
        db_table = 'Upvotes'