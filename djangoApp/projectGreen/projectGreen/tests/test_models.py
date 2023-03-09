import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from projectGreen.models import Profile

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
