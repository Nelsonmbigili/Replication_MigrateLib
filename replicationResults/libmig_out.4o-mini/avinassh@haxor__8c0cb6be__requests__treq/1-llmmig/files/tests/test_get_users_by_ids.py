#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import treq

from hackernews import HackerNews
from hackernews import User


class TestGetUsersByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_users_by_ids(self):
        users = self.hn.get_users_by_ids(['pg', 'tptacek', 'jacquesm'])
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    def tearDown(self):
        pass  # No need to close session in treq

if __name__ == '__main__':
    unittest.main()
