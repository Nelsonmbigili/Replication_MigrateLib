"""Tests for `snapchat_dl` package."""

import os
import shutil
import unittest

from aiohttp import ClientResponseError  # Updated import for aiohttp

from snapchat_dl.downloader import download_url
import pytest


def teardown_module(module):
    shutil.rmtree(".test-data")


class Test_downloader(unittest.TestCase):
    """Tests for `snapchat_dl.downloader.download_url` package."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_url = (
            "https://sample-videos.com/video321/mp4/240/big_buck_bunny_240p_1mb.mp4"
        )
        self.test_url404 = "https://google.com/error.html"

    @pytest.mark.asyncio
    async def test_download_url(self):
        """Test snapchat_dl download_url."""
        await download_url(self.test_url, ".test-data/test_dl_23.mp4", sleep_interval=0)

    @pytest.mark.asyncio
    async def test_empty_download(self):
        """Test snapchat_dl download_url."""
        open(".test-data/test_dl_23.mp4", "w").close()
        await download_url(self.test_url, ".test-data/test_dl_23.mp4", sleep_interval=0)

    @pytest.mark.asyncio
    async def test_download_url_raise(self):
        """Test snapchat_dl download_url with invalid url."""
        with self.assertRaises(ClientResponseError):  # Updated exception
            await download_url(
                self.test_url404, ".test-data/test_dl_23.mp4", sleep_interval=0
            )
