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


class TestGetAsync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def _run_async(self, urls):
        responses = []
        for url in urls:
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.FOLLOWLOCATION, True)
            try:
                c.perform()
                response_code = c.getinfo(c.RESPONSE_CODE)
                if response_code == 200:
                    response_data = buffer.getvalue()
                    responses.append(json.loads(response_data))
                else:
                    responses.append(None)
            except Exception as e:
                responses.append(None)
            finally:
                c.close()
        return responses

    def test_get_async(self):
        response = self._run_async([self.url])
        self.assertEqual(response[0]['id'], 8863)
        self.assertEqual(response[0]['by'], 'dhouston')

    def test_get_async_error(self):
        response = self._run_async([self.err_url])
        self.assertEqual(response, [None])

    def tearDown(self):
        pass  # No session to close in pycurl

if __name__ == '__main__':
    unittest.main()
