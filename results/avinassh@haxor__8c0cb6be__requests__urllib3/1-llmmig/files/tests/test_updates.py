#!/usr/bin/env python

"""
Tests updates()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import urllib3
import json


class HackerNews:
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.http = urllib3.PoolManager()

    def updates(self):
        url = f"{self.BASE_URL}/updates.json"
        response = self.http.request("GET", url)
        if response.status == 200:
            return json.loads(response.data.decode('utf-8'))
        else:
            response.raise_for_status()

    def close(self):
        self.http.clear()


class TestUpdates(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_top_stories(self):
        updates = self.hn.updates()
        self.assertIsNotNone(updates)
        self.assertIsInstance(updates, dict)
        self.assertIsInstance(updates['profiles'], list)
        self.assertIsInstance(updates['items'], list)

    def tearDown(self):
        self.hn.close()


if __name__ == '__main__':
    unittest.main()
