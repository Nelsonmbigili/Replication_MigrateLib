#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
from requests_futures.sessions import FuturesSession  # Changed import

from hackernews import HackerNews
from hackernews import User


class TestGetUsersByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Changed to FuturesSession

    def test_get_users_by_ids(self):
        users_future = self.hn.get_users_by_ids(['pg', 'tptacek', 'jacquesm'])  # Assuming this method is updated to handle futures
        users = users_future.result()  # Get the result from the future
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
