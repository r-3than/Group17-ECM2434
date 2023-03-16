'''
Main Author:
    TN - Models and points system
Sub-Author:
    LB - Challenge model helper functions; overall code review
'''

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime as dt
import math
import logging
import urllib.request
from projectGreen.settings import PROFANITY_FILTER_SOURCE_URL

LOGGER = logging.getLogger(__name__)

USERNAME_MAX_LENGTH = 20
SCORES = {'submission':20, 'upvote':{'given':1, 'recieved':4}, 'comment':{'given':3, 'recieved':12}}

def punctuality_scaling(time_for_challenge: int, minutes_late: int) -> int:
    '''
    Used to scale points based on "lateness" of submission
    max ~= sqrt(time_for_challenge); min = 1
    '''
    return round(math.sqrt(max(time_for_challenge-minutes_late, 0)+1))

def load_profanity_file() -> list[str]:
    '''
    Loads list of profane words from the provided source URL
    Note that changing the source may require an alteration to the current formatting
    '''
    url_stream = urllib.request.urlopen(PROFANITY_FILTER_SOURCE_URL)
    LOGGER.info('loaded profanity file from {}'.format(PROFANITY_FILTER_SOURCE_URL))
    return [line.decode().strip('\n') for line in url_stream.readlines()][1:]

WORDS_TO_FILTER = load_profanity_file()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    number_of_submissions_removed = models.IntegerField(default=0)
    number_of_comments_removed = models.IntegerField(default=0)
    number_of_false_reports = models.IntegerField(default=0)

    def user_data(self, fetch: bool=True, delete: bool=False) -> dict:
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
        data['comments']['given'] = Comment.objects.filter(comment_username=u.username)
        data['upvotes']['recieved'] = []
        data['comments']['recieved'] = []
        for sub in data['submissions']:
            data['upvotes']['recieved'].append(sub.get_upvotes())
            data['comments']['recieved'].append(sub.get_comments())
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
        # upvote points
        upvotes_given = Upvote.objects.filter(voter_username=username, submission__reported=False)
        points += len(upvotes_given)*SCORES['upvote']['given']
        upvotes_recieved = Upvote.objects.filter(submission__username=username, submission__reported=False)
        points += len(upvotes_recieved)*SCORES['upvote']['recieved']
        # comment points
        comments_given = Comment.objects.filter(comment_username=username, submission__reported=False, reported=False)
        points += len(comments_given)*SCORES['comment']['given']
        comments_recieved = Comment.objects.filter(submission__username=username, submission__reported=False, reported=False)
        points += len(comments_recieved)*SCORES['comment']['recieved']
        # submission points
        submissions = Submission.objects.filter(username=username)
        for sub in submissions:
            if sub.reported:
                continue
            points += SCORES['submission'] * sub.get_punctuality_scaling()
        Profile.set_points_by_username(username, points)

    def recalculate_user_points(self):
        '''
        Calculates the total points for a user based on submissions and interactions
        Interactions are only counted / points are only assigned for non-reported submissions
        '''
        username = self.user.username
        points = 0
        # upvote points
        upvotes_given = Upvote.objects.filter(voter_username=username, submission__reported=False)
        points += len(upvotes_given)*SCORES['upvote']['given']
        upvotes_recieved = Upvote.objects.filter(submission__username=username, submission__reported=False)
        points += len(upvotes_recieved)*SCORES['upvote']['recieved']
        # comment points
        comments_given = Comment.objects.filter(comment_username=username, submission__reported=False, reported=False)
        points += len(comments_given)*SCORES['comment']['given']
        comments_recieved = Comment.objects.filter(submission__username=username, submission__reported=False, reported=False)
        points += len(comments_recieved)*SCORES['comment']['recieved']
        # submission points
        submissions = Submission.objects.filter(username=username)
        for sub in submissions:
            if sub.reported:
                continue
            points += SCORES['submission'] * sub.get_punctuality_scaling()
        self.user.profile.set_points(points)

    @classmethod
    def get_profile(cls, username: str) -> 'Profile':
        '''
        Ensures profile exists and fetches it
        '''
        Profile.add_points_by_username(username, 0)
        return Profile.objects.get(username=username)

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
        # checks that users exist
        try:
            User.objects.get(username=from_username)
        except User.DoesNotExist:
            LOGGER.warning('the queried user "{}" does not exist'.format(from_username))
            return
        try:
            User.objects.get(username=to_username)
        except User.DoesNotExist:
            LOGGER.warning('the queried user "{}" does not exist'.format(to_username))
            return
        
        try: # check if friend object already exists
            f = Friend.objects.get(left_username=from_username, right_username=to_username)
            if f.pending:
                LOGGER.warning('friend request from {} to {} is still pending.'.format(from_username, to_username))
            else:
                LOGGER.warning('{} and {} are already friends.'.format(from_username, to_username))
            return
        except Friend.DoesNotExist:
            pass
        try: # check if friend object already exists (alternate direction)
            f = Friend.objects.get(left_username=to_username, right_username=from_username)
            if f.pending:
                f.pending = False
                f.save()
            else:
                LOGGER.warning('{} and {} are already friends.'.format(from_username, to_username))
        except Friend.DoesNotExist: # creates friend object
            f = Friend(left_username=from_username, right_username=to_username, pending=True)
            f.save()

    @classmethod
    def get_pending_friend_usernames(cls, username: str) -> list[str]:
        '''
        Fetchs all friend connections to a user flagged as pending
        i.e. outstanding friend requests
        '''
        friend_requests = Friend.objects.filter(right_username=username, pending=True)
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
    
    @classmethod
    def get_friend_post_count(cls, username: str, active_challenge: 'ActiveChallenge') -> int:
        '''
        Counts the number of friends who have posted for the given challenge
        '''
        friend_usernames = Friend.get_friend_usernames(username)
        valid_submissions = []
        for un in friend_usernames:
            try:
                s = Submission.objects.get(username=un, active_challenge=active_challenge, reported=False)
                valid_submissions.append(s)
            except Submission.DoesNotExist:
                pass
        return len(valid_submissions)

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
        Throws django.db.utils.IntegrityError if submission already exists.
        '''
        s = Submission(username=username, active_challenge=self, submission_time=submission_time)
        if create_submission_instance:
            s.save()
        Profile.add_points_by_username(username, SCORES['submission']*s.get_punctuality_scaling())                         

    @classmethod
    def get_last_active_challenge(cls) -> 'ActiveChallenge':
        '''
        Returns the most recent (current) ActiveChallenge object
        '''
        return ActiveChallenge.objects.latest('date')
    
    def get_challenge_description(self) -> str:
        '''
        Returns the challenge description asociated with an ActiveChallenge object
        '''
        return self.challenge.description

    verbose_name = 'ActiveChallenge'
    verbose_name_plural = 'ActiveChallenges'
    class Meta:
        db_table = 'ActiveChallenges'

class Submission(models.Model):
    username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    active_challenge = models.ForeignKey(ActiveChallenge, models.CASCADE, null=True)
    submission_time = models.DateTimeField('Submission Time', null=True)
    reported = models.BooleanField(default=False)
    reported_by = models.CharField(max_length=USERNAME_MAX_LENGTH, null=True)
    reviewed = models.BooleanField(default=False)
    photo_bytes = models.BinaryField(null=True)

    @classmethod
    def user_has_submitted(cls, username: str) -> bool:
        '''
        Checks if a user has submitted for the most recent challenge
        '''
        ac = ActiveChallenge.get_last_active_challenge()
        try:
            Submission.objects.get(username=username, active_challenge=ac)
            return True
        except Submission.DoesNotExist:
            return False

    def get_minutes_late(self) -> int:
        '''
        Calculates time from when the challenge was set to when the submission was made
        '''
        late = self.submission_time - self.active_challenge.date
        return late.total_seconds() // 60
    
    def get_punctuality_scaling(self) -> float:
        '''
        Value used to scale the points awarded for a submission
        '''
        time_for_challenge = self.active_challenge.challenge.time_for_challenge
        return punctuality_scaling(time_for_challenge, self.get_minutes_late())

    def report_submission(self, reporter_username: str) -> bool:
        '''
        Marks a submission as reported - it will not be
        displayed in the feed while reported == True
        A post cannot be re-reported (once reviewed)
        Points are updated accordingly
        Returns False if post has already been reported/reviewed
        '''
        date = self.active_challenge.date.strftime('%Y-%m-%d')
        if self.reported:
            LOGGER.warning('{}\'s post on {} has already been reported.'.format(self.username, date))
        elif self.reviewed:
            LOGGER.warning('{}\'s post on {} has been reviewed.'.format(self.username, date))
        else:
            self.remove_submission(False)
            self.reported = True
            self.reported_by = reporter_username
            self.save()
            return True
        return False

    def review_submission(self, is_suitable: bool) -> bool:
        '''
        Sets reported to False if the post is deemed suitable and points are reinstated
        Otherwise, the submission is deleted, and their "removed submissions" count is incremented
        Returns False if the post is either not reported, or already reviewed
        '''
        date = self.active_challenge.date.strftime('%Y-%m-%d')
        if not self.reported:
            LOGGER.warning('{}\'s post on {} has not been reported.'.format(self.username, date))
        elif self.reviewed:
            LOGGER.warning('{}\'s post on {} has already been reviewed.'.format(self.username, date))
        else:
            self.reported = False if is_suitable else True
            self.reviewed = True
            self.save()
            if is_suitable:
                self.reinstate_submission()
                p = Profile.get_profile(self.reported_by)
                try:
                    p.number_of_false_reports += 1
                except :
                    p.number_of_false_reports = 1
                p.save()
            else:
                u = User.objects.get(username=self.username)
                try:
                    p = Profile.objects.get(user=u)
                    p.number_of_submissions_removed += 1
                except Profile.DoesNotExist:
                    p = Profile(user=u, number_of_submissions_removed=1)
                p.save()
                self.delete()
            return True
        return False

    def remove_submission(self, delete_instance: bool=True) -> bool:
        '''
        Removes submission object, as well as associated upvote objects,
        from database (conditional flag) and synchronises points
        Returns False if post is reported (points do not change)
        '''
        if not self.reported:
            points_to_remove = SCORES['submission'] * self.get_punctuality_scaling()
            Profile.add_points_by_username(self.username, -points_to_remove)
            for upvote in self.get_upvotes():
                upvote.remove_upvote(delete_instance)
            for comment in self.get_comments():
                comment.remove_comment(delete_instance)
        if delete_instance: self.delete()
        return not self.reported

    def reinstate_submission(self):
        '''
        Adds points associated with a submission back (used after submission review)
        '''
        points = SCORES['submission'] * self.get_punctuality_scaling()
        Profile.add_points_by_username(self.username, points)
        for upvote in self.get_upvotes():
            upvote.reinstate_upvote()
        for comment in self.get_comments():
            comment.reinstate_comment()

    def create_upvote(self, voter_username: str, create_upvote_instance: bool=True) -> bool:
        '''
        Creates upvote object for this submission in database and syncronises points
        CREATING UPVOTE ON REPORTED SUBMISSION WILL LIKELY CAUSE POINTS DESYNC
        Returns False if the upvote already exists
        '''
        try:
            Upvote.objects.get(submission=self, voter_username=voter_username)
            return False
        except Upvote.DoesNotExist:
            u = Upvote(submission=self, voter_username=voter_username)
            if create_upvote_instance:
                u.save()
            Profile.add_points_by_username(self.username, SCORES['upvote']['recieved'])
            Profile.add_points_by_username(voter_username, SCORES['upvote']['given'])
            return True

    def create_comment(self, comment_username: str, comment_content: str, create_comment_instance: bool=True) -> bool:
        '''
        Creates comment object for this submission in database and syncronises points
        Returns False if comment was flagged for profanity
        '''
        u = Comment(submission=self, comment_username=comment_username, content=comment_content)
        if create_comment_instance:
            u.save()
        Profile.add_points_by_username(self.username, SCORES['comment']['recieved'])
        Profile.add_points_by_username(comment_username, SCORES['comment']['given'])
        if u.inappropriate_language_filter():
            u.report_comment()
            return False
        else:
            return True
        
    def get_upvotes(self) -> list['Upvote']:
        '''
        Gets list of Upvotes for this submission
        '''
        return Upvote.objects.filter(submission=self)
    
    def get_comments(self) -> list['Comment']:
        '''
        Gets list of Comments for this submission
        Reported comments are excluded from this list
        '''
        return Comment.objects.filter(submission=self, reported=False)
    
    def get_upvote_count(self) -> int:
        '''
        Gets the number of Upvotes for a submission
        '''
        return len(self.get_upvotes())
    
    def get_comment_count(self) -> int:
        '''
        Gets the number of Comments for a submission
        Reported comments are excluded from this count
        '''
        return len(self.get_comments())

    verbose_name = 'Submission'
    verbose_name_plural = 'Submissions'
    class Meta:
        db_table = 'Submissions'
        constraints = [
            models.UniqueConstraint(fields=['username','active_challenge'],
                                    name='single_submission_per_active_challenge')
        ]
    
class Upvote(models.Model):
    submission = models.ForeignKey(Submission, models.CASCADE, null=True)
    voter_username = models.CharField(max_length=USERNAME_MAX_LENGTH)

    def remove_upvote(self, delete_instance: bool=True) -> bool:
        '''
        Removes upvote object from database (conditional flag) and synchronises points
        Returns False if associated post is reported (points do not change)
        '''
        if not self.submission.reported:
            Profile.add_points_by_username(self.voter_username, -SCORES['upvote']['given'])
            Profile.add_points_by_username(self.submission.username, -SCORES['upvote']['recieved'])
        if delete_instance: self.delete()
        return not self.submission.reported

    def reinstate_upvote(self):
        '''
        Adds points from an upvote back (used after submission review)
        '''
        Profile.add_points_by_username(self.voter_username, SCORES['upvote']['given'])
        Profile.add_points_by_username(self.submission.username, SCORES['upvote']['recieved'])

    verbose_name = 'Upvote'
    verbose_name_plural = 'Upvotes'
    class Meta:
        db_table = 'Upvotes'

class Comment(models.Model):
    submission = models.ForeignKey(Submission, models.CASCADE, null=True)
    comment_username = models.CharField(max_length=USERNAME_MAX_LENGTH)
    content = models.CharField(max_length=256)
    reported = models.BooleanField(default=False)
    reported_by = models.CharField(max_length=USERNAME_MAX_LENGTH, null=True)
    reviewed = models.BooleanField(default=False)

    def report_comment(self, reporter_username: str) -> bool:
        '''
        Marks a comment as reported - it will not be
        displayed on a post while reported == True
        A comment cannot be re-reported (once reviewed)
        Points are updated accordingly
        Returns False if comment has already been reported/reviewed
        '''
        date = self.submission.active_challenge.date.strftime('%Y-%m-%d')
        if self.reported:
            LOGGER.warning('{}\'s comment on {}\' post (on {}) has already been reported.'.format(self.comment_username, self.submission.username, date))
        elif self.reviewed:
            LOGGER.warning('{}\'s comment on {}\' post (on {}) has been reviewed.'.format(self.comment_username, self.submission.username, date))
        else:
            self.remove_comment(False)
            self.reported = True
            self.reported_by = reporter_username
            self.save()
            return True
        return False

    def review_comment(self, is_suitable: bool) -> bool:
        '''
        Sets reported to False if the comment is deemed suitable and points are reinstated
        Otherwise, the comment is deleted, and their "removed comment" count is incremented
        Returns False if the comment is either not reported, or already reviewed
        '''
        date = self.submission.active_challenge.date.strftime('%Y-%m-%d')
        if not self.reported:
            LOGGER.warning('{}\'s comment on {}\' post (on {}) has not been reported.'.format(self.comment_username, self.submission.username, date))
        elif self.reviewed:
            LOGGER.warning('{}\'s comment on {}\' post (on {}) has already been reviewed.'.format(self.comment_username, self.submission.username, date))
        else:
            self.reported = False if is_suitable else True
            self.reviewed = True
            self.save()
            if is_suitable:
                self.reinstate_comment()
                p = Profile.get_profile(self.reported_by)
                try:
                    p.number_of_false_reports += 1
                except :
                    p.number_of_false_reports = 1
                p.save()
            else:
                u = User.objects.get(username=self.comment_username)
                try:
                    p = Profile.objects.get(user=u)
                    p.number_of_comments_removed += 1
                except Profile.DoesNotExist:
                    p = Profile(user=u, number_of_comments_removed=1)
                p.save()
                self.delete()
            return True
        return False

    def remove_comment(self, delete_instance: bool=True) -> bool:
        '''
        Removes comment object from database (conditional flag) and synchronises points
        Returns False if either the submission or comment is reported (points do not change)
        '''
        condition = not (self.submission.reported or self.reported)
        if condition:
            Profile.add_points_by_username(self.comment_username, -SCORES['comment']['given'])
            Profile.add_points_by_username(self.submission.username, -SCORES['comment']['recieved'])
        if delete_instance: self.delete()
        return condition

    def reinstate_comment(self) -> bool:
        '''
        Adds points from an comment back (used after submission review)
        Returns False if either the comment is reported (points do not change)
        '''
        if not self.reported:
            Profile.add_points_by_username(self.comment_username, SCORES['comment']['given'])
            Profile.add_points_by_username(self.submission.username, SCORES['comment']['recieved'])
        return not self.reported

    def inappropriate_language_filter(self) -> bool:
        '''
        Flags inappropriate words based on WORDS_TO_FILTER; called by create_comment
        May flag false positives; hence comment is reported not removed
        '''
        for word in WORDS_TO_FILTER:
            if word in self.content:
                LOGGER.warning('flagged inappropriate word "{}" in {}\'s comment'.format(word, self.comment_username))
                return True
        return False