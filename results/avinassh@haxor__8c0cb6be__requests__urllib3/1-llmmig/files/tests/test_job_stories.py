#!/usr/bin/env python

"""
Tests job_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from hackernews import HackerNews
from hackernews import Item


class TestJobStories(unittest.TestCase):

    def setUp(self):
        # Initialize the HackerNews instance
        self.hn = HackerNews()

    def test_job_stories(self):
        # Test the job_stories method with a limit
        job_stories = self.hn.job_stories(limit=10)
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], Item)
        self.assertIsNotNone(job_stories)

    def test_job_stories_raw(self):
        # Test the job_stories method with raw=True
        job_stories = self.hn.job_stories(raw=True)
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], str)
        self.assertIsNotNone(job_stories)

    def tearDown(self):
        # Close the urllib3 PoolManager instance
        self.hn.session.close()


if __name__ == '__main__':
    unittest.main()
