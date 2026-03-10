#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import pycurl
from io import BytesIO
from hackernews import HackerNews
from hackernews import User


class TestGetUsersByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_users_by_ids(self):
        # Prepare a buffer to capture the response
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/user/pg.json')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        # Decode the response
        response = buffer.getvalue().decode('utf-8')
        users = [response]  # This is a placeholder; actual implementation will vary

        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    def tearDown(self):
        pass  # No session to close in pycurl

if __name__ == '__main__':
    unittest.main()
