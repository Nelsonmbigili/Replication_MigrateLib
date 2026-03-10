#!/usr/bin/env python

"""
Tests job_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import pycurl
from io import BytesIO
from hackernews import HackerNews
from hackernews import Item


class TestJobStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_job_stories(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/jobstories.json?limit=10')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        job_stories = self.hn.parse_response(buffer.getvalue())
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], Item)
        self.assertIsNotNone(job_stories)

    def test_job_stories_raw(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/jobstories.json?raw=true')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        job_stories = self.hn.parse_response_raw(buffer.getvalue())
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], str)
        self.assertIsNotNone(job_stories)

    def tearDown(self):
        pass  # No session to close in pycurl

if __name__ == '__main__':
    unittest.main()
