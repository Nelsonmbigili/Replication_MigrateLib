### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The `requests` library was replaced with `urllib3`. The `requests` library is a higher-level abstraction over HTTP requests, while `urllib3` is a lower-level library that requires more manual handling of connections and responses.

2. **Creating a Pool Manager**: In `urllib3`, a `PoolManager` is used to manage connections. This was instantiated to handle the HTTP requests.

3. **Making Requests**: The `requests.get()` method was replaced with the `http.request()` method from the `urllib3` library. The headers were passed as a dictionary to this method.

4. **Response Handling**: The response from `urllib3` is an object that requires accessing the `.data` attribute to get the response body, which is in bytes. This was decoded to a string using `.decode('utf-8')`.

5. **Response Status Code**: The status code check was modified to use the `response.status` attribute from the `urllib3` response object.

Here is the modified code:

```python
"""The Main Snapchat Downloader Class."""

import concurrent.futures
import json
import os
import re

import urllib3
from loguru import logger

from snapchat_dl.downloader import download_url
from snapchat_dl.utils import APIResponseError
from snapchat_dl.utils import dump_response
from snapchat_dl.utils import MEDIA_TYPE
from snapchat_dl.utils import NoStoriesFound
from snapchat_dl.utils import strf_time
from snapchat_dl.utils import UserNotFoundError

class SnapchatDL:
    """Interact with Snapchat API to download story."""

    def __init__(
        self,
        directory_prefix=".",
        max_workers=2,
        limit_story=-1,
        sleep_interval=1,
        quiet=False,
        dump_json=False,
    ):
        self.directory_prefix = os.path.abspath(os.path.normpath(directory_prefix))
        self.max_workers = max_workers
        self.limit_story = limit_story
        self.sleep_interval = sleep_interval
        self.quiet = quiet
        self.dump_json = dump_json
        self.endpoint_web = "https://www.snapchat.com/add/{}/"
        self.regexp_web_json = (
            r'<script\s*id="__NEXT_DATA__"\s*type="application\/json">([^<]+)<\/script>'
        )
        self.reaponse_ok = 200  # Changed to a static value for HTTP OK

        # Create a PoolManager instance
        self.http = urllib3.PoolManager()

    def _api_response(self, username):
        web_url = self.endpoint_web.format(username)
        response = self.http.request(
            'GET',
            web_url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            },
        )
        if response.status != self.reaponse_ok:
            raise APIResponseError("Failed to fetch data from API")
        return response.data.decode('utf-8')

    def _web_fetch_story(self, username):
        """Download user stories from Web.

        Args:
            username (str): Snapchat `username`

        Raises:
            APIResponseError: API Error

        Returns:
            (dict, dict): user_info, stories
        """
        response = self._api_response(username)
        response_json_raw = re.findall(self.regexp_web_json, response)

        try:
            response_json = json.loads(response_json_raw[0])

            def util_web_user_info(content: dict):
                if "userProfile" in content["props"]["pageProps"]:
                    user_profile = content["props"]["pageProps"]["userProfile"]
                    field_id = user_profile["$case"]
                    return user_profile[field_id]
                else:
                    raise UserNotFoundError

            def util_web_story(content: dict):
                if "story" in content["props"]["pageProps"]:
                    return content["props"]["pageProps"]["story"]["snapList"]
                return list()

            def util_web_extract(content: dict):
                if "curatedHighlights" in content["props"]["pageProps"]:
                    return content["props"]["pageProps"]["curatedHighlights"]
                return list()

            user_info = util_web_user_info(response_json)
            stories = util_web_story(response_json)
            curatedHighlights = util_web_extract(response_json)
            spotHighlights = util_web_extract(response_json)
            return stories, user_info, curatedHighlights, spotHighlights
        except (IndexError, KeyError, ValueError):
            raise APIResponseError

    def download(self, username):
        """Download Snapchat Story for `username`.

        Args:
            username (str): Snapchat `username`

        Returns:
            [bool]: story downloader
        """
        stories, snap_user, *_ = self._web_fetch_story(username)

        if len(stories) == 0:
            if self.quiet is False:
                logger.info("\033[91m{}\033[0m has no stories".format(username))

            raise NoStoriesFound

        if self.limit_story > -1:
            stories = stories[0 : self.limit_story]

        logger.info("[+] {} has {} stories".format(username, len(stories)))

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        try:
            for media in stories:
                snap_id = media["snapId"]["value"]
                media_url = media["snapUrls"]["mediaUrl"]
                media_type = media["snapMediaType"]
                timestamp = int(media["timestampInSec"]["value"])
                date_str = strf_time(timestamp, "%Y-%m-%d")

                dir_name = os.path.join(self.directory_prefix, username, date_str)

                filename = strf_time(timestamp, "%Y-%m-%d_%H-%M-%S {} {}.{}").format(
                    snap_id, username, MEDIA_TYPE[media_type]
                )

                if self.dump_json:
                    filename_json = os.path.join(dir_name, filename + ".json")
                    media_json = dict(media)
                    media_json["snapUser"] = snap_user
                    dump_response(media_json, filename_json)

                media_output = os.path.join(dir_name, filename)
                executor.submit(
                    download_url, media_url, media_output, self.sleep_interval
                )

        except KeyboardInterrupt:
            executor.shutdown(wait=False)

        logger.info("[✔] {} stories downloaded".format(username, len(stories)))
```