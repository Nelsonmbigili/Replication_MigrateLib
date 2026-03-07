#!/usr/bin/env python

"""
Tests get_all()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import httpx  # Assuming httpx is used in HackerNews class

from hackernews import HackerNews
from hackernews import Item


class TestGetLast(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_item(self):
        items = self.hn.get_last(5)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 5)
        self.assertIsInstance(items[0], Item)

    def tearDown(self):
        self.hn.session.close()  # This may need to be adapted if using httpx.Client()

if __name__ == '__main__':
    unittest.main()
