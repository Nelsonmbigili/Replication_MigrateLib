import pycurl
from io import BytesIO
import json

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
        curl.setopt(curl.URL, url)
        curl.setopt(curl.WRITEDATA, buffer)
        curl.setopt(curl.FOLLOWLOCATION, True)
        curl.setopt(curl.USERAGENT, "pycurl/7.45.6")
        curl.perform()
        curl.close()

        response_data = buffer.getvalue().decode("utf-8")
        return json.loads(response_data)

    def top_stories(self, limit=None, raw=False):
        """
        Fetches the top stories from Hacker News.
        """
        top_stories_ids = self._make_request("topstories")
        if limit:
            top_stories_ids = top_stories_ids[:limit]

        if raw:
            return [str(story_id) for story_id in top_stories_ids]

        return [self.get_item(story_id) for story_id in top_stories_ids]

    def get_item(self, item_id):
        """
        Fetches a single item (story, comment, etc.) by its ID.
        """
        item_data = self._make_request(f"item/{item_id}")
        return Item(item_data)


class Item:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"<Item {self.data.get('id')}>"
#!/usr/bin/env python

"""
Tests top_stories()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import unittest

from hackernews import HackerNews
from hackernews import Item


class TestTopStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_top_stories(self):
        top_stories = self.hn.top_stories(limit=10)
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], Item)
        self.assertIsNotNone(top_stories)

    def test_top_stories_raw(self):
        top_stories = self.hn.top_stories(raw=True)
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], str)
        self.assertIsNotNone(top_stories)

    def tearDown(self):
        pass  # No session to close since pycurl does not use persistent sessions.

if __name__ == '__main__':
    unittest.main()
