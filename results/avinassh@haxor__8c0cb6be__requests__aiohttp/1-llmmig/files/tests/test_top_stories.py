#!/usr/bin/env python

"""
Tests top_stories()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import unittest
from hackernews import HackerNews
from hackernews import Item


class TestTopStories(unittest.IsolatedAsyncioTestCase):  # Use IsolatedAsyncioTestCase for async tests

    async def asyncSetUp(self):
        self.hn = HackerNews()

    async def test_top_stories(self):
        top_stories = await self.hn.top_stories(limit=10)  # Await the async method
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], Item)
        self.assertIsNotNone(top_stories)

    async def test_top_stories_raw(self):
        top_stories = await self.hn.top_stories(raw=True)  # Await the async method
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], str)
        self.assertIsNotNone(top_stories)

    async def asyncTearDown(self):
        await self.hn.session.close()  # Close the aiohttp session asynchronously


if __name__ == '__main__':
    unittest.main()
