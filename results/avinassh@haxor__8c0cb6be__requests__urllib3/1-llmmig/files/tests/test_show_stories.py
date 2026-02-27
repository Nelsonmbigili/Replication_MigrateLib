#!/usr/bin/env python

"""
Tests show_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import urllib3
import json


class Item:
    """Represents an item from Hacker News."""
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"Item({self.data})"


class HackerNews:
    """HackerNews client using urllib3."""
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.session = urllib3.PoolManager()

    def show_stories(self, limit=None, raw=False):
        url = f"{self.BASE_URL}/showstories.json"
        response = self.session.request("GET", url)
        if response.status != 200:
            raise Exception(f"Failed to fetch show stories: {response.status}")
        
        story_ids = json.loads(response.data.decode("utf-8"))
        if limit:
            story_ids = story_ids[:limit]

        if raw:
            return [str(story_id) for story_id in story_ids]

        stories = []
        for story_id in story_ids:
            story_url = f"{self.BASE_URL}/item/{story_id}.json"
            story_response = self.session.request("GET", story_url)
            if story_response.status == 200:
                story_data = json.loads(story_response.data.decode("utf-8"))
                stories.append(Item(story_data))
        return stories

    def close(self):
        self.session.clear()


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
