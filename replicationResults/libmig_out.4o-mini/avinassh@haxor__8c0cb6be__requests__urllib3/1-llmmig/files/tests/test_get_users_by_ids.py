#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import urllib3
import json

from hackernews import HackerNews
from hackernews import User


class TestGetUsersByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.http = urllib3.PoolManager()

    def test_get_users_by_ids(self):
        user_ids = ['pg', 'tptacek', 'jacquesm']
        users = self.hn.get_users_by_ids(user_ids)
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
