### Explanation of Changes
To migrate the code from using the `requests` library to the `aiohttp` library, the following changes were made:

1. **Importing aiohttp**: The `requests` library was replaced with `aiohttp` for asynchronous HTTP requests.
2. **Asynchronous Functions**: The `download_url` function needs to be modified to be asynchronous, which requires using `async def` and `await` for making requests.
3. **Error Handling**: The error handling for HTTP errors was updated to use `aiohttp.ClientResponseError` instead of `requests.exceptions.HTTPError`.
4. **Event Loop**: Since `aiohttp` is asynchronous, the test functions need to be run within an event loop. This is typically done using `asyncio.run()` in the main execution context.

### Modified Code
Here is the modified code using `aiohttp`:

```python
"""Tests for `snapchat_dl` package."""

import os
import shutil
import unittest
import aiohttp
import asyncio

from aiohttp import ClientResponseError

from snapchat_dl.downloader import download_url


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

    def test_download_url(self):
        """Test snapchat_dl download_url."""
        asyncio.run(download_url(self.test_url, ".test-data/test_dl_23.mp4", sleep_interval=0))

    def test_empty_download(self):
        """Test snapchat_dl download_url."""
        open(".test-data/test_dl_23.mp4", "w").close()
        asyncio.run(download_url(self.test_url, ".test-data/test_dl_23.mp4", sleep_interval=0))

    def test_download_url_raise(self):
        """Test snapchat_dl download_url with invalid url."""
        with self.assertRaises(ClientResponseError):
            asyncio.run(download_url(
                self.test_url404, ".test-data/test_dl_23.mp4", sleep_interval=0
            ))
```

### Note
Make sure that the `download_url` function in the `snapchat_dl.downloader` module is also updated to be asynchronous and compatible with `aiohttp`.