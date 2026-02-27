#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjke
"""

import unittest
import urllib3
import json

from hackernews import HackerNews


class HackerNews:
    def __init__(self):
        self.session = urllib3.PoolManager()

    def _run_async(self, urls):
        responses = []
        for url in urls:
            try:
                response = self.session.request('GET', url)
                if response.status == 200:
                    responses.append(json.loads(response.data.decode('utf-8')))
                else:
                    responses.append(None)
            except Exception:
                responses.append(None)
        return responses


class TestGetAsync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_async(self):
        response = self.hn._run_async([self.url])
        self.assertEqual(response[0]['id'], 8863)
        self.assertEqual(response[0]['by'], 'dhouston')

    def test_get_async_error(self):
        response = self.hn._run_async([self.err_url])
        self.assertEqual(response, [None])

    def tearDown(self):
        self.hn.session.clear()  # Close the PoolManager


if __name__ == '__main__':
    unittest.main()
