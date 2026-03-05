#!/usr/bin/env python

"""
Tests updates()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import aiohttp
import asyncio

from hackernews import HackerNews


class TestUpdates(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    async def async_test_top_stories(self):
        updates = await self.hn.updates()
        self.assertIsNotNone(updates)
        self.assertIsInstance(updates, dict)
        self.assertIsInstance(updates['profiles'], list)
        self.assertIsInstance(updates['items'], list)

    def test_top_stories(self):
        asyncio.run(self.async_test_top_stories())

    def tearDown(self):
        pass  # No need to close session explicitly with aiohttp

if __name__ == '__main__':
    unittest.main()
