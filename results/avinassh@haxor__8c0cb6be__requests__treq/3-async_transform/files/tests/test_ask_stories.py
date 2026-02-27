#!/usr/bin/env python

"""
Tests ask_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import asyncio
from hackernews import HackerNews
from hackernews import Item
import pytest


class TestAskStories(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.hn = HackerNews()

    @pytest.mark.asyncio
    async def test_ask_stories(self):
        ask_stories = await self.hn.ask_stories(limit=10)
        self.assertIsInstance(ask_stories, list)
        self.assertIsInstance(ask_stories[0], Item)
        self.assertIsNotNone(ask_stories)

    @pytest.mark.asyncio
    async def test_ask_stories_raw(self):
        ask_stories = await self.hn.ask_stories(raw=True)
        self.assertIsInstance(ask_stories, list)
        self.assertIsInstance(ask_stories[0], str)
        self.assertIsNotNone(ask_stories)

    async def asyncTearDown(self):
        await self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
