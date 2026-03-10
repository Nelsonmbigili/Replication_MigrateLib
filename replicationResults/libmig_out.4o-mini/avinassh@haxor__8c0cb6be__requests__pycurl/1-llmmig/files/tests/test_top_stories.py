#!/usr/bin/env python

"""
Tests top_stories()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import unittest
import pycurl
from io import BytesIO
from hackernews import HackerNews
from hackernews import Item


class TestTopStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_top_stories(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        top_stories = self.hn.top_stories(limit=10)
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], Item)
        self.assertIsNotNone(top_stories)

    def test_top_stories_raw(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        top_stories = self.hn.top_stories(raw=True)
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], str)
        self.assertIsNotNone(top_stories)

    def tearDown(self):
        pass  # No session to close with pycurl

if __name__ == '__main__':
    unittest.main()
