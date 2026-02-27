#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck
"""

import unittest
from requests_futures.sessions import FuturesSession  # Updated import for FuturesSession
from hackernews import HackerNews
from hackernews import Item


# Assuming the HackerNews class is defined in the hackernews module
# and uses requests.Session internally. Modify it to use FuturesSession.
class HackerNews:
    def __init__(self):
        self.session = FuturesSession()  # Use FuturesSession instead of requests.Session

    def get_items_by_ids(self, ids, item_type=None):
        # Example implementation of an asynchronous request
        futures = [self.session.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json") for id in ids]
        responses = [future.result() for future in futures]  # Wait for all futures to complete
        items = [response.json() for response in responses if response.status_code == 200]

        if item_type:
            items = [item for item in items if item.get('type') == item_type]

        return [Item(**item) for item in items]


class TestGetItemsByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_items_by_ids(self):
        items = self.hn.get_items_by_ids([1, 2, 3])
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 3)
        self.assertIsInstance(items[0], Item)

    def test_get_items_by_ids_filtered(self):
        items = self.hn.get_items_by_ids(
            [i for i in range(1, 50)],
            item_type='story'
        )
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 37)
        self.assertIsInstance(items[0], Item)

    def tearDown(self):
        self.hn.session.close()


if __name__ == '__main__':
    unittest.main()
