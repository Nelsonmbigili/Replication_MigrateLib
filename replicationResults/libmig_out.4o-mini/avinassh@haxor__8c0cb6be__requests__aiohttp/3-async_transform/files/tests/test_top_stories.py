#!/usr/bin/env python

"""
Tests top_stories()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import unittest
import asyncio

from hackernews import HackerNews
from hackernews import Item
import pytest


class TestTopStories(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.hn = HackerNews()

    @pytest.mark.asyncio
    async def test_top_stories(self):
        top_stories = await self.hn.top_stories(limit=10)
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], Item)
        self.assertIsNotNone(top_stories)

    @pytest.mark.asyncio
    async def test_top_stories_raw(self):
        top_stories = await self.hn.top_stories(raw=True)
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], str)
        self.assertIsNotNone(top_stories)

    async def asyncTearDown(self):
        await self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
