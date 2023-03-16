'''
Main Authors:
    TN - Profile, Friend and Comment tests; code review
    LB - Challenge, ActiveChallenge, Submission and Upvote tests
'''

import unittest
import datetime
import pytz
from django.test import TestCase
from django.contrib.auth.models import User
from projectGreen.models import Profile, Friend, Challenge, ActiveChallenge, Submission, Upvote, Comment, SCORES, WORDS_TO_FILTER

class ProfileTestCase(TestCase):
    def setUp(self):
        user = User(username='js123', password='unsecure_password')
        user.save()

    def test_user_data(self):
        pass
    
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

    def test_get_profile(self):
        pass

class FriendTestCase(TestCase):
    def setUp(self):
        for un in ['ab123','abc123','bc123']:
            user = User(username=un, password='unsecure_password')
            user.save()
        pending_friend = Friend(left_username='ab123',right_username='abc123',pending=True)
        pending_friend.save() # from ab123 to abc123
        friend = Friend(left_username='ab123',right_username='bc123',pending=False)
        friend.save()

    def test_get_pending_friends(self):
        pending_friend_usernames = Friend.get_pending_friend_usernames('abc123')
        self.assertEqual(['ab123'], pending_friend_usernames)
        pending_friend_usernames = Friend.get_pending_friend_usernames('ab123')
        self.assertEqual([], pending_friend_usernames)

    def test_get_friends(self):
        friend_usernames = Friend.get_friend_usernames('ab123')
        self.assertEqual(['bc123'], friend_usernames)

    def test_create_friend_request(self):
        # attempts to create friend connection between non-existient users
        Friend.create_friend_request('cd123','ef123')
        with self.assertRaises(Friend.DoesNotExist, msg='invalid connection created - neither user exists'):
            Friend.objects.get(left_username='cd123',right_username='ef123')
        with self.assertRaises(Friend.DoesNotExist, msg='invalid connection created - neither user exists'):
            Friend.objects.get(left_username='ef123',right_username='cd123')
        # attempts to create friend connection between existient and non-existient users
        Friend.create_friend_request('ab123','ef123')
        with self.assertRaises(Friend.DoesNotExist, msg='invalid connection created - to non-existient user'):
            Friend.objects.get(left_username='ab123',right_username='ef123')
        with self.assertRaises(Friend.DoesNotExist, msg='invalid connection created - to non-existient user (reverse)'):
            Friend.objects.get(left_username='ef123',right_username='ab123')
        # reverse direction
        Friend.create_friend_request('ef123','ab123')
        with self.assertRaises(Friend.DoesNotExist, msg='invalid connection created - from non-existient user (reverse)'):
            Friend.objects.get(left_username='ab123',right_username='ef123')
        with self.assertRaises(Friend.DoesNotExist, msg='invalid connection created - from non-existient user'):
            Friend.objects.get(left_username='ef123',right_username='ab123')

        # removes manual friend reqest (from setUp)
        f = Friend.objects.get(left_username='ab123',right_username='abc123')
        f.delete()
        self.assertEqual([], Friend.get_pending_friend_usernames('ab123'))
        self.assertEqual([], Friend.get_pending_friend_usernames('abc123'))
        
        # creates friend request using class method and accepts
        Friend.create_friend_request('ab123','abc123')
        f = Friend.objects.get(left_username='ab123',right_username='abc123')
        f.pending = False
        f.save()
        self.assertEqual([], Friend.get_pending_friend_usernames('ab123'), 'residual friend request')
        self.assertEqual([], Friend.get_pending_friend_usernames('abc123'), 'residual friend request')
        self.assertEqual(['bc123','abc123'], Friend.get_friend_usernames('ab123'), 'ab123 friend list incorrect')
        self.assertEqual(['ab123'], Friend.get_friend_usernames('abc123'), 'abc123 friend list incorrect')
        self.assertEqual(['ab123'], Friend.get_friend_usernames('bc123'), 'bc123 friend list incorrect')

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
        c = Challenge.objects.get(description='test challenge')
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,30,0,0,pytz.UTC), challenge=c)
        activechallenge.save() # latest challenge
        activechallenge2 = ActiveChallenge(date=datetime.datetime(2023,3,9,10,10,0,0,pytz.UTC), challenge=c)
        activechallenge2.save()
        latest_challenge = ActiveChallenge.get_last_active_challenge()
        self.assertEqual(activechallenge, latest_challenge)
        c = Challenge(description='second test challenge', time_for_challenge=10)
        c.save() # introducing another challenge
        activechallenge3 = ActiveChallenge(date=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), challenge=c)
        activechallenge3.save()
        latest_challenge = ActiveChallenge.get_last_active_challenge()
        self.assertEqual(activechallenge, latest_challenge)
        activechallenge4 = ActiveChallenge(date=datetime.datetime(2023,3,9,10,45,0,0,pytz.UTC), challenge=c)
        activechallenge4.save() # new latest
        latest_challenge = ActiveChallenge.get_last_active_challenge()
        self.assertEqual(activechallenge4, latest_challenge)

    def test_get_challenge_description(self):
        activechallenge = ActiveChallenge.objects.get(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC))
        self.assertEqual('test challenge', activechallenge.get_challenge_description())

class SubmissionTestCase(TestCase):
    def setUp(self):
        for un in ['ab123','abc123','bc123','cd123','ef123']:
            user = User(username=un, password='unsecure_password')
            user.save()
        challenge = Challenge(description='test challenge', time_for_challenge=20)
        challenge.save()
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC), challenge=challenge)
        activechallenge.save()
        for un in ['ab123','abc123']:
            submission = Submission(username=un, active_challenge=activechallenge,
                                    submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC))
            submission.save()
        reported_submission = Submission(username='bc123', active_challenge=activechallenge,
                                        submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), reported=True, reported_by='ab123')
        reported_submission.save()
        reviewed_submission = Submission(username='cd123', active_challenge=activechallenge,
                                            submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC), reviewed=True)
        reviewed_submission.save()

    def test_user_has_submitted(self):
        for un in ['ab123','abc123','bc123','cd123']:
            self.assertTrue(Submission.user_has_submitted(un), 'user submission not detected')
        self.assertFalse(Submission.user_has_submitted('ef123'))
        # add submission to an earlier ActiveChallenge
        c = Challenge.objects.get(description='test challenge')
        early_ac = ActiveChallenge(date=datetime.datetime(2023,3,9,9,30,0,0,pytz.UTC), challenge=c)
        early_ac.save()
        early_ac.create_submission('ef123',datetime.datetime(2023,3,9,9,50,0,0,pytz.UTC))
        self.assertFalse(Submission.user_has_submitted('ef123'))

    def test_get_minutes_late(self):
        submission = Submission.objects.get(username='ab123')
        minutes = submission.get_minutes_late()
        self.assertEqual(minutes, 15, 'get_minutes_late failed')
    
    def test_punctuality_scaling(self):
        submission = Submission.objects.get(username='ab123')
        scaled_points = submission.get_punctuality_scaling()
        self.assertEqual(scaled_points, 2)
        submission_on_time = Submission(username='ef123', active_challenge=submission.active_challenge,
                                    submission_time=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC))
        self.assertEqual(submission_on_time.get_punctuality_scaling(), 5)
        submission_late = Submission(username='ef123', active_challenge=submission.active_challenge,
                                    submission_time=datetime.datetime(2023,3,9,10,30,0,0,pytz.UTC))
        self.assertEqual(submission_late.get_punctuality_scaling(), 1)

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
        for un in ['ab123','bc123','cd123']:
            Profile.recalculate_user_points_by_username(un)
        submission = Submission.objects.get(username='ab123')
        submission.create_upvote('cd123')
        submission.create_upvote('bc123') # Create upvotes for the submission
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['upvote']['recieved']) # 2 upvotes recieved
        submission.report_submission('cd123')
        for un in ['ab123','bc123']:
            profile = Profile.objects.get(user__username=un)
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

class UpvoteTestCase(TestCase):
    def setUp(self):
        for un in ['ab123','bc123','cd123']:
            user = User(username=un, password='unsecure_password')
            user.save()
        challenge = Challenge(description='test challenge', time_for_challenge=20)
        challenge.save()
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC), challenge=challenge)
        activechallenge.save()
        submission = Submission(username='ab123', active_challenge=activechallenge, submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC))
        submission.save()
        for un in ['bc123','cd123']:
            submission.create_upvote(un)

    def test_remove_upvote(self):
        for un in ['ab123','bc123','cd123']:
            Profile.recalculate_user_points_by_username(un)
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['upvote']['recieved'])
        for un in ['bc123','cd123']:
            profile = Profile.objects.get(user__username=un)
            self.assertEqual(profile.points, SCORES['upvote']['given'])
        self.assertEqual(len(Upvote.objects.all()), 2)

        # Remove upvote with delete_instance = False
        upvote = Upvote.objects.get(voter_username='bc123')
        upvote.remove_upvote(delete_instance=False)
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+SCORES['upvote']['recieved']) # Points should be removed
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, 0)
        self.assertEqual(len(Upvote.objects.all()), 2) # Upvote should still exist

        # Remove upvote with delete_instance = True
        upvote = Upvote.objects.get(voter_username='cd123')
        upvote.remove_upvote(delete_instance=True)
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()) # Points should be removed
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
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+SCORES['upvote']['recieved']) # Points should be removed
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, 0)
        upvote.reinstate_upvote()
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['upvote']['recieved']) # Points should be reinstated
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, SCORES['upvote']['given'])

class CommentTestCase(TestCase):
    def setUp(self):
        for un in ['ab123','bc123','cd123','ef123']:
            user = User(username=un, password='unsecure_password')
            user.save()
        challenge = Challenge(description='test challenge', time_for_challenge=20)
        challenge.save()
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC), challenge=challenge)
        activechallenge.save()
        submission = Submission(username='ab123', active_challenge=activechallenge, submission_time=datetime.datetime(2023,3,9,10,15,0,0,pytz.UTC))
        submission.save()
        submission.create_comment('bc123', 'test comment')
        submission.create_comment('cd123', 'this is a reviewed comment')
        c = Comment.objects.get(comment_username='cd123')
        c.reviewed = True
        c.save()
        submission.create_comment('ef123', 'this is a reported commment')
        c = Comment.objects.get(comment_username='ef123')
        c.reported = True
        c.reported_by = 'ab123'
        c.save()

    def test_report_comment(self):
        Profile.recalculate_user_points_by_username('ab123')
        profile = Profile.objects.get(user__username='ab123')
        sub = Submission.objects.get(username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*sub.get_punctuality_scaling()+2*SCORES['comment']['recieved']) # inital points check
        self.assertEqual(2, sub.get_comment_count())

        Profile.recalculate_user_points_by_username('ef123')
        already_reported = Comment.objects.get(comment_username='ef123')
        self.assertTrue(already_reported.reported)
        # attempt to report
        self.assertFalse(already_reported.report_comment('ab123'))
        profile = Profile.objects.get(user__username='ef123')
        self.assertEqual(profile.points, 0) # no points for reported comment

        already_reviewed = Comment.objects.get(comment_username='cd123')
        # attempt to report a reviewed comment
        self.assertFalse(already_reviewed.report_comment('ab123'))
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given'])
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, SCORES['comment']['given'])
        # points for unreported/reviewed comment

        # reporting valid comment
        Profile.recalculate_user_points_by_username('bc123')
        comment = Comment.objects.get(comment_username='bc123')
        comment.report_comment('ab123')
        profile = Profile.objects.get(user__username='bc123')
        self.assertEqual(profile.points, 0)
        self.assertTrue(comment.reported)
        self.assertEqual(comment.reported_by, 'ab123')

        ## repeat for reported submission
        

    def test_review_comment(self):
        already_reviewed = Comment.objects.get(comment_username='cd123')
        # attempt to review comment after review
        self.assertFalse(already_reviewed.review_comment(True))
        self.assertFalse(already_reviewed.review_comment(False))
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given'])

        # reviewing valid comment with is_suitable = True
        comment = Comment.objects.get(comment_username='ef123')
        reporting_username = comment.reported_by
        self.assertTrue(comment.reported)
        self.assertTrue(comment.review_comment(True))
        profile = Profile.objects.get(user__username=reporting_username)
        self.assertEqual(profile.number_of_false_reports, 1)
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
        self.assertEqual(1, profile.number_of_comments_removed)

        sub = Submission.objects.get(username='ab123')
        self.assertEqual(2, sub.get_comment_count())

        ## repeat for reported submission

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
        
        Profile.recalculate_user_points_by_username('ab123')


    def test_reinstate_comment(self):
        pass
    
    def test_inappropriate_language_filter(self):
        Profile.recalculate_user_points_by_username('ab123')
        Profile.recalculate_user_points_by_username('cd123')
        submission = Submission.objects.get(username='ab123')
        self.assertEqual(2, submission.get_comment_count(), 'incorrect inital comment count')
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*submission.get_punctuality_scaling()+2*SCORES['comment']['recieved'])
        # attempt to create comment containing profane language
        inappropriate_comment = ''.join([WORDS_TO_FILTER[i] for i in [16, 32, 64]])
        self.assertFalse(submission.create_comment('cd123', inappropriate_comment))
        self.assertEqual(2, submission.get_comment_count()) # only non-reported fetched
        comment = Comment.objects.get(comment_username='cd123', content=inappropriate_comment)
        self.assertTrue(comment.reported)
        self.assertEqual(0, len(submission.get_comments().filter(comment_username='cd123', content=inappropriate_comment)))
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, SCORES['submission']*submission.get_punctuality_scaling()+2*SCORES['comment']['recieved'])
        profile = Profile.objects.get(user__username='cd123')
        self.assertEqual(profile.points, SCORES['comment']['given']) # only points for one comment