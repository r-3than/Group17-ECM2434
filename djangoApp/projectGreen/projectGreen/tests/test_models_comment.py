'''
Main Author:
    TN
Code-Review:
    LB
'''

import datetime
import pytz

from django.test import TestCase
from django.contrib.auth.models import User

from projectGreen.models import Profile, Challenge, ActiveChallenge, Submission, Comment, SCORES, WORDS_TO_FILTER

class CommentTestCase(TestCase):
    def setUp(self):
        for username in ['ab123','bc123','cd123','ef123']:
            user = User(username=username, password='unsecure_password')
            user.save()
        challenge = Challenge(description='test challenge', time_for_challenge=20)
        challenge.save()
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC), challenge=challenge)
        activechallenge.save()
        submission = Submission(username='ab123', active_challenge=activechallenge, submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC))
        submission.save()
        submission.create_comment('bc123', 'test comment')
        comment = Comment(submission=submission, comment_username='cd123', content='this is a reviewed comment', reviewed=True)
        comment.save()
        comment = Comment(submission=submission, comment_username='ef123', content='this is a reported commment', reported=True, reported_by='ab123')
        comment.save()
        submission = Submission(username='cd123', active_challenge=activechallenge, submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), reported=True)
        submission.save()
        comment = Comment(submission=submission, comment_username='cd123', content='this is a another reviewed comment', reviewed=True)
        comment.save()
        comment = Comment(submission=submission, comment_username='ab123', content='this is a another reported commment', reported=True, reported_by='bc123')
        comment.save()
        for username in ['ab123', 'bc123', 'cd123']:
            Profile.recalculate_user_points_by_username(username)

    def test_report_comment(self):
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['comment']['recieved']) # inital points check
        self.assertEqual(2, sub.get_comment_count())

        Profile.recalculate_user_points_by_username('ef123')
        already_reported = Comment.objects.get(submission=sub, comment_username='ef123')
        self.assertTrue(already_reported.reported)
        # attempt to report
        self.assertFalse(already_reported.report_comment('ab123'), 'reported comment should not be reportable')
        profile = Profile.objects.get(user__username='ef123')
        self.assertEqual(profile.points, 0, 'reported comment should not give points') # no points for reported comment

        already_reviewed = Comment.objects.get(submission=sub, comment_username='cd123')
        # attempt to report a reviewed comment
        self.assertFalse(already_reviewed.report_comment('ab123'), 'reviewed comment should not be reportable')
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given'])
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, SCORES['comment']['given'])
        # points for unreported/reviewed comment

        # reporting valid comment
        Profile.recalculate_user_points_by_username('bc123')
        comment = Comment.objects.get(submission=sub, comment_username='bc123')
        comment.report_comment('ab123')
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, 0)
        self.assertTrue(comment.reported)
        self.assertEqual(comment.reported_by, 'ab123')

        ## repeat for reported submission

        sub = Submission.objects.get(username='cd123')
        already_reported = Comment.objects.get(submission=sub, comment_username='ab123')
        self.assertTrue(already_reported.reported)
        profile = Profile.objects.get(user__username='ab123')
        current_points = profile.points
        # attempt to report
        self.assertFalse(already_reported.report_comment('ef123'))
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, current_points, 'points desync') # points unchanged

        already_reviewed = Comment.objects.get(submission=sub, comment_username='cd123')
        # attempt to report a reviewed comment
        self.assertFalse(already_reviewed.report_comment('ef123'))
        # reporting valid comment
        comment = already_reviewed
        comment.reviewed = False
        comment.save()
        profile = Profile.objects.get(user__username='cd123')
        current_points = profile.points
        self.assertTrue(comment.report_comment('ab123'))
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, current_points) # points unchanged
        self.assertTrue(comment.reported)
        self.assertEqual(comment.reported_by, 'ab123')

    def test_review_comment(self):
        sub = Submission.objects.get(username='ab123')
        already_reviewed = Comment.objects.get(submission=sub, comment_username='cd123')
        # attempt to review comment after review
        self.assertFalse(already_reviewed.review_comment(True), 'reviewed comment should not be reviewable')
        self.assertFalse(already_reviewed.review_comment(False), 'reviewed comment should not be reviewable')
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given'], 'points desync')

        # reviewing valid comment with is_suitable = True
        comment = Comment.objects.get(submission=sub, comment_username='ef123')
        reporting_username = comment.reported_by
        self.assertTrue(comment.reported)
        self.assertTrue(comment.review_comment(True))
        profile = Profile.objects.get(user__username=reporting_username)
        self.assertEqual(profile.number_of_false_reports, 1, 'false report counter not incremented')
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given'])
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(3, sub.get_comment_count())
        # reviewing valid comment with is_suitable = False
        comment.reported = True
        comment.reviewed = False
        comment.save()
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(2, sub.get_comment_count())
        Profile.recalculate_user_points_by_username('ef123')
        profile = Profile.objects.get(user__username='ef123')
        self.assertEqual(profile.points, 0)
        self.assertEqual(0, profile.number_of_comments_removed) # comment not "removed" yet
        self.assertTrue(comment.review_comment(False))
        profile = Profile.objects.get(user__username='ef123')
        self.assertEqual(profile.points, 0)
        self.assertEqual(1, profile.number_of_comments_removed, 'removed comment counter not incremented')

        sub = Submission.objects.get(username='ab123')
        self.assertEqual(2, sub.get_comment_count())

        ## repeat for reported submission

        sub = Submission.objects.get(username='cd123')
        already_reviewed = Comment.objects.get(submission=sub, comment_username='cd123')
        # attempt to review comment after review
        self.assertFalse(already_reviewed.review_comment(True))
        self.assertFalse(already_reviewed.review_comment(False))
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given'])

        # reviewing valid comment with is_suitable = True
        self.assertEqual(1, sub.get_comment_count())
        profile = Profile.objects.get(user__username='ab123')
        current_points = profile.points
        comment = Comment.objects.get(submission=sub, comment_username='ab123')
        reporting_username = comment.reported_by
        self.assertTrue(comment.reported)
        self.assertTrue(comment.review_comment(True))
        profile = Profile.objects.get(user__username=reporting_username)
        self.assertEqual(profile.number_of_false_reports, 1)
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, current_points+SCORES['comment']['given'], 'points desync')
        sub = Submission.objects.get(username='cd123')
        self.assertEqual(2, sub.get_comment_count())
        # reviewing valid comment with is_suitable = False
        comment.reported = True
        comment.reviewed = False
        comment.save()
        self.assertEqual(1, sub.get_comment_count())
        Profile.recalculate_user_points_by_username('ab123')
        profile = Profile.objects.get(user__username='ab123')
        current_points = profile.points
        self.assertEqual(0, profile.number_of_comments_removed) # comment not "removed" yet
        self.assertTrue(comment.review_comment(False))
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(current_points, profile.points)
        self.assertEqual(1, profile.number_of_comments_removed, 'removed comment counter not incremented')

    def test_remove_comment(self):
        # remove comment with delete_instance = False
        Profile.recalculate_user_points_by_username('ab123')
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['comment']['recieved'])
        comment = Comment.objects.get(comment_username='bc123')
        comment.remove_comment(False)
        self.assertEqual(sub.get_comment_count(), 2) # comments should still exist
        # points should be removed
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+SCORES['comment']['recieved'])

        # remove comment with delete_instance = True
        Profile.recalculate_user_points_by_username('ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertTrue(sub.create_comment('bc123', 'another comment'))
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+3*SCORES['comment']['recieved'])
        comment = Comment.objects.get(comment_username='bc123', content='another comment')
        self.assertTrue(comment.remove_comment(True))
        self.assertEqual(sub.get_comment_count(), 2) # comments should be removed
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['comment']['recieved'])

        # remove reported comment with delete_instance = False
        Profile.recalculate_user_points_by_username('ab123')
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['comment']['recieved'])
        comment = Comment.objects.get(comment_username='ef123')
        comment.remove_comment(False)
        self.assertEqual(sub.get_comment_count(), 2) # comments should still exist
        # points should be unchanged
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['comment']['recieved'])

        # remove reported comment with delete_instance = True
        Profile.recalculate_user_points_by_username('ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertTrue(sub.create_comment('bc123', 'another comment'))
        comment = Comment.objects.get(comment_username='bc123', content='another comment')
        comment.report_comment('ef123')
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['comment']['recieved'])
        self.assertFalse(comment.remove_comment(True)) # points not removed so returns false
        self.assertEqual(sub.get_comment_count(), 2) # comments should be unchanged
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['comment']['recieved'])

        ## repeat for reported submission

        # remove comment with delete_instance = False
        sub = Submission.objects.get(username='cd123')
        sub.create_comment('ef123', 'test_remove_comment on reported submission')
        Profile.recalculate_user_points_by_username('cd123')
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given'])
        comment = Comment.objects.get(submission=sub, comment_username='ef123')
        self.assertFalse(comment.remove_comment(False))
        self.assertEqual(sub.get_comment_count(), 2) # comments should still exist
        # points should be removed
        profile = Profile.objects.get(user__username='cd123')
        sub = Submission.objects.get(username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given']) # points dont change as submision is reported

        # remove comment with delete_instance = True
        Profile.recalculate_user_points_by_username('cd123')
        sub = Submission.objects.get(username='cd123')
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given']) # points dont change as submision is reported
        comment = Comment.objects.get(submission=sub, comment_username='ef123')
        self.assertFalse(comment.remove_comment(True))
        self.assertEqual(sub.get_comment_count(), 1) # comments should be removed
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given']) # again, points unchanged

        # remove reported comment with delete_instance = False
        sub = Submission.objects.get(username='cd123')
        sub.create_comment('ef123', 'test_remove_comment on reported submission')
        comment = Comment.objects.get(submission=sub, comment_username='ef123')
        self.assertEqual(sub.get_comment_count(), 2)
        self.assertTrue(comment.report_comment('ab123'))
        self.assertEqual(sub.get_comment_count(), 1)
        Profile.recalculate_user_points_by_username('cd123')
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given'])
        self.assertFalse(comment.remove_comment(False))
        self.assertEqual(sub.get_comment_count(), 1)
        # points should be unchanged
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given']) # points should be unchanged

        # remove reported comment with delete_instance = True
        Profile.recalculate_user_points_by_username('cd123')
        sub = Submission.objects.get(username='cd123')
        self.assertFalse(comment.report_comment('ab123'))
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given']) # points dont change as submision is reported
        comment = Comment.objects.get(submission=sub, comment_username='ef123')
        self.assertFalse(comment.remove_comment(True))
        self.assertEqual(sub.get_comment_count(), 1) # comments should be removed
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given']) # again, points unchanged

    def test_reinstate_comment(self):
        for username in ['ab123','bc123','cd123','ef123']:
            Profile.recalculate_user_points_by_username(username)
        submission = Submission.objects.get(username='ab123')
        self.assertTrue(submission.report_submission('ab123'))
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, 0)
        for username in ['ab123','bc123','ef123']:
            profile = Profile.objects.get(user__username=username)
            self.assertEqual(profile.points, 0)
        comment = Comment.objects.get(comment_username='ef123')
        self.assertFalse(comment.reinstate_comment())
        profile = Profile.objects.get(user__username='ef123')
        self.assertEqual(profile.points, 0)
        comment = Comment.objects.get(comment_username='bc123')
        self.assertTrue(comment.reinstate_comment())
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, SCORES['comment']['given'])

    def test_inappropriate_language_filter(self):
        Profile.recalculate_user_points_by_username('ab123')
        Profile.recalculate_user_points_by_username('cd123')
        submission = Submission.objects.get(username='ab123')
        self.assertEqual(2, submission.get_comment_count(), 'incorrect inital comment count')
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*submission.get_punctuality_scaling()+2*SCORES['comment']['recieved'])
        # attempt to create comment containing profane language
        inappropriate_comment = ''.join([WORDS_TO_FILTER[i] for i in [8, 16, 32]])
        self.assertFalse(submission.create_comment('cd123', inappropriate_comment), 'profanity in comment was not flagged')
        self.assertEqual(2, submission.get_comment_count()) # only non-reported fetched
        comment = Comment.objects.get(comment_username='cd123', content=inappropriate_comment)
        self.assertTrue(comment.reported, 'inappropriate comment was not auto-reported')
        self.assertEqual(0, len(submission.get_comments().filter(comment_username='cd123', content=inappropriate_comment)))
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*submission.get_punctuality_scaling()+2*SCORES['comment']['recieved'])
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given'], 'points should not be assigned for reported comment') # only points for one comment
