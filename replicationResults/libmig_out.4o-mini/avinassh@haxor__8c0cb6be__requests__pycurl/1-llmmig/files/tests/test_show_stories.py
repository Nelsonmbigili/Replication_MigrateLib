#!/usr/bin/env python

"""
Tests show_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import pycurl
from io import BytesIO
from hackernews import HackerNews
from hackernews import Item


class TestShowStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_show_stories(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        show_stories = self.hn.show_stories(limit=10)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], Item)
        self.assertIsNotNone(show_stories)

    def test_show_stories_raw(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        show_stories = self.hn.show_stories(raw=True)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], str)
        self.assertIsNotNone(show_stories)

    def tearDown(self):
        pass  # No session to close with pycurl

if __name__ == '__main__':
    unittest.main()
