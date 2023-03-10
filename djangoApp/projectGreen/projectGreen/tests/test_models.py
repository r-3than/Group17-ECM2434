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
        self.assertEqual(submission.username, 'ab123', 'create_submission failed')

class SubmissionTestCase(TestCase):
    def setUp(self):
        user = User(username='ab123', password='unsecure_password')
        user.save()
        user = User(username='abc123', password='unsecure_password')
        user.save()
        user2 = User(username='bc123', password='unsecure_password')
        user2.save()
        user3 = User(username='cd123', password='unsecure_password')
        user3.save()
        challenge = Challenge(description='test challenge', time_for_challenge='20')
        challenge.save()
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC), challenge=challenge)
        activechallenge.save()
        submission = Submission(username='ab123', active_challenge=activechallenge, submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC))
        submission.save()
        submission2 = Submission(username='abc123', active_challenge=activechallenge, submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC))
        submission2.save()
        reported_submission = Submission(username='bc123', active_challenge=activechallenge, submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), reported=True)
        reported_submission.save()
        reviewed_submission = Submission(username='cd123', active_challenge=activechallenge, submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), reviewed=True)
        reviewed_submission.save()

    def test_get_minutes_late(self):
        submission = Submission.objects.get(username='ab123')
        minutes = submission.get_minutes_late()
        self.assertEqual(minutes, 15, 'get_minutes_late failed')
    
    def test_punctuality_scaling(self):
        submission = Submission.objects.get(username='ab123')
        scaled_points = submission.get_punctuality_scaling()
        self.assertEqual(scaled_points, 2)

    def test_report_submission(self):
        already_reported = Submission.objects.get(username='bc123')
        already_reported.report_submission()
        self.assertEqual(Submission.objects.get(username='bc123'), already_reported)

        already_reviewed = Submission.objects.get(username='cd123')
        already_reviewed.report_submission()
        self.assertEqual(Submission.objects.get(username='cd123'), already_reviewed)

        Profile.recalculate_user_points_by_username('ab123')
        profile = Profile.objects.get(user__username='ab123')
        submission = Submission.objects.get(username='ab123')
        submission.report_submission()
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, 0)
        assert(submission.reported)

    def test_review_submission(self):
        not_reported = Submission.objects.get(username='ab123')
        not_reported.review_submission(is_suitable=True)
        self.assertEqual(Submission.objects.get(username='ab123'), not_reported)
        assert(not not_reported.reported)

        already_reviewed = Submission.objects.get(username='cd123')
        already_reviewed.review_submission(is_suitable=True)
        self.assertEqual(Submission.objects.get(username='cd123'), already_reviewed)
        assert(not already_reviewed.reported)

        Profile.recalculate_user_points_by_username('ab123')
        profile = Profile.objects.get(user__username='ab123')
        submission = Submission.objects.get(username='ab123')
        submission.report_submission()
        profile = Profile.objects.get(user__username='ab123')
        submission.review_submission(is_suitable=True)
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, 20)
        assert(submission.reviewed)
        assert(not submission.reported)

        Profile.recalculate_user_points_by_username('abc123')
        profile = Profile.objects.get(user__username='abc123')
        submission = Submission.objects.get(username='abc123')
        submission.report_submission()
        profile = Profile.objects.get(user__username='abc123')
        submission.review_submission(is_suitable=False)
        profile = Profile.objects.get(user__username='abc123')
        self.assertEqual(profile.points, 0)
        self.assertEqual(profile.number_of_submissions_removed, 1)
        assert(submission.reviewed)
        assert(submission.reported)