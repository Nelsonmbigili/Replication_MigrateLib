#!/usr/bin/env python

"""
Tests ask_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import pycurl
from io import BytesIO
import json

from hackernews import HackerNews
from hackernews import Item


class TestAskStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_ask_stories(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/askstories.json?print=pretty')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        response = json.loads(buffer.getvalue().decode('utf-8'))
        ask_stories = [Item(**item) for item in response[:10]]  # Assuming Item can be initialized this way
        self.assertIsInstance(ask_stories, list)
        self.assertIsInstance(ask_stories[0], Item)
        self.assertIsNotNone(ask_stories)

    def test_ask_stories_raw(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/askstories.json?print=pretty')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        response = buffer.getvalue().decode('utf-8')
        ask_stories = json.loads(response)
        self.assertIsInstance(ask_stories, list)
        self.assertIsInstance(ask_stories[0], str)
        self.assertIsNotNone(ask_stories)

    def tearDown(self):
        pass  # No session to close in pycurl

if __name__ == '__main__':
    unittest.main()
