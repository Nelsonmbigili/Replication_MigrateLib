#!/usr/bin/env python

"""
Tests show_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import asyncio

from hackernews import HackerNews
from hackernews import Item


class TestShowStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    async def async_test_show_stories(self):
        show_stories = await self.hn.show_stories(limit=10)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], Item)
        self.assertIsNotNone(show_stories)

    async def async_test_show_stories_raw(self):
        show_stories = await self.hn.show_stories(raw=True)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], str)
        self.assertIsNotNone(show_stories)

    def test_show_stories(self):
        asyncio.run(self.async_test_show_stories())

    def test_show_stories_raw(self):
        asyncio.run(self.async_test_show_stories_raw())

    def tearDown(self):
        pass  # No need to close session explicitly with aiohttp

if __name__ == '__main__':
    unittest.main()
