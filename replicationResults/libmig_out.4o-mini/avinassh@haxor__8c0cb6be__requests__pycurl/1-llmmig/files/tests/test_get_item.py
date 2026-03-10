#!/usr/bin/env python

"""
Tests get_item()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import unittest
import pycurl
from io import BytesIO
import json

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidItemID


class TestGetItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def get_item_with_pycurl(self, item_id, expand=False):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, f'https://hacker-news.firebaseio.com/v0/item/{item_id}.json')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        response_data = buffer.getvalue()
        item_data = json.loads(response_data)

        if 'error' in item_data:
            raise InvalidItemID("Invalid item ID")

        item = Item(**item_data)
        if expand:
            item.by = User(item.by)  # Assuming User can be constructed this way
            item.kids = [Item(**kid) for kid in item_data.get('kids', [])]
        return item

    def test_get_item(self):
        item = self.get_item_with_pycurl(8863)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertEqual(item.by, "dhouston")
        self.assertEqual(
            repr(item),
            ('<hackernews.Item: 8863 - My YC app: '
                'Dropbox - Throw away your USB drive>')
        )

    def test_invalid_item(self):
        with self.assertRaises(InvalidItemID):
            self.get_item_with_pycurl(0)

    def test_get_item_expand(self):
        item = self.get_item_with_pycurl(8863, expand=True)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertIsInstance(item.by, User)
        self.assertIsInstance(item.kids[0], Item)

    def tearDown(self):
        pass  # No session to close with pycurl

if __name__ == '__main__':
    unittest.main()
