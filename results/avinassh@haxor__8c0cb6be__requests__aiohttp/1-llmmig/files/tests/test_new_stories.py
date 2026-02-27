#!/usr/bin/env python

"""
Tests new_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from hackernews import HackerNews
from hackernews import Item


class TestNewStories(unittest.IsolatedAsyncioTestCase):  # Use IsolatedAsyncioTestCase for async tests

    async def asyncSetUp(self):
        self.hn = HackerNews()

    async def test_new_stories(self):
        new_stories = await self.hn.new_stories(limit=10)  # Await the async method
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], Item)
        self.assertIsNotNone(new_stories)

    async def test_new_stories_raw(self):
        new_stories = await self.hn.new_stories(raw=True)  # Await the async method
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], str)
        self.assertIsNotNone(new_stories)

    async def asyncTearDown(self):
        await self.hn.session.close()  # Close the aiohttp session asynchronously


if __name__ == '__main__':
    unittest.main()
