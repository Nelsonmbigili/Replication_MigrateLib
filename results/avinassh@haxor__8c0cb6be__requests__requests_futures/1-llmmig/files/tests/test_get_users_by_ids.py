#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck
"""

import unittest
from requests_futures.sessions import FuturesSession  # Updated import for requests_futures

from hackernews import HackerNews
from hackernews import User


class TestGetUsersByIDs(unittest.TestCase):

    def setUp(self):
        # Assuming HackerNews uses a session internally, we ensure it uses FuturesSession
        self.hn = HackerNews(session=FuturesSession())  # Pass FuturesSession to HackerNews

    def test_get_users_by_ids(self):
        users = self.hn.get_users_by_ids(['pg', 'tptacek', 'jacquesm'])
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    def tearDown(self):
        self.hn.session.close()  # Close the FuturesSession

if __name__ == '__main__':
    unittest.main()
