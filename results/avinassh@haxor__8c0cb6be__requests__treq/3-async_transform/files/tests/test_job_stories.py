#!/usr/bin/env python

"""
Tests job_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import asyncio
from hackernews import HackerNews
from hackernews import Item
import pytest


class TestJobStories(unittest.IsolatedAsyncioTestCase):  # Use IsolatedAsyncioTestCase for async tests

    async def asyncSetUp(self):
        self.hn = HackerNews()

    @pytest.mark.asyncio
    async def test_job_stories(self):
        job_stories = await self.hn.job_stories(limit=10)  # Await the async method
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], Item)
        self.assertIsNotNone(job_stories)

    @pytest.mark.asyncio
    async def test_job_stories_raw(self):
        job_stories = await self.hn.job_stories(raw=True)  # Await the async method
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], str)
        self.assertIsNotNone(job_stories)

    async def asyncTearDown(self):
        await self.hn.session.close()  # Ensure proper cleanup of async resources


if __name__ == '__main__':
    unittest.main()
