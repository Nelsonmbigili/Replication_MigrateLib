### Explanation of Changes
To migrate the code from using the `requests` library to using `pycurl`, the following changes were made:

1. **Importing PycURL**: The `requests` library was replaced with `pycurl`. The `HTTPError` exception handling was removed since `pycurl` does not raise this specific exception.
2. **Download Function**: The `download_url` function needs to be modified to use `pycurl` for making HTTP requests. This involves setting up a `pycurl.Curl` object, configuring it with the necessary options (like URL, output file, etc.), and executing the request.
3. **Error Handling**: Instead of raising an `HTTPError`, we will handle errors using `pycurl`'s error codes and exceptions.

The following code reflects these changes:

### Modified Code
```python
"""Tests for `snapchat_dl` package."""

import os
import shutil
import unittest
import pycurl
from io import BytesIO

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
        with self.assertRaises(pycurl.error):
            download_url(
                self.test_url404, ".test-data/test_dl_23.mp4", sleep_interval=0
            )
```

### Note
The `download_url` function itself must be modified to implement the actual downloading logic using `pycurl`. The above code assumes that the `download_url` function is updated accordingly to handle `pycurl` operations.