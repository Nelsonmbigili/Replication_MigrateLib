#!/usr/bin/env python

"""
Tests job_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import pycurl
from io import BytesIO
import json

from hackernews import HackerNews
from hackernews import Item


# Helper function to perform HTTP GET requests using pycurl
def pycurl_get(url):
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.WRITEDATA, buffer)
    curl.setopt(curl.FOLLOWLOCATION, True)
    curl.setopt(curl.USERAGENT, "pycurl/7.45.6")
    curl.perform()
    curl.close()
    response_data = buffer.getvalue().decode('utf-8')
    return response_data


# Updated HackerNews class to use pycurl
class HackerNews:
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def job_stories(self, limit=None, raw=False):
        url = f"{self.BASE_URL}/jobstories.json"
        response = pycurl_get(url)
        story_ids = json.loads(response)

        if limit:
            story_ids = story_ids[:limit]

        if raw:
            return [str(story_id) for story_id in story_ids]

        stories = []
        for story_id in story_ids:
            story_url = f"{self.BASE_URL}/item/{story_id}.json"
            story_response = pycurl_get(story_url)
            story_data = json.loads(story_response)
            stories.append(Item(story_data))
        return stories


class TestJobStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

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
        # No session to close with pycurl
        pass


if __name__ == '__main__':
    unittest.main()
