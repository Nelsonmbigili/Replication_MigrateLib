#!/usr/bin/env python

"""
Tests get_all()

@author john keck
@email robertjkeck
"""

import unittest
import asyncio

from hackernews import HackerNews
from hackernews import Item


class TestGetLast(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_item(self):
        async def async_test():
            items = await self.hn.get_last(5)
            self.assertIsInstance(items, list)
            self.assertEqual(len(items), 5)
            self.assertIsInstance(items[0], Item)

        asyncio.run(async_test())

    def tearDown(self):
        async def async_teardown():
            await self.hn.session.close()

        asyncio.run(async_teardown())


if __name__ == '__main__':
    unittest.main()
