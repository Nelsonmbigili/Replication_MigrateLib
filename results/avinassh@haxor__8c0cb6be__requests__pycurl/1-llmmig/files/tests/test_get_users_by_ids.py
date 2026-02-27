#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjke
"""

import unittest
import pycurl
import io
import json


class User:
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.created = user_data.get('created')
        self.karma = user_data.get('karma')
        self.about = user_data.get('about')


class HackerNews:
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        pass  # No session needed for pycurl

    def _make_request(self, endpoint):
        """
        Helper method to make an HTTP GET request using pycurl.
        """
        buffer = io.BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, f"{self.BASE_URL}/{endpoint}.json")
        curl.setopt(curl.WRITEFUNCTION, buffer.write)
        curl.setopt(curl.FOLLOWLOCATION, True)
        curl.setopt(curl.USERAGENT, "pycurl/7.45.6")
        curl.perform()
        curl.close()

        # Decode the response
        response_data = buffer.getvalue().decode('utf-8')
        return json.loads(response_data)

    def get_users_by_ids(self, user_ids):
        """
        Fetch user details for a list of user IDs.
        """
        users = []
        for user_id in user_ids:
            user_data = self._make_request(f"user/{user_id}")
            if user_data:
                users.append(User(user_data))
        return users


class TestGetUsersByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_users_by_ids(self):
        users = self.hn.get_users_by_ids(['pg', 'tptacek', 'jacquesm'])
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    def tearDown(self):
        pass  # No session to close for pycurl


if __name__ == '__main__':
    unittest.main()
