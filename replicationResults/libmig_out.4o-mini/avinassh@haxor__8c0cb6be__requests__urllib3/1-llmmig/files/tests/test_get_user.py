#!/usr/bin/env python

"""
Tests get_user()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import datetime
import unittest
import urllib3
import json

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidUserID


class TestGetUser(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.http = urllib3.PoolManager()

    def test_get_user(self):
        response = self.hn.http.request('GET', f'https://hacker-news.firebaseio.com/v0/user/pg.json')
        user_data = json.loads(response.data.decode('utf-8'))
        user = self.hn.get_user(user_data)
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'pg')
        self.assertEqual(user.created,
                         datetime.datetime.fromtimestamp(1160418092))
        self.assertEqual(repr(user), '<hackernews.User: pg>')

    def test_get_invalid_user(self):
        self.assertRaises(InvalidUserID, self.hn.get_user, 'a')

    def test_get_user_expand(self):
        response = self.hn.http.request('GET', f'https://hacker-news.firebaseio.com/v0/user/avinassh.json')
        user_data = json.loads(response.data.decode('utf-8'))
        user = self.hn.get_user(user_data, expand=True)
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'avinassh')
        self.assertIsInstance(user.comments[0], Item)
        self.assertIsInstance(user.stories[0], Item)

    def tearDown(self):
        pass  # No need to close the PoolManager

if __name__ == '__main__':
    unittest.main()
