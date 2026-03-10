#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import pycurl
import json
from io import BytesIO
from hackernews import HackerNews
from hackernews import HTTPError


class TestGetSync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def _get_sync(self, url):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.FOLLOWLOCATION, True)
        
        try:
            c.perform()
            response_code = c.getinfo(c.RESPONSE_CODE)
            if response_code != 200:
                raise HTTPError(f"HTTP Error: {response_code}")
        except pycurl.error as e:
            raise HTTPError(f"Request failed: {e}")
        finally:
            c.close()

        body = buffer.getvalue()
        return json.loads(body)

    def test_get_sync(self):
        response = self._get_sync(self.url)
        self.assertEqual(response['id'], 8863)
        self.assertEqual(response['by'], 'dhouston')

    def test_get_sync_error(self):
        self.assertRaises(HTTPError, self._get_sync, self.err_url)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
