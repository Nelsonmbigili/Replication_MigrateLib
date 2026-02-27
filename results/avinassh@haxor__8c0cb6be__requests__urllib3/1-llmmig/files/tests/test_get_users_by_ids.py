#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck
"""

import unittest
import urllib3

from hackernews import HackerNews
from hackernews import User


class TestGetUsersByIDs(unittest.TestCase):

    def setUp(self):
        # Initialize HackerNews with urllib3's PoolManager
        self.hn = HackerNews()
        self.hn.session = urllib3.PoolManager()

    def test_get_users_by_ids(self):
        users = self.hn.get_users_by_ids(['pg', 'tptacek', 'jacquesm'])
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    def tearDown(self):
        # Properly clean up the PoolManager
        self.hn.session.clear()

if __name__ == '__main__':
    unittest.main()
