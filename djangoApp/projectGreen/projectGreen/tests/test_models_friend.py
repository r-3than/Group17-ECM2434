'''
Main Author:
    TN
Code-Review:
    LB
'''

from django.test import TestCase
from django.contrib.auth.models import User

from projectGreen.models import Friend

class FriendTestCase(TestCase):
    def setUp(self):
        for username in ['ab123','abc123','bc123']:
            user = User(username=username, password='unsecure_password')
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
        friendship = Friend.objects.get(left_username='ab123',right_username='abc123')
        friendship.delete()
        self.assertEqual([], Friend.get_pending_friend_usernames('ab123'))
        self.assertEqual([], Friend.get_pending_friend_usernames('abc123'))

        # creates friend request using class method and accepts
        Friend.create_friend_request('ab123','abc123')
        friendship = Friend.objects.get(left_username='ab123',right_username='abc123')
        friendship.pending = False
        friendship.save()
        self.assertEqual([], Friend.get_pending_friend_usernames('ab123'), 'residual friend request')
        self.assertEqual([], Friend.get_pending_friend_usernames('abc123'), 'residual friend request')
        self.assertEqual(['bc123','abc123'], Friend.get_friend_usernames('ab123'), 'ab123 friend list incorrect')
        self.assertEqual(['ab123'], Friend.get_friend_usernames('abc123'), 'abc123 friend list incorrect')
        self.assertEqual(['ab123'], Friend.get_friend_usernames('bc123'), 'bc123 friend list incorrect')

    def test_accept_friend_request(self):
        # should fail when valid users are already friends
        Friend.create_friend_request('ab123','abc123')
        friendship = Friend.objects.get(left_username='ab123',right_username='abc123')
        friendship.pending = False
        friendship.save()
        Friend.accept_friend_request('ab123','abc123')
        self.assertFalse(friendship.pending)
        friendship.delete()

        # should succeed when valid friend request exists
        Friend.create_friend_request('ab123','abc123')
        friendship = Friend.objects.get(left_username='ab123',right_username='abc123')
        friendship.pending = True
        friendship.save()
        Friend.accept_friend_request('ab123','abc123')
        friendship = Friend.objects.get(left_username='ab123',right_username='abc123')
        self.assertEqual(friendship.pending, False)
        self.assertEqual([], Friend.get_pending_friend_usernames('ab123'), 'residual friend request')
        self.assertEqual([], Friend.get_pending_friend_usernames('abc123'), 'residual friend request')
        self.assertEqual(['bc123','abc123'], Friend.get_friend_usernames('ab123'), 'ab123 friend list incorrect')
        self.assertEqual(['ab123'], Friend.get_friend_usernames('abc123'), 'abc123 friend list incorrect')
        friendship.delete()

    def test_decline_friend_request(self):
        # should fail when valid users are already friends
        Friend.create_friend_request('ab123','abc123')
        friendship = Friend.objects.get(left_username='ab123',right_username='abc123')
        friendship.pending = False
        friendship.save()
        Friend.decline_friend_request('ab123','abc123')
        self.assertFalse(friendship.pending)
        friendship.delete()

        # should succeed when valid friend request exists
        Friend.create_friend_request('ab123','abc123')
        friendship = Friend.objects.get(left_username='ab123',right_username='abc123')
        friendship.pending = True
        friendship.save()
        Friend.decline_friend_request('ab123','abc123')
        with self.assertRaises(Friend.DoesNotExist, msg='friend request not removed'):
            Friend.objects.get(left_username='ab123',right_username='abc123')
        self.assertEqual([], Friend.get_pending_friend_usernames('ab123'), 'residual friend request')
        self.assertEqual([], Friend.get_pending_friend_usernames('abc123'), 'residual friend request')
        self.assertEqual(['bc123'], Friend.get_friend_usernames('ab123'), 'ab123 friend list incorrect')
        self.assertEqual([], Friend.get_friend_usernames('abc123'), 'abc123 friend list incorrect')
        friendship.delete()

    def test_remove_friend(self):
        # should succeed when valid friend request exists
        Friend.create_friend_request('ab123','abc123')
        friendship = Friend.objects.get(left_username='ab123',right_username='abc123')
        friendship.pending = False
        friendship.save()
        Friend.remove_friend('ab123','abc123')
        with self.assertRaises(Friend.DoesNotExist, msg='friendship shouldn\'t exist'):
            friendship = Friend.objects.get(left_username='ab123',right_username='abc123')
        with self.assertRaises(Friend.DoesNotExist, msg='friendship shouldn\'t exist'):
            friendship = Friend.objects.get(left_username='abc123',right_username='ab123')
        self.assertEqual(['bc123'], Friend.get_friend_usernames('ab123'), 'ab123 friend list incorrect')
        self.assertEqual([], Friend.get_friend_usernames('abc123'), 'abc123 friend list incorrect')
        friendship.delete()

        # should succeed when valid friend request exists (reverse)
        Friend.create_friend_request('ab123','abc123')
        friendship = Friend.objects.get(left_username='ab123',right_username='abc123')
        friendship.pending = False
        friendship.save()
        Friend.remove_friend('abc123','ab123')
        with self.assertRaises(Friend.DoesNotExist, msg='friendship shouldn\'t exist'):
            friendship = Friend.objects.get(left_username='ab123',right_username='abc123')
        with self.assertRaises(Friend.DoesNotExist, msg='friendship shouldn\'t exist'):
            friendship = Friend.objects.get(left_username='abc123',right_username='ab123')
        self.assertEqual(['bc123'], Friend.get_friend_usernames('ab123'), 'ab123 friend list incorrect')
        self.assertEqual([], Friend.get_friend_usernames('abc123'), 'abc123 friend list incorrect')
        friendship.delete()

        # Returns None when Friend object doesn't exist
        self.assertFalse(Friend.remove_friend('ab123','abc123'))
