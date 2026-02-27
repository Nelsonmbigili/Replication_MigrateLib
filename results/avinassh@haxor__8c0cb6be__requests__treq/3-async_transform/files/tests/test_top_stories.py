#!/usr/bin/env python

"""
Tests top_stories()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import unittest
import asyncio
from hackernews import HackerNews
from hackernews import Item
import pytest


class TestTopStories(unittest.IsolatedAsyncioTestCase):  # Use IsolatedAsyncioTestCase for async tests

    async def asyncSetUp(self):
        self.hn = HackerNews()

    @pytest.mark.asyncio
    async def test_top_stories(self):
        top_stories = await self.hn.top_stories(limit=10)  # Await the async method
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], Item)
        self.assertIsNotNone(top_stories)

    @pytest.mark.asyncio
    async def test_top_stories_raw(self):
        top_stories = await self.hn.top_stories(raw=True)  # Await the async method
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], str)
        self.assertIsNotNone(top_stories)

    async def asyncTearDown(self):
        await self.hn.session.close()  # Ensure the session is closed asynchronously

if __name__ == '__main__':
    unittest.main()
