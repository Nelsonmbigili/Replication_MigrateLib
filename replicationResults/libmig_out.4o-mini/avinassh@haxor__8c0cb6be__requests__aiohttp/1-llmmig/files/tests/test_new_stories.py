#!/usr/bin/env python

"""
Tests new_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import aiohttp
import asyncio

from hackernews import HackerNews
from hackernews import Item


class TestNewStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    async def async_test_new_stories(self):
        new_stories = await self.hn.new_stories(limit=10)
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], Item)
        self.assertIsNotNone(new_stories)

    async def async_test_new_stories_raw(self):
        new_stories = await self.hn.new_stories(raw=True)
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], str)
        self.assertIsNotNone(new_stories)

    def test_new_stories(self):
        asyncio.run(self.async_test_new_stories())

    def test_new_stories_raw(self):
        asyncio.run(self.async_test_new_stories_raw())

    def tearDown(self):
        pass  # No need to close session explicitly with aiohttp

if __name__ == '__main__':
    unittest.main()
