#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import pycurl
from io import BytesIO
import json

from hackernews import HackerNews
from hackernews import HTTPError


class HackerNews:
    def _get_sync(self, url):
        """
        Perform a synchronous HTTP GET request using pycurl.
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.setopt(pycurl.FOLLOWLOCATION, True)
        curl.setopt(pycurl.TIMEOUT, 10)

        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            if status_code != 200:
                raise HTTPError(f"HTTP request failed with status code {status_code}")
        except pycurl.error as e:
            raise HTTPError(f"HTTP request failed: {e}")
        finally:
            curl.close()

        # Decode the response and parse JSON
        response_data = buffer.getvalue().decode('utf-8')
        return json.loads(response_data)


class TestGetSync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_sync(self):
        response = self.hn._get_sync(self.url)
        self.assertEqual(response['id'], 8863)
        self.assertEqual(response['by'], 'dhouston')

    def test_get_sync_error(self):
        self.assertRaises(HTTPError, self.hn._get_sync, self.err_url)

    def tearDown(self):
        pass  # No session to close when using pycurl


if __name__ == '__main__':
    unittest.main()
