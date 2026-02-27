#!/usr/bin/env python

"""
Tests updates()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import pycurl
from io import BytesIO
import json


class HackerNews:
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.curl = pycurl.Curl()

    def _make_request(self, endpoint):
        url = f"{self.BASE_URL}/{endpoint}.json"
        buffer = BytesIO()

        # Configure pycurl
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.setopt(pycurl.FOLLOWLOCATION, True)
        self.curl.setopt(pycurl.USERAGENT, "pycurl/7.45.6")

        # Perform the request
        self.curl.perform()

        # Get the response
        response_code = self.curl.getinfo(pycurl.RESPONSE_CODE)
        if response_code != 200:
            raise Exception(f"HTTP request failed with status code {response_code}")

        response_data = buffer.getvalue().decode("utf-8")
        return json.loads(response_data)

    def updates(self):
        return self._make_request("updates")

    def close(self):
        self.curl.close()


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
