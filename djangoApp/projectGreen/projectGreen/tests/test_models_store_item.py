'''
Main author:
    LB
Code-Review:

'''

from django.test import TestCase
from django.contrib.auth.models import User

from projectGreen.models import StoreItem


class StoreItemTestCase(TestCase):
    def setUp(self):
        new_item = StoreItem(item_name="test_item", cost=100)
        new_item.save()

    def test_get_item_cost(self):
        self.assertEqual(StoreItem.get_item_cost("test_item"), 100)
        #not_real = 