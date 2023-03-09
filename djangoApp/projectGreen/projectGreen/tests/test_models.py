import unittest
import datetime
import pytz
from django.test import TestCase
from django.contrib.auth.models import User
from projectGreen.models import Profile, Challenge, ActiveChallenge, Submission

class ProfileTestCase(TestCase):
    def setUp(self):
        user = User(username='js123', password='unsecure_password')
        user.save()
    
    def test_recalc_user_points(self):
        Profile.set_points_by_username('js123', 0)
        profile = Profile.objects.get(user__username='js123')
        profile.recalculate_user_points()
        self.assertEqual(profile.points, 0, 'inital points incorrect')
        profile.delete()

    def test_recalc_user_points_by_username(self):
        Profile.recalculate_user_points_by_username('js123')
        profile = Profile.objects.get(user__username='js123')
        self.assertEqual(profile.points, 0, 'inital points incorrect')
        profile.delete()

    def test_set_points(self):
        Profile.set_points_by_username('js123', 50)
        profile = Profile.objects.get(user__username='js123')
        self.assertEqual(profile.points, 50, 'set_points_by_username failed')
        profile.set_points(25)
        self.assertEqual(profile.points, 25, 'add_points failed')
    
    def test_add_points(self):
        Profile.set_points_by_username('js123', 0)
        Profile.add_points_by_username('js123', 10)
        profile = Profile.objects.get(user__username='js123')
        self.assertEqual(profile.points, 10, 'add_points_by_username failed')
        profile.add_points(10)
        self.assertEqual(profile.points, 20, 'add_points failed')


class ActiveChallengeTestCase(TestCase):
    def setUp(self):
        user = User(username='ab123', password='unsecure_password')
        user.save()
        challenge = Challenge(description='test challenge', time_for_challenge='20')
        challenge.save()
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC), challenge=challenge)
        activechallenge.save()
    
    
    def test_create_submission(self):
        activechallenge = ActiveChallenge.objects.get(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC))
        activechallenge.create_submission('ab123', datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC))
        submission = Submission.objects.get(username='ab123')
        self.assertEqual(submission.submission_time, datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), 'create_submission failed')


class SubmissionTestCase(TestCase):
    def setUp(self):
        user = User(username='ab123', password='unsecure_password')
        user.save()
        challenge = Challenge(description='test challenge', time_for_challenge='20')
        challenge.save()
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC), challenge=challenge)
        activechallenge.save()
        submission = Submission(username='ab123', active_challenge=activechallenge, submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC))
        submission.save()

    def test_get_minutes_late(self):
        submission = Submission.objects.get(username='ab123')
        minutes = submission.get_minutes_late()
        self.assertEqual(minutes, 15, 'get_minutes_late failed')
