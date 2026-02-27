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
import pytest


class TestShowStories(unittest.IsolatedAsyncioTestCase):  # Use IsolatedAsyncioTestCase for async tests

    async def asyncSetUp(self):
        self.hn = HackerNews()

    @pytest.mark.asyncio
    async def test_show_stories(self):
        show_stories = await self.hn.show_stories(limit=10)  # Await the async method
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], Item)
        self.assertIsNotNone(show_stories)

    @pytest.mark.asyncio
    async def test_show_stories_raw(self):
        show_stories = await self.hn.show_stories(raw=True)  # Await the async method
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], str)
        self.assertIsNotNone(show_stories)

    async def asyncTearDown(self):
        await self.hn.session.close()  # Asynchronously close the session


if __name__ == '__main__':
    unittest.main()
