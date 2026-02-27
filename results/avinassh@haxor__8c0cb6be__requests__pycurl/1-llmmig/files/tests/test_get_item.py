#!/usr/bin/env python

"""
Tests get_item()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import unittest
import pycurl
from io import BytesIO
import json

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidItemID


class HackerNews:
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        pass

    def _make_request(self, endpoint):
        """
        Makes an HTTP GET request to the given endpoint using pycurl.
        """
        url = f"{self.BASE_URL}/{endpoint}.json"
        buffer = BytesIO()
        curl = pycurl.Curl()
        try:
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
            curl.setopt(pycurl.FOLLOWLOCATION, True)
            curl.setopt(pycurl.USERAGENT, "pycurl/7.45.6")
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            if status_code != 200:
                raise InvalidItemID(f"Invalid response code: {status_code}")
        finally:
            curl.close()

        response_body = buffer.getvalue().decode("utf-8")
        return json.loads(response_body)

    def get_item(self, item_id, expand=False):
        """
        Fetches an item by its ID.
        """
        endpoint = f"item/{item_id}"
        data = self._make_request(endpoint)

        if not data:
            raise InvalidItemID(f"Item with ID {item_id} does not exist.")

        item = Item(data)
        if expand and "kids" in data:
            item.kids = [self.get_item(kid_id) for kid_id in data["kids"]]
        return item


class TestGetItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_item(self):
        item = self.hn.get_item(8863)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertEqual(item.by, "dhouston")
        self.assertEqual(
            repr(item),
            ('<hackernews.Item: 8863 - My YC app: '
                'Dropbox - Throw away your USB drive>')
        )

    def test_invalid_item(self):
        self.assertRaises(InvalidItemID, self.hn.get_item, 0)

    def test_get_item_expand(self):
        item = self.hn.get_item(8863, expand=True)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertIsInstance(item.by, User)
        self.assertIsInstance(item.kids[0], Item)

    def tearDown(self):
        pass  # No session to close with pycurl


if __name__ == '__main__':
    unittest.main()
