import pycurl
from io import BytesIO
import json


class Item:
    def __init__(self, item_id, data):
        self.item_id = item_id
        self.data = data

    def __repr__(self):
        return f"<Item {self.item_id}>"


class HackerNews:
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        pass

    def _get(self, endpoint):
        """
        Perform a GET request using pycurl.
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

        # Decode the response
        response_data = buffer.getvalue().decode("utf-8")
        return json.loads(response_data)

    def ask_stories(self, limit=None, raw=False):
        """
        Fetch ask stories from Hacker News.
        """
        story_ids = self._get("askstories")
        if limit:
            story_ids = story_ids[:limit]

        if raw:
            return story_ids

        stories = []
        for story_id in story_ids:
            story_data = self._get(f"item/{story_id}")
            stories.append(Item(story_id, story_data))
        return stories
#!/usr/bin/env python

"""
Tests ask_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest

from hackernews import HackerNews
from hackernews import Item


class TestAskStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_ask_stories(self):
        ask_stories = self.hn.ask_stories(limit=10)
        self.assertIsInstance(ask_stories, list)
        self.assertIsInstance(ask_stories[0], Item)
        self.assertIsNotNone(ask_stories)

    def test_ask_stories_raw(self):
        ask_stories = self.hn.ask_stories(raw=True)
        self.assertIsInstance(ask_stories, list)
        self.assertIsInstance(ask_stories[0], str)
        self.assertIsNotNone(ask_stories)

    def tearDown(self):
        pass  # No session to close with pycurl


if __name__ == '__main__':
    unittest.main()
