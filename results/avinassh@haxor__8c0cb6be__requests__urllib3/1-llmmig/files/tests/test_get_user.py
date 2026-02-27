#!/usr/bin/env python

"""
Tests get_user()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import datetime
import unittest
import urllib3

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidUserID


class HackerNews:
    """
    Modified HackerNews class to use urllib3 instead of requests.
    """
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.http = urllib3.PoolManager()

    def get_user(self, user_id, expand=False):
        url = f"{self.BASE_URL}/user/{user_id}.json"
        response = self.http.request("GET", url)
        if response.status != 200:
            raise InvalidUserID(f"User ID {user_id} is invalid or not found.")
        user_data = response.data.decode("utf-8")
        # Assuming User and Item are properly implemented to handle user_data
        user = User(user_data)
        if expand:
            user.expand_items(self.http)  # Assuming expand_items uses self.http for further requests
        return user

    def close(self):
        self.http.clear()


class TestGetUser(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_user(self):
        user = self.hn.get_user('pg')
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'pg')
        self.assertEqual(user.created,
                         datetime.datetime.fromtimestamp(1160418092))
        self.assertEqual(repr(user), '<hackernews.User: pg>')

    def test_get_invalid_user(self):
        self.assertRaises(InvalidUserID, self.hn.get_user, 'a')

    def test_get_user_expand(self):
        user = self.hn.get_user('avinassh', expand=True)
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'avinassh')
        self.assertIsInstance(user.comments[0], Item)
        self.assertIsInstance(user.stories[0], Item)

    def tearDown(self):
        self.hn.close()


if __name__ == '__main__':
    unittest.main()
