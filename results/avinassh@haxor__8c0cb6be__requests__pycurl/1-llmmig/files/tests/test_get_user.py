#!/usr/bin/env python

"""
Tests get_user()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import datetime
import unittest
import pycurl
import io
import json

from hackernews import Item, User
from hackernews import InvalidUserID


class HackerNews:
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.curl = pycurl.Curl()

    def _make_request(self, endpoint):
        url = f"{self.BASE_URL}/{endpoint}.json"
        buffer = io.BytesIO()
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.WRITEDATA, buffer)
        self.curl.setopt(pycurl.FOLLOWLOCATION, True)
        self.curl.setopt(pycurl.FAILONERROR, True)

        try:
            self.curl.perform()
            response_code = self.curl.getinfo(pycurl.RESPONSE_CODE)
            if response_code != 200:
                raise InvalidUserID(f"HTTP error: {response_code}")
        except pycurl.error as e:
            raise InvalidUserID(f"Request failed: {e}")

        response_data = buffer.getvalue().decode("utf-8")
        return json.loads(response_data)

    def get_user(self, user_id, expand=False):
        user_data = self._make_request(f"user/{user_id}")
        if not user_data:
            raise InvalidUserID(f"User ID {user_id} not found")

        user = User(user_data)
        if expand:
            user.comments = [Item(self._make_request(f"item/{item_id}")) for item_id in user_data.get("submitted", [])]
            user.stories = [Item(self._make_request(f"item/{item_id}")) for item_id in user_data.get("submitted", [])]
        return user

    def close(self):
        self.curl.close()


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
