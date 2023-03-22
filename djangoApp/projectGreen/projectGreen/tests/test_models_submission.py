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

from projectGreen.models import Profile, Challenge, ActiveChallenge, Submission, Upvote, Comment, SCORES

class SubmissionTestCase(TestCase):
    def setUp(self):
        for username in ['ab123','abc123','bc123','cd123','ef123']:
            user = User(username=username, password='unsecure_password')
            user.save()
        challenge = Challenge(description='test challenge', time_for_challenge=20,
                                latitude=50.72228531721723, longitude=-3.531841571481125,
                                allowed_distance=20)
        challenge.save()
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC), challenge=challenge)
        activechallenge.save()
        with open("IMG_1379.JPG", "rb") as img:
            file = img.read()
            binary_image = bytearray(file)
            binary_image = bytearray(file)
        for username in ['ab123','abc123']:
            submission = Submission(username=username, active_challenge=activechallenge,
                                    submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC),
                                    photo_bytes=binary_image)
            submission.save()
        reported_submission = Submission(username='bc123', active_challenge=activechallenge,
                                        submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), reported=True, reported_by='ab123')
        reported_submission.save()
        reviewed_submission = Submission(username='cd123', active_challenge=activechallenge,
                                            submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), reviewed=True)
        reviewed_submission.save()

    def test_user_has_submitted(self):
        for username in ['ab123','abc123','bc123','cd123']:
            self.assertTrue(Submission.user_has_submitted(username), 'user submission not detected')
        self.assertFalse(Submission.user_has_submitted('ef123'))
        # add submission to an earlier ActiveChallenge
        challenge = Challenge.objects.get(description='test challenge')
        early_ac = ActiveChallenge(date=datetime.datetime(2023,3,9,9,30,0,0,pytz.UTC), challenge=challenge)
        early_ac.save()
        early_ac.create_submission('ef123',datetime.datetime(2023,3,9,9,50,0,0,pytz.UTC))
        self.assertFalse(Submission.user_has_submitted('ef123'))

    def test_is_for_active_challenge(self):
        submission = Submission.objects.get(username='ab123')
        self.assertTrue(submission.is_for_active_challenge(), 'is_for_active_challenge failed')

    def test_get_minutes_late(self):
        submission = Submission.objects.get(username='ab123')
        minutes = submission.get_minutes_late()
        self.assertEqual(minutes, 15, 'get_minutes_late failed')

    def test_get_punctuality_scaling(self):
        submission = Submission.objects.get(username='ab123')
        scaled_points = submission.get_punctuality_scaling()
        self.assertEqual(scaled_points, 2)
        submission_on_time = Submission(username='ef123', active_challenge=submission.active_challenge,
                                    submission_time=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC))
        self.assertEqual(submission_on_time.get_punctuality_scaling(), 5, 'on time scaling incorrect')
        submission_late = Submission(username='ef123', active_challenge=submission.active_challenge,
                                    submission_time=datetime.datetime(2023,3,9,10,30,0,0,pytz.UTC))
        self.assertEqual(submission_late.get_punctuality_scaling(), 1, 'late scaling incorrect')

    def test_report_submission(self):
        already_reported = Submission.objects.get(username='bc123')
        self.assertFalse(already_reported.report_submission('ab123'))
        self.assertEqual(Submission.objects.get(username='bc123'), already_reported)

        already_reviewed = Submission.objects.get(username='cd123')
        self.assertFalse(already_reviewed.report_submission('ab123'))
        self.assertEqual(Submission.objects.get(username='cd123'), already_reviewed)

        Profile.recalculate_user_points_by_username('ab123')
        submission = Submission.objects.get(username='ab123')
        submission.report_submission('bc123')
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, 0)
        self.assertTrue(submission.reported)
        self.assertEqual(submission.reported_by, 'bc123')

    def test_review_submission(self):
        not_reported = Submission.objects.get(username='ab123')
        self.assertFalse(not_reported.review_submission(is_suitable=True))
        self.assertEqual(Submission.objects.get(username='ab123'), not_reported)
        self.assertFalse(not_reported.reported)

        already_reviewed = Submission.objects.get(username='cd123')
        self.assertFalse(already_reviewed.review_submission(is_suitable=True))
        self.assertEqual(Submission.objects.get(username='cd123'), already_reviewed)
        self.assertFalse(already_reviewed.reported)

        # testing reporting and aproving submission
        Profile.recalculate_user_points_by_username('ab123')
        profile = Profile.objects.get(user__username='ab123')
        submission = Submission.objects.get(username='ab123')
        submission.report_submission('ef123')
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, 0)
        submission.review_submission(is_suitable=True)
        profile = Profile.objects.get(user__username='ef123')
        self.assertEqual(profile.number_of_false_reports, 1)
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling())
        self.assertTrue(submission.reviewed)
        self.assertFalse(submission.reported)

        # testing reporting and denying submission
        Profile.recalculate_user_points_by_username('abc123')
        profile = Profile.objects.get(user__username='abc123')
        submission = Submission.objects.get(username='abc123')
        submission.report_submission('ab123')
        profile = Profile.objects.get(user__username='abc123')
        self.assertEqual(profile.points, 0)
        submission.review_submission(is_suitable=False)
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.number_of_false_reports, 0)
        profile = Profile.objects.get(user__username='abc123')
        self.assertEqual(profile.points, 0)
        self.assertEqual(profile.number_of_submissions_removed, 1)
        self.assertTrue(submission.reviewed)
        self.assertTrue(submission.reported)

    def test_remove_submission(self):
        # Remove submission with delete_instance = False
        Profile.recalculate_user_points_by_username('ab123')
        not_reported = Submission.objects.get(username='ab123')
        not_reported.create_upvote('bc123') # Create upvote for the submission
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+SCORES['upvote']['recieved']) # Check profile points
        not_reported.remove_submission(delete_instance=False) # Remove submission
        self.assertEqual(not_reported.get_upvote_count(), 1) # Upvotes should not be deleted
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, 0) # Points should be removed

        # Remove submission with delete_instance = True
        Profile.recalculate_user_points_by_username('abc123')
        not_reported = Submission.objects.get(username='abc123')
        not_reported.create_upvote('bc123') # Create upvote for the submission
        profile = Profile.objects.get(user__username='abc123')
        sub = Submission.objects.get(username='abc123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+SCORES['upvote']['recieved']) # Check profile points
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
        reported.create_upvote('ab123') # Create upvote for the submission
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, sum(SCORES['upvote'].values())) # for receiving an upvote, and for upvoting another submission
        self.assertEqual(len(Submission.objects.all()), 3) # Check total number of submissions
        reported.remove_submission(delete_instance=False) # Remove submission
        self.assertEqual(reported.get_upvote_count(), 1) # Upvotes should not be deleted
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, sum(SCORES['upvote'].values())) # Points should be not change
        self.assertEqual(len(Submission.objects.all()), 3) # Check total number of submissions

        # Remove submission with reported flag set to True and delete_instance = True
        activechallenge = ActiveChallenge.objects.get(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC))
        reported = Submission(username='ef123', active_challenge=activechallenge, submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), reported=True)
        reported.save() # Create new reported submission (not removed)
        Profile.recalculate_user_points_by_username('ef123')
        reported = Submission.objects.get(username='ef123')
        Upvote(submission=reported, voter_username='ab123').save() # Create upvote for the submission
        profile = Profile.objects.get(user__username='ef123')
        self.assertEqual(profile.points, 0) # Submission reported - no points
        self.assertEqual(len(Submission.objects.all()), 4) # Check total number of submissions
        reported = Submission.objects.get(username='ef123')
        reported.remove_submission(delete_instance=True) # Remove submission
        self.assertEqual(len(Submission.objects.all()), 3) # Check total number of submissions
        profile = Profile.objects.get(user__username='ef123')
        self.assertEqual(profile.points, 0)

    def test_reinstate_submission(self):
        for username in ['ab123','bc123','cd123']:
            Profile.recalculate_user_points_by_username(username)
        submission = Submission.objects.get(username='ab123')
        submission.create_upvote('cd123')
        submission.create_upvote('bc123') # Create upvotes for the submission
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['upvote']['recieved']) # 2 upvotes recieved
        submission.report_submission('cd123')
        for username in ['ab123','bc123']:
            profile = Profile.objects.get(user__username=username)
            self.assertEqual(profile.points, 0)
        profile = Profile.objects.get(user__username='cd123')
        sub = Submission.objects.get(username='cd123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling())
        submission.reinstate_submission()

        # check residual scores
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['upvote']['recieved']) # Reinstated points
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, SCORES['upvote']['given'])
        profile = Profile.objects.get(user__username='cd123')
        sub = Submission.objects.get(username='cd123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+SCORES['upvote']['given'])

    def test_create_upvote(self):
        Profile.recalculate_user_points_by_username('ab123')
        submission = Submission.objects.get(username='ab123')
        self.assertTrue(submission.create_upvote('cd123')) # Create upvote
        self.assertEqual(submission.get_upvote_count(), 1)
        self.assertEqual(len(Upvote.objects.all()), 1) # Check upvote exists
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+SCORES['upvote']['recieved']) # Check received upvote points
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['upvote']['given']) # Check given upvote points

    def test_get_upvotes(self):
        submission = Submission.objects.get(username='ab123')
        submission.create_upvote('cd123')
        submission.create_upvote('bc123') # Create upvotes
        upvote1 = Upvote.objects.get(voter_username='cd123')
        upvote2 = Upvote.objects.get(voter_username='bc123')
        self.assertEqual(len(submission.get_upvotes()), 2)
        self.assertEqual(submission.get_upvotes()[0], upvote1)
        self.assertEqual(submission.get_upvotes()[1], upvote2)

    def test_get_upvote_count(self):
        submission = Submission.objects.get(username='ab123')
        submission.create_upvote('cd123')
        submission.create_upvote('bc123') # Create upvotes
        self.assertEqual(submission.get_upvote_count(), 2)

    def test_create_comment(self):
        Profile.recalculate_user_points_by_username('ab123')
        submission = Submission.objects.get(username='ab123')
        self.assertTrue(submission.create_comment('cd123', 'test comment')) # Create comment
        self.assertEqual(submission.get_comment_count(), 1)
        self.assertEqual(len(Comment.objects.all()), 1) # Check comment exists
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+SCORES['comment']['recieved']) # Check received comment points
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given']) # Check given upvote points

    def test_get_comments(self):
        submission = Submission.objects.get(username='ab123')
        submission.create_comment('bc123', 'test comment')
        submission.create_comment('cd123', 'another test comment') # Create comments
        submission.create_comment('ef123', '****, reported comment ')
        reported_comment = Comment.objects.get(comment_username='ef123')
        reported_comment.reported = True
        reported_comment.save()
        comments = submission.get_comments()
        self.assertEqual(1, len(comments.filter(comment_username='bc123')), 'missing comment')
        self.assertEqual(1, len(comments.filter(comment_username='cd123')), 'missing comment')
        self.assertEqual(0, len(comments.filter(comment_username='ef123')), 'fetched reported comment')
        self.assertEqual(len(comments), 2)

    def test_get_comment_count(self):
        submission = Submission.objects.get(username='ab123')
        submission.create_comment('bc123', 'test comment')
        submission.create_comment('cd123', 'another test comment') # Create comments
        submission.create_comment('ef123', '****, reported comment ')
        reported_comment = Comment.objects.get(comment_username='ef123')
        reported_comment.reported = True
        reported_comment.reported_by = 'ab123'
        reported_comment.save()
        self.assertEqual(submission.get_comment_count(), 2, 'get_comment_count failed')

    def test_location_is_valid(self):
        submission = Submission.objects.get(username='ab123')
        assert submission.location_is_valid()
        submission2 = Submission.objects.get(username='bc123')
        assert not submission2.location_is_valid()

    def test_location_check_missing_metadata(self):
        submission = Submission.objects.get(username='bc123')
        self.assertTrue(submission.location_check_missing_metadata('50.73473', '-3.533968'))
        self.assertFalse(submission.location_check_missing_metadata('55.94585', '-3.231052'))