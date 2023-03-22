'''
Main Author:
    LB
Code-Review:
    TN
'''

import datetime
import pytz

from django.test import TestCase
from django.contrib.auth.models import User

from projectGreen.models import Profile, Challenge, ActiveChallenge, Submission, Upvote, SCORES

class UpvoteTestCase(TestCase):
    def setUp(self):
        for username in ['ab123','bc123','cd123']:
            user = User(username=username, password='unsecure_password')
            user.save()
        challenge = Challenge(description='test challenge', time_for_challenge=20)
        challenge.save()
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC), challenge=challenge)
        activechallenge.save()
        submission = Submission(username='ab123', active_challenge=activechallenge, submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC))
        submission.save()
        for username in ['bc123','cd123']:
            submission.create_upvote(username)

    def test_remove_upvote(self):
        for username in ['ab123','bc123','cd123']:
            Profile.recalculate_user_points_by_username(username)
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['upvote']['recieved'])
        for username in ['bc123','cd123']:
            profile = Profile.objects.get(user__username=username)
            self.assertEqual(profile.points, SCORES['upvote']['given'], 'points desync')
        self.assertEqual(len(Upvote.objects.all()), 2)

        # Remove upvote with delete_instance = False
        upvote = Upvote.objects.get(voter_username='bc123')
        upvote.remove_upvote(delete_instance=False)
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+SCORES['upvote']['recieved'], 'points not removed') # Points should be removed
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, 0)
        self.assertEqual(len(Upvote.objects.all()), 2) # Upvote should still exist

        # Remove upvote with delete_instance = True
        upvote = Upvote.objects.get(voter_username='cd123')
        upvote.remove_upvote(delete_instance=True)
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling(),  'points not removed') # Points should be removed
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, 0)
        self.assertEqual(len(Upvote.objects.all()), 1) # previous upvote should still exist

    def test_reinstate_upvote(self):
        Profile.recalculate_user_points_by_username('ab123')
        Profile.recalculate_user_points_by_username('bc123')
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['upvote']['recieved'])
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, SCORES['upvote']['given'])
        self.assertEqual(len(Upvote.objects.all()), 2)

        upvote = Upvote.objects.get(voter_username='bc123')
        upvote.remove_upvote(delete_instance=False)
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+SCORES['upvote']['recieved'], 'points not removed') # Points should be removed
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, 0)
        upvote.reinstate_upvote()
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['upvote']['recieved'], 'points not reinstated') # Points should be reinstated
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, SCORES['upvote']['given'])
