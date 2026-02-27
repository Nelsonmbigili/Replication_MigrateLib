#!/usr/bin/env python

"""
Tests ask_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import urllib3
import json


class HackerNews:
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.session = urllib3.PoolManager()

    def ask_stories(self, limit=10, raw=False):
        url = f"{self.BASE_URL}/askstories.json"
        response = self.session.request("GET", url)
        if response.status != 200:
            raise Exception(f"Failed to fetch ask stories: {response.status}")
        story_ids = json.loads(response.data.decode("utf-8"))[:limit]

        if raw:
            return story_ids

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


class Item:
    def __init__(self, data):
        self.data = data


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
        self.hn.close()


if __name__ == '__main__':
    unittest.main()
