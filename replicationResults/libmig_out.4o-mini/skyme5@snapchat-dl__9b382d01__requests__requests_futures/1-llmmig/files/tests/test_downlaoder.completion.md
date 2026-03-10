### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the primary change involves how HTTP requests are made. The `requests_futures` library allows for asynchronous requests by using futures, which means we need to modify the way we handle the requests in the `download_url` function. Specifically, we will replace the synchronous request calls with futures that can be executed in the background. 

In the modified code, we will import `FuturesSession` from `requests_futures.sessions` instead of using the standard `requests` session. The `download_url` function will need to be adjusted to use this new session type, allowing it to handle requests asynchronously.

### Modified Code
```python
"""Tests for `snapchat_dl` package."""

import os
import shutil
import unittest

from requests_futures.sessions import FuturesSession
from requests.exceptions import HTTPError

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
        download_url(self.test_url, ".test-data/test_dl_23.mp4", sleep_interval=0)

    def test_empty_download(self):
        """Test snapchat_dl download_url."""
        open(".test-data/test_dl_23.mp4", "w").close()
        download_url(self.test_url, ".test-data/test_dl_23.mp4", sleep_interval=0)

    def test_download_url_raise(self):
        """Test snapchat_dl download_url with invalid url."""
        with self.assertRaises(HTTPError):
            download_url(
                self.test_url404, ".test-data/test_dl_23.mp4", sleep_interval=0
            )
```

### Note
The actual implementation of the `download_url` function is not provided in the original code snippet. Therefore, ensure that the `download_url` function is updated to utilize `FuturesSession` for making requests asynchronously. This will involve creating a `FuturesSession` instance and using it to make the HTTP requests instead of the standard `requests` session.