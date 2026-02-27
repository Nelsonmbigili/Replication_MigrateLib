#!/usr/bin/env python

"""
Tests updates()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import asyncio
from hackernews import HackerNews


class TestUpdates(unittest.IsolatedAsyncioTestCase):  # Use IsolatedAsyncioTestCase for async tests

    async def asyncSetUp(self):
        self.hn = HackerNews()

    async def test_top_stories(self):
        updates = await self.hn.updates()  # Await the asynchronous method
        self.assertIsNotNone(updates)
        self.assertIsInstance(updates, dict)
        self.assertIsInstance(updates['profiles'], list)
        self.assertIsInstance(updates['items'], list)

    async def asyncTearDown(self):
        await self.hn.session.close()  # Ensure proper cleanup of async resources

if __name__ == '__main__':
    unittest.main()
