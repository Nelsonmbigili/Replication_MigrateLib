### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Changes**: The import statement for `HTTPError` was removed since `urllib3` handles HTTP errors differently. Instead of raising an `HTTPError`, `urllib3` will raise a different exception, which we will handle accordingly.
  
2. **Error Handling**: The error handling in the `test_download_url_raise` method was modified to catch `urllib3.exceptions.HTTPError` instead of `requests.exceptions.HTTPError`. 

3. **Download Function**: The `download_url` function is assumed to be modified to use `urllib3` internally. If it still uses `requests`, it would need to be updated accordingly, but since the instruction is to only change the parts directly related to the migration, we will assume `download_url` is already adapted.

Here is the modified code:

```python
"""Tests for `snapchat_dl` package."""

import os
import shutil
import unittest

from urllib3.exceptions import HTTPError

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

This code now uses `urllib3` for HTTP error handling while keeping the overall structure and functionality intact.