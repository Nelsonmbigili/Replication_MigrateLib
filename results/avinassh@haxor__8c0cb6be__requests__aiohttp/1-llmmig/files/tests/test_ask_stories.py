#!/usr/bin/env python

"""
Tests ask_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from hackernews import HackerNews
from hackernews import Item


class TestAskStories(unittest.IsolatedAsyncioTestCase):  # Updated to support async tests

    async def asyncSetUp(self):
        self.hn = HackerNews()
        await self.hn.initialize_session()  # Assuming HackerNews has an async session initializer

    async def test_ask_stories(self):
        ask_stories = await self.hn.ask_stories(limit=10)  # Await the async method
        self.assertIsInstance(ask_stories, list)
        self.assertIsInstance(ask_stories[0], Item)
        self.assertIsNotNone(ask_stories)

    async def test_ask_stories_raw(self):
        ask_stories = await self.hn.ask_stories(raw=True)  # Await the async method
        self.assertIsInstance(ask_stories, list)
        self.assertIsInstance(ask_stories[0], str)
        self.assertIsNotNone(ask_stories)

    async def asyncTearDown(self):
        await self.hn.session.close()  # Close the aiohttp session asynchronously

if __name__ == '__main__':
    unittest.main()
