#!/usr/bin/env python

"""
Tests job_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import httpx  # Importing httpx

from hackernews import HackerNews
from hackernews import Item


class TestJobStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = httpx.Client()  # Using httpx.Client() instead of requests.Session()

    def test_job_stories(self):
        job_stories = self.hn.job_stories(limit=10)
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], Item)
        self.assertIsNotNone(job_stories)

    def test_job_stories_raw(self):
        job_stories = self.hn.job_stories(raw=True)
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], str)
        self.assertIsNotNone(job_stories)

    def tearDown(self):
        self.hn.session.close()  # Closing the httpx.Client() session

if __name__ == '__main__':
    unittest.main()
