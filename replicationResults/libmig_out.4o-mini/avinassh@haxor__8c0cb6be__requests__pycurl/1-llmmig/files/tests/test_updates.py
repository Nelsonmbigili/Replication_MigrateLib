#!/usr/bin/env python

"""
Tests updates()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import pycurl
from io import BytesIO
from hackernews import HackerNews


class TestUpdates(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_top_stories(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.hn.api_url + '/updates')  # Assuming api_url is defined in HackerNews
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        response_data = buffer.getvalue()
        updates = json.loads(response_data.decode('utf-8'))  # Assuming the response is JSON
        self.assertIsNotNone(updates)
        self.assertIsInstance(updates, dict)
        self.assertIsInstance(updates['profiles'], list)
        self.assertIsInstance(updates['items'], list)

    def tearDown(self):
        pass  # No session to close with pycurl

if __name__ == '__main__':
    unittest.main()
