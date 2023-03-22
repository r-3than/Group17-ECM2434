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

from projectGreen.models import Challenge, ActiveChallenge, Submission

class ActiveChallengeTestCase(TestCase):
    def setUp(self):
        user = User(username='ab123', password='unsecure_password')
        user.save()
        challenge = Challenge(description='test challenge', time_for_challenge=20)
        challenge.save()
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC), challenge=challenge)
        activechallenge.save()

    def test_create_submission(self):
        activechallenge = ActiveChallenge.objects.get(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC))
        activechallenge.create_submission('ab123', datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC))
        submission = Submission.objects.get(username='ab123')
        self.assertEqual(submission.submission_time, datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), 'create_submission failed')
        self.assertEqual(submission.username, 'ab123', 'create_submission failed')

    def test_get_last_active_challenge(self):
        challenge = Challenge.objects.get(description='test challenge')
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,30,0,0,pytz.UTC), challenge=challenge)
        activechallenge.save() # latest challenge
        activechallenge2 = ActiveChallenge(date=datetime.datetime(2023,3,9,10,10,0,0,pytz.UTC), challenge=challenge)
        activechallenge2.save()
        latest_challenge = ActiveChallenge.get_last_active_challenge()
        self.assertEqual(activechallenge, latest_challenge)
        challenge = Challenge(description='second test challenge', time_for_challenge=10)
        challenge.save() # introducing another challenge
        activechallenge3 = ActiveChallenge(date=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), challenge=challenge)
        activechallenge3.save()
        latest_challenge = ActiveChallenge.get_last_active_challenge()
        self.assertEqual(activechallenge, latest_challenge, 'fetched incorrect challenge')
        activechallenge4 = ActiveChallenge(date=datetime.datetime(2023,3,9,10,45,0,0,pytz.UTC), challenge=challenge)
        activechallenge4.save() # new latest
        latest_challenge = ActiveChallenge.get_last_active_challenge()
        self.assertEqual(activechallenge4, latest_challenge, 'didnt fetch new challenge')

    def test_get_challenge_description(self):
        activechallenge = ActiveChallenge.objects.get(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC))
        self.assertEqual('test challenge', activechallenge.get_challenge_description())