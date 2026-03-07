#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
from requests_futures.sessions import FuturesSession
from hackernews import HackerNews


class TestGetAsync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Use FuturesSession for async requests
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_async(self):
        future = self.hn.session.get(self.url)  # Use get method of FuturesSession
        response = future.result()  # Get the result of the future
        self.assertEqual(response.json()['id'], 8863)
        self.assertEqual(response.json()['by'], 'dhouston')

    def test_get_async_error(self):
        future = self.hn.session.get(self.err_url)  # Use get method of FuturesSession
        response = future.result()  # Get the result of the future
        self.assertEqual(response, None)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
