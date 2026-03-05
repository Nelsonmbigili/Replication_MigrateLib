#!/usr/bin/env python

"""
Tests get_user()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import datetime
import unittest
import asyncio

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidUserID


class TestGetUser(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    async def async_get_user(self, user_id, expand=False):
        return await self.hn.get_user(user_id, expand=expand)

    def test_get_user(self):
        user = asyncio.run(self.async_get_user('pg'))
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'pg')
        self.assertEqual(user.created,
                         datetime.datetime.fromtimestamp(1160418092))
        self.assertEqual(repr(user), '<hackernews.User: pg>')

    def test_get_invalid_user(self):
        self.assertRaises(InvalidUserID, asyncio.run, self.async_get_user('a'))

    def test_get_user_expand(self):
        user = asyncio.run(self.async_get_user('avinassh', expand=True))
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'avinassh')
        self.assertIsInstance(user.comments[0], Item)
        self.assertIsInstance(user.stories[0], Item)

    def tearDown(self):
        pass  # No need to close session explicitly in aiohttp

if __name__ == '__main__':
    unittest.main()
