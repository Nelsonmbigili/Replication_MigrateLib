#!/usr/bin/env python

"""
Tests show_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import treq
from twisted.internet import reactor, defer
from twisted.web.client import Agent
from twisted.internet.defer import inlineCallbacks


class Item:
    """Represents a Hacker News item."""
    def __init__(self, item_id, title, url):
        self.item_id = item_id
        self.title = title
        self.url = url


class HackerNews:
    """HackerNews API client using treq."""
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.agent = Agent(reactor)

    @inlineCallbacks
    def show_stories(self, limit=10, raw=False):
        """Fetches 'show' stories from Hacker News."""
        url = f"{self.BASE_URL}/showstories.json"
        response = yield treq.get(url, agent=self.agent)
        story_ids = yield treq.json_content(response)

        if raw:
            defer.returnValue(story_ids[:limit])

        stories = []
        for story_id in story_ids[:limit]:
            story_url = f"{self.BASE_URL}/item/{story_id}.json"
            story_response = yield treq.get(story_url, agent=self.agent)
            story_data = yield treq.json_content(story_response)
            stories.append(Item(story_data['id'], story_data['title'], story_data.get('url', '')))

        defer.returnValue(stories)

    def close(self):
        """Closes any resources if needed (not required for treq)."""
        pass


class TestShowStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    @defer.inlineCallbacks
    def test_show_stories(self):
        show_stories = yield self.hn.show_stories(limit=10)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], Item)
        self.assertIsNotNone(show_stories)

    @defer.inlineCallbacks
    def test_show_stories_raw(self):
        show_stories = yield self.hn.show_stories(raw=True)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], str)
        self.assertIsNotNone(show_stories)

    def tearDown(self):
        self.hn.close()


if __name__ == '__main__':
    unittest.main()
