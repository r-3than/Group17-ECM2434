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

from projectGreen.models import Profile, Friend, Challenge, ActiveChallenge, Submission, Upvote, Comment

class ProfileTestCase(TestCase):
    def setUp(self):
        user = User(username='ab123', password='unsecure_password')
        user.save()

    def test_user_data(self):
        user = User.objects.get(username='ab123')
        profile = Profile(user=user, points=100)
        data_empty = {
            'profile': [user, profile],
            'friends_set': set(),
            'submissions': set(),
            'upvotes': {
                'given': set(),
                'recieved': set()
            },
            'comments': {
                'given': set(),
                'recieved': set()
            }
        }
        u_data = profile.user_data()
        self.assertEqual(data_empty['profile'], u_data['profile'])
        self.assertSetEqual(data_empty['friends_set'], u_data['friends_set'])
        self.assertSetEqual(data_empty['submissions'], u_data['submissions'])
        self.assertSetEqual(data_empty['upvotes']['given'], u_data['upvotes']['given'])
        self.assertSetEqual(data_empty['upvotes']['recieved'], u_data['upvotes']['recieved'])
        self.assertSetEqual(data_empty['comments']['given'], u_data['comments']['given'])
        self.assertSetEqual(data_empty['comments']['recieved'], u_data['comments']['recieved'])

        # initialize env
        for username in ['bc123', 'cd123', 'ef123']: # extra users
            User(username=username, password='unsecure_password').save()
        challenge = Challenge(description='test challenge', time_for_challenge=20)
        challenge.save()
        activechallenge = ActiveChallenge(date=datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC), challenge=challenge)
        activechallenge.save()
        activechallenge.create_submission('ab123', datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC))
        activechallenge.create_submission('bc123', datetime.datetime(2023,3,9,10,0,0,0,pytz.UTC))

        # outgoing
        sub = Submission.objects.get(username='bc123')
        sub.create_upvote('ab123')
        up0 = Upvote.objects.get(voter_username='ab123')
        sub.create_comment('ab123', 'hello')
        c0 = Comment.objects.get(comment_username='ab123')

        # incoming
        sub = Submission.objects.get(username='ab123')
        sub.create_upvote('bc123')
        up1 = Upvote.objects.get(voter_username='bc123')
        sub.create_upvote('cd123')
        up2 = Upvote.objects.get(voter_username='cd123')
        sub.create_comment('cd123', 'hi ab123')
        c1 = Comment.objects.get(comment_username='cd123', content='hi ab123')
        sub.create_comment('cd123', 'i love your post')
        c2 = Comment.objects.get(comment_username='cd123', content='i love your post')

        # friends
        f1 = Friend(left_username='ab123', right_username='bc123')
        f1.save()
        f2 = Friend(left_username='cd123', right_username='ab123')
        f2.save()
        f3 = Friend(left_username='ab123', right_username='ef123', pending=True)
        f3.save()
        data_populated = {
            'profile': [user, profile],
            'friends_set': {f1, f2, f3},
            'submissions': {sub},
            'upvotes': {
                'given': {up0},
                'recieved': {up1, up2}
            },
            'comments': {
                'given': {c0},
                'recieved': {c1, c2}
            }
        }
        u_data = profile.user_data()
        self.assertEqual(data_populated['profile'], u_data['profile'], 'fetched profile/user incorrect')
        self.assertSetEqual(data_populated['friends_set'], u_data['friends_set'], 'fetched friends incorrect')
        self.assertSetEqual(data_populated['submissions'], u_data['submissions'], 'fetched submissions incorrect')
        self.assertSetEqual(data_populated['upvotes']['given'], u_data['upvotes']['given'], 'fetched given upvotes incorrect')
        self.assertSetEqual(data_populated['upvotes']['recieved'], u_data['upvotes']['recieved'], 'fetched recieved upvotes incorrect')
        self.assertSetEqual(data_populated['comments']['given'], u_data['comments']['given'], 'fetched given comments incorrect')
        self.assertSetEqual(data_populated['comments']['recieved'], u_data['comments']['recieved'], 'fetched recieved comments incorrect')

        # delete user
        profile.user_data(delete=True)
        with self.assertRaises(User.DoesNotExist, msg='user not deleted'):
            User.objects.get(username='ab123')

    def test_recalc_user_points(self):
        Profile.set_points_by_username('ab123', 0)
        profile = Profile.objects.get(user__username='ab123')
        profile.recalculate_user_points()
        self.assertEqual(profile.points, 0, 'inital points incorrect')
        profile.delete()

    def test_recalc_user_points_by_username(self):
        Profile.recalculate_user_points_by_username('ab123')
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, 0, 'inital points incorrect')
        profile.delete()

    def test_set_points(self):
        Profile.set_points_by_username('ab123', 50)
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, 50, 'set_points_by_username failed')
        profile.set_points(25)
        self.assertEqual(profile.points, 25, 'add_points failed')

    def test_add_points(self):
        Profile.set_points_by_username('ab123', 0)
        Profile.add_points_by_username('ab123', 10)
        profile = Profile.objects.get(user__username='ab123')
        self.assertEqual(profile.points, 10, 'add_points_by_username failed')
        profile.add_points(10)
        self.assertEqual(profile.points, 20, 'add_points failed')

    def test_get_profile(self):
        user = User.objects.get(username='ab123')
        profile = Profile(user=user)
        profile.save()
        self.assertEqual(profile, Profile.get_profile('ab123'))