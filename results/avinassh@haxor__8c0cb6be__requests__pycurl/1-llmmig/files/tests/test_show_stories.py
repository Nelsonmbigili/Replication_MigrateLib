#!/usr/bin/env python

"""
Tests show_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import pycurl
from io import BytesIO
import json


class Item:
    """Represents an item from Hacker News."""
    def __init__(self, data):
        self.data = data


class HackerNews:
    """HackerNews client using pycurl."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        pass

    def _make_request(self, endpoint):
        """Make an HTTP GET request using pycurl."""
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, f"{self.BASE_URL}/{endpoint}.json")
        curl.setopt(curl.WRITEDATA, buffer)
        curl.setopt(curl.FOLLOWLOCATION, True)
        curl.perform()
        curl.close()

        body = buffer.getvalue().decode('utf-8')
        return json.loads(body)

    def show_stories(self, limit=None, raw=False):
        """Fetch 'show' stories from Hacker News."""
        stories = self._make_request("showstories")
        if limit:
            stories = stories[:limit]

        if raw:
            return stories

        return [Item(self._make_request(f"item/{story_id}")) for story_id in stories]

    def close(self):
        """Placeholder for closing resources (if needed)."""
        pass


class TestShowStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_show_stories(self):
        show_stories = self.hn.show_stories(limit=10)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], Item)
        self.assertIsNotNone(show_stories)

    def test_show_stories_raw(self):
        show_stories = self.hn.show_stories(raw=True)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], str)
        self.assertIsNotNone(show_stories)

    def tearDown(self):
        self.hn.close()


if __name__ == '__main__':
    unittest.main()
