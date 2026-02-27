#!/usr/bin/env python

"""
Tests get_all()

@author john keck
@email robertjke
"""

import unittest
from twisted.internet import defer
from twisted.trial.unittest import TestCase

from hackernews import HackerNews
from hackernews import Item


class TestGetLast(TestCase):

    def setUp(self):
        self.hn = HackerNews()

    @defer.inlineCallbacks
    def test_get_item(self):
        items = yield self.hn.get_last(5)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 5)
        self.assertIsInstance(items[0], Item)

    def tearDown(self):
        # No explicit session close needed for treq
        pass


if __name__ == '__main__':
    unittest.main()
