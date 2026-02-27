#!/usr/bin/env python

"""
Tests get_user()

@author avinash sajjanshetty
"""

import datetime
import unittest
import asyncio
from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidUserID


class TestGetUser(unittest.IsolatedAsyncioTestCase):  # Use IsolatedAsyncioTestCase for async tests

    async def asyncSetUp(self):
        self.hn = HackerNews()
        await self.hn.initialize_session()  # Initialize aiohttp session

    async def test_get_user(self):
        user = await self.hn.get_user('pg')  # Await the async method
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'pg')
        self.assertEqual(user.created,
                         datetime.datetime.fromtimestamp(1160418092))
        self.assertEqual(repr(user), '<hackernews.User: pg>')

    async def test_get_invalid_user(self):
        with self.assertRaises(InvalidUserID):
            await self.hn.get_user('a')  # Await the async method

    async def test_get_user_expand(self):
        user = await self.hn.get_user('avinassh', expand=True)  # Await the async method
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'avinassh')
        self.assertIsInstance(user.comments[0], Item)
        self.assertIsInstance(user.stories[0], Item)

    async def asyncTearDown(self):
        await self.hn.close_session()  # Close aiohttp session


if __name__ == '__main__':
    unittest.main()
import aiohttp

class HackerNews:
    def __init__(self):
        self.session = None

    async def initialize_session(self):
        self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def get_user(self, user_id, expand=False):
        if not self.session:
            raise RuntimeError("Session not initialized. Call initialize_session() first.")
        
        url = f"https://hacker-news.firebaseio.com/v0/user/{user_id}.json"
        async with self.session.get(url) as response:
            if response.status == 404:
                raise InvalidUserID(f"User {user_id} not found")
            data = await response.json()
            # Process the data and return a User object
            return User(data)
