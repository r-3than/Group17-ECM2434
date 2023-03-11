from django.db import models
from django.contrib.auth.models import User
from datetime import datetime as dt
import math

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
    number_of_submissions_removed = models.IntegerField(default=0)

    def user_data(self, fetch: bool=True, delete: bool=False):
        '''
        Can fetch all data related to a single user
        Will delete all this data if delete flag is set
        '''
        data = {}
        u = self.user
        data['profile'] = self
        data['friends'] = Friend.objects.filter(left_username=u.username) + Friend.objects.filter(right_username=u.username)
        data['submissions'] = Submission.objects.filter(user=u)
        data['upvotes']['given'] = Upvote.objects.filter(voter_username=u.username)
        data['upvotes']['recieved'] = []
        for sub in data['submissions']:
            data['upvotes']['recieved'].append(sub.get_upvotes())
        if delete:
            for sub in data['submissions']:
                sub.remove_submission()
            for up in data['upvotes']['given']:
                up.remove_upvote()
            data['friends'].delete()
            u.delete()
            self.delete()
        if fetch: return data

    @classmethod
    def set_points_by_username(cls, username: str, points_value: int):
        '''
        Sets the points of a user's profile
        '''
        try:
            profile = Profile.objects.get(user__username=username)
            profile.points = points_value
        except Profile.DoesNotExist:
            u = User.objects.get(username=username)
            profile = Profile(user=u, points=points_value)
        profile.save()

    def set_points(self, points_value: int):
        '''
        Sets the points of a user's profile
        '''
        self.points = points_value
        self.save()

    @classmethod
    def add_points_by_username(cls, username: str, points_to_add: int):
        '''
        Increments a user's points in their profile
        '''
        try:
            profile = Profile.objects.get(user__username=username)
            profile.points += points_to_add
        except Profile.DoesNotExist:
            u = User.objects.get(username=username)
            profile = Profile(user=u, points=points_to_add)
        profile.save()

    def add_points(self, points_to_add: int):
        '''
        Increments a user's points in their profile
        '''
        self.points += points_to_add
        self.save()

    @classmethod
    def recalculate_user_points_by_username(cls, username: str):
        '''
        Calculates the total points for a user based on submissions and interactions
        Interactions are only counted / points are only assigned for non-reported submissions
        '''
        points = 0
        upvotes_given = Upvote.objects.filter(voter_username=username, submission__reported=False)
        points += len(upvotes_given)*SCORES['upvote']['given']
        upvotes_recieved = Upvote.objects.filter(submission__username=username, submission__reported=False)
        points += len(upvotes_recieved)*SCORES['upvote']['recieved']
        submissions = Submission.objects.filter(username=username)
        for sub in submissions:
            if sub.reported:
                continue
            points += int(SCORES['submission'] * sub.get_punctuality_scaling())
        Profile.set_points_by_username(username, points)

    def recalculate_user_points(self):
        '''
        Calculates the total points for a user based on submissions and interactions
        Interactions are only counted / points are only assigned for non-reported submissions
        '''
        username = self.user.username
        points = 0
        upvotes_given = Upvote.objects.filter(voter_username=username, submission__reported=False)
        points += len(upvotes_given)*SCORES['upvote']['given']
        upvotes_recieved = Upvote.objects.filter(submission__username=username, submission__reported=False)
        points += len(upvotes_recieved)*SCORES['upvote']['recieved']
        submissions = Submission.objects.filter(username=username)
        for sub in submissions:
            if sub.reported:
                continue
            points += int(SCORES['submission'] * sub.get_punctuality_scaling())
        self.user.profile.set_points(points)

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

    def create_submission(self, username: str, submission_time: dt, create_submission_instance: bool=True):
        '''
        Creates submission object associated with this challenge in database and syncronises points
        '''
        s = Submission(username=username, active_challenge=self, submission_time=submission_time)
        if create_submission_instance:
            s.save()
        Profile.add_points_by_username(username, int(SCORES['submission']*s.get_punctuality_scaling()))                           

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
            print('{}\'s post on {} has already been reported.'.format(self.username, date))
        elif self.reviewed:
            print('{}\'s post on {} has been reviewed.'.format(self.username, date))
        else:
            for u in self.get_upvotes():
                u.remove_upvote(False)
            self.remove_submission(False)
            self.reported = True
            self.save()

    def review_submission(self, is_suitable: bool):
        '''
        Sets reported to False if the post is deemed suitable and points are reinstated
        Otherwise, the submission is deleted, and their "removed submissions" count is incremented
        '''
        date = self.active_challenge.date.strftime('%Y-%m-%d')
        if not self.reported:
            print('{}\'s post on {} has not been reported.'.format(self.username, date))
        elif self.reviewed:
            print('{}\'s post on {} has already been reviewed.'.format(self.username, date))
        else:
            self.reported = False if is_suitable else True
            self.reviewed = True
            self.save()
            if is_suitable:
                self.reinstate_submission()
            else:
                u = User.objects.get(username=self.username)
                try:
                    p = Profile.objects.get(user=u)
                    p.number_of_submissions_removed += 1
                except Profile.DoesNotExist:
                    p = Profile(user=u, number_of_submissions_removed=1)
                p.save()
                self.delete()

    def remove_submission(self, delete_instance: bool=True):
        '''
        Removes submission object, as well as associated upvote objects,
        from database (conditional flag) and synchronises points
        '''
        if not self.reported:
            points_to_remove = SCORES['submission'] * self.get_punctuality_scaling()
            #profile = Profile.objects.get(user__username=self.username)
            Profile.add_points_by_username(self.username, -int(points_to_remove))
            for upvote in self.get_upvotes():
                upvote.remove_upvote(delete_instance)
        if delete_instance: self.delete()

    def reinstate_submission(self): # TODO implement this fix
        '''
        Adds points associated with a submission back (used after submission review)
        '''
        points = SCORES['submission'] * self.get_punctuality_scaling()
        Profile.add_points_by_username(self.username, int(points))
        for upvote in self.get_upvotes():
            upvote.reinstate_upvote()

    def create_upvote(self, voter_username: str, create_upvote_instance: bool=True):
        '''
        Creates upvote object for this submission in database and syncronises points
        '''
        u = Upvote(submission=self, voter_username=voter_username)
        if create_upvote_instance:
            u.save()
        Profile.add_points_by_username(self.username, SCORES['upvote']['recieved'])
        Profile.add_points_by_username(voter_username, SCORES['upvote']['given'])
        
    def get_upvotes(self) -> list:
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
        Removes upvote object from database (conditional flag) and synchronises points
        '''
        if not self.submission.reported:
            Profile.add_points_by_username(self.voter_username, -SCORES['upvote']['given'])
            Profile.add_points_by_username(self.submission.username, -SCORES['upvote']['recieved'])
        if delete_instance: self.delete()

    def reinstate_upvote(self): # TODO implement this fix
        '''
        Adds points from an upvote back (used after submission review)
        '''
        Profile.add_points_by_username(self.voter_username, SCORES['upvote']['given'])
        Profile.add_points_by_username(self.submission.username, SCORES['upvote']['recieved'])

    verbose_name = 'Upvote'
    verbose_name_plural = 'Upvotes'
    class Meta:
        db_table = 'Upvotes'