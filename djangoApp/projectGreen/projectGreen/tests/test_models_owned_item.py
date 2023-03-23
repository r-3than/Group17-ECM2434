'''
Main author:
    LB
Code-Review:

'''

import io
from PIL import Image

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File

from projectGreen.models import StoreItem, OwnedItem


class OwnedItemTestCase(TestCase):
    def setUp(self):
        for username in ['ab123','abc123','bc123','cd123','ef123']:
            user = User(username=username, password='unsecure_password')
            user.save()
        new_store_item = StoreItem(item_name='test_item2', cost=100, text_colour='FFFFFF')
        new_store_item.photo = 'uploads/forest.jpg'
        new_store_item.save()
        new_item1 = OwnedItem(item_name='test_item1', username='ab123', is_active=False)
        new_item1.save()
        new_item2 = OwnedItem(item_name='test_item2', username='ab123', is_active=True)
        new_item2.save()

    def test_owns_item(self):
        self.assertTrue(OwnedItem.owns_item('test_item1', 'ab123'))
        self.assertTrue(OwnedItem.owns_item('test_item2', 'ab123'))

    def test_make_active(self):
        self.assertTrue(OwnedItem.make_active('test_item1', 'ab123'))
        self.assertTrue(OwnedItem.make_active('test_item2', 'ab123'))
        self.assertFalse(OwnedItem.make_active('test_item3', 'ab123'))

    def test_make_inactive(self):
        self.assertFalse(OwnedItem.make_inactive('test_item1', 'ab123'))
        self.assertTrue(OwnedItem.make_inactive('test_item2', 'ab123'))
        self.assertFalse(OwnedItem.make_inactive('test_item3', 'ab123'))

    def test_get_active_name(self):
        self.assertEqual(OwnedItem.get_active_name('ab123'), 'test_item2')
        self.assertEqual(OwnedItem.get_active_name('abc123'), '')

    def test_get_active_item_data(self):
        null_data = {'is_active': False, 'image': None, 'text': None}
        data = {'is_active': True, 'image': '/uploads/uploads/forest.jpg', 'text': '#FFFFFF'}
        self.assertEqual(OwnedItem.get_active_item_data('test_item1'), null_data)
        self.assertEqual(OwnedItem.get_active_item_data('ab123'), data)