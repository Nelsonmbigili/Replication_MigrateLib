#!/usr/bin/env python

"""
Tests job_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import urllib3
import json

from hackernews import HackerNews
from hackernews import Item


class TestJobStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.http = urllib3.PoolManager()

    def test_job_stories(self):
        response = self.hn.http.request('GET', 'https://hacker-news.firebaseio.com/v0/jobstories.json?print=pretty&limit=10')
        job_stories = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], Item)
        self.assertIsNotNone(job_stories)

    def test_job_stories_raw(self):
        response = self.hn.http.request('GET', 'https://hacker-news.firebaseio.com/v0/jobstories.json?print=pretty&raw=true')
        job_stories = response.data.decode('utf-8').splitlines()
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], str)
        self.assertIsNotNone(job_stories)

    def tearDown(self):
        pass  # No need to close the PoolManager

if __name__ == '__main__':
    unittest.main()
