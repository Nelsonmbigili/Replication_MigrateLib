#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck
"""

import unittest
import asyncio
from hackernews import HackerNews
from hackernews import User
import pytest


class TestGetUsersByIDs(unittest.IsolatedAsyncioTestCase):  # Use IsolatedAsyncioTestCase for async tests

    async def asyncSetUp(self):
        self.hn = HackerNews()

    @pytest.mark.asyncio
    async def test_get_users_by_ids(self):
        users = await self.hn.get_users_by_ids(['pg', 'tptacek', 'jacquesm'])  # Await the async method
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    async def asyncTearDown(self):
        await self.hn.session.close()  # Ensure the aiohttp session is properly closed

if __name__ == '__main__':
    unittest.main()
