import unittest
import datetime
import pytz
from django.test import TestCase
from django.contrib.auth.models import User
from projectGreen.models import Profile, Challenge, ActiveChallenge, Submission, Upvote

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
        user4 = User(username='ef123', password='unsecure_password')
        user4.save()
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

    def test_remove_submission(self):
        # Remove submission with delete_instance = False
        Profile.recalculate_user_points_by_username('ab123')
        not_reported = Submission.objects.get(username='ab123')
        not_reported.create_upvote(voter_username='bc123') # Create upvote for the submission
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, 22) # Check profile points
        not_reported.remove_submission(delete_instance=False) # Remove submission
        self.assertEqual(not_reported.get_upvote_count(), 1) # Upvotes should not be deleted
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, 0) # Points should be removed

        # Remove submission with delete_instance = True
        Profile.recalculate_user_points_by_username('abc123')
        not_reported = Submission.objects.get(username='abc123')
        not_reported.create_upvote(voter_username='bc123') # Create upvote for the submission
        profile = Profile.objects.get(user__username='abc123')
        self.assertEqual(profile.points, 22) # Check profile points
        self.assertEqual(len(Submission.objects.all()), 4) # Check total number of submissions
        not_reported = Submission.objects.get(username='abc123')
        not_reported.remove_submission(delete_instance=True) # Remove submission
        self.assertEqual(not_reported.get_upvote_count(), 0) # Upvotes should be deleted
        profile = Profile.objects.get(user__username='abc123')
        self.assertEqual(profile.points, 0) # Points should be removed
        self.assertEqual(len(Submission.objects.all()), 3) # Check total number of submissions

        # Remove submission with reported flag set to True and delete_instance = False
        Profile.recalculate_user_points_by_username('bc123')
        reported = Submission.objects.get(username='bc123')
        reported.create_upvote(voter_username='ab123') # Create upvote for the submission
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, 3) # 2pt for receiving an upvote, 1pt for upvoting another submission
        self.assertEqual(len(Submission.objects.all()), 3) # Check total number of submissions
        reported.remove_submission(delete_instance=False) # Remove submission
        self.assertEqual(reported.get_upvote_count(), 1) # Upvotes should not be deleted
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, 3) # Points should be not be removed
        self.assertEqual(len(Submission.objects.all()), 3) # Check total number of submissions

        # Remove submission with reported flag set to True and delete_instance = True
        activechallenge = ActiveChallenge.objects.get(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC))
        reported = Submission(username='ef123', active_challenge=activechallenge, submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), reported=True)
        reported.save() # Create new reported submission (not removed)
        
        Profile.recalculate_user_points_by_username('ef123')
        reported = Submission.objects.get(username='ef123')
        reported.create_upvote(voter_username='ab123') # Create upvote for the submission
        profile = Profile.objects.get(user__username='ef123')
        self.assertEqual(profile.points, 2) # Submission reported - only 2pts for upvote
        self.assertEqual(len(Submission.objects.all()), 4) # Check total number of submissions
        reported = Submission.objects.get(username='ef123')
        reported.remove_submission(delete_instance=True) # Remove submission
        self.assertEqual(len(Submission.objects.all()), 3) # Check total number of submissions
        Profile.recalculate_user_points_by_username('ef123')
        profile = Profile.objects.get(user__username='ef123')
        self.assertEqual(profile.points, 0) # Points should be removed

    def test_reinstate_submission(self):
        Profile.recalculate_user_points_by_username('ab123')
        submission = Submission.objects.get(username='ab123')
        submission.create_upvote(voter_username='bc123') # Create upvote for the submission

        profile = Profile.objects.get(user__username='ab123')
        #self.assertEqual(profile.points, 22)
        #print("upvotes: ", submission.get_upvote_count())

        submission.report_submission()

        profile = Profile.objects.get(user__username='ab123')
        #print("points: ", profile.points)
        profile = Profile.objects.get(user__username='ab123')
        #self.assertEqual(profile.points, 0)
        submission.reviewed = True
        submission.reinstate_submission()
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, 22) 