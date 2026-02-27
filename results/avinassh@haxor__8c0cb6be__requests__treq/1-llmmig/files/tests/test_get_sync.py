#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjke
"""

import unittest
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred
import treq
from hackernews import HackerNews
from hackernews import HTTPError


class HackerNews:
    def __init__(self):
        pass

    @inlineCallbacks
    def _get_sync(self, url):
        """
        Synchronous-like method to fetch data from the given URL using treq.
        """
        response = yield treq.get(url)
        if response.code != 200:
            raise HTTPError(f"HTTP Error: {response.code}")
        data = yield response.json()
        return data


class TestGetSync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_sync(self):
        """
        Test the _get_sync method for a valid URL.
        """
        def run_test():
            d = self.hn._get_sync(self.url)
            d.addCallback(self._assert_valid_response)
            return d

        def _assert_valid_response(self, response):
            self.assertEqual(response['id'], 8863)
            self.assertEqual(response['by'], 'dhouston')

        return run_test()

    def test_get_sync_error(self):
        """
        Test the _get_sync method for an invalid URL.
        """
        def run_test():
            d = self.hn._get_sync(self.err_url)
            d.addErrback(self._assert_error_raised)
            return d

        def _assert_error_raised(self, failure):
            self.assertIsInstance(failure.value, HTTPError)

        return run_test()

    def tearDown(self):
        pass  # No session to close in treq


if __name__ == '__main__':
    unittest.main()
