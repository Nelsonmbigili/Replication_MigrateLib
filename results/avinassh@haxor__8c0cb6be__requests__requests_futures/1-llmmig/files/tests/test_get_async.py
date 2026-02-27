#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck
"""

import unittest
from requests_futures.sessions import FuturesSession  # Updated import
from hackernews import HackerNews


class HackerNews:
    def __init__(self):
        self.session = FuturesSession()  # Use FuturesSession for async requests

    def _run_async(self, urls):
        futures = [self.session.get(url) for url in urls]  # Send async requests
        results = []
        for future in futures:
            try:
                response = future.result()  # Wait for the response
                if response.status_code == 200:
                    results.append(response.json())
                else:
                    results.append(None)
            except Exception:
                results.append(None)
        return results


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
        self.hn.session.close()


if __name__ == '__main__':
    unittest.main()
