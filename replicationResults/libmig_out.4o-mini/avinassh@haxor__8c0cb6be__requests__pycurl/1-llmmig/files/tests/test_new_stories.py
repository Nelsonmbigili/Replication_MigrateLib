#!/usr/bin/env python

"""
Tests new_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import pycurl
from io import BytesIO
from hackernews import HackerNews
from hackernews import Item


class TestNewStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_new_stories(self):
        new_stories = self.hn.new_stories(limit=10)
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], Item)
        self.assertIsNotNone(new_stories)

    def test_new_stories_raw(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/newstories.json?print=pretty')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        body = buffer.getvalue().decode('utf-8')
        new_stories = eval(body)  # Assuming the response is a JSON array of story IDs
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], str)
        self.assertIsNotNone(new_stories)

    def tearDown(self):
        pass  # No session to close with pycurl

if __name__ == '__main__':
    unittest.main()
