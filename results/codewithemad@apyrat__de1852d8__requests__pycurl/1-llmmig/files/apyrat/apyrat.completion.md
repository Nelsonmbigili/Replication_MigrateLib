### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.get` calls**: The `requests.get` method was replaced with `pycurl` to perform HTTP GET requests. `pycurl` requires setting up a `pycurl.Curl` object, configuring it with the URL, headers, and other options, and then capturing the response in a buffer.
2. **Response Handling**: Since `pycurl` does not return a JSON object directly, the response is captured in a `BytesIO` buffer, and the content is decoded and parsed using the `json` module.
3. **Header Preparation**: Headers were converted into a format compatible with `pycurl` (a list of strings in the form `key: value`).
4. **Thread Safety**: `pycurl` is thread-safe, so no additional changes were needed for the `ThreadPoolExecutor`.

Below is the modified code:

---

### Modified Code:
```python
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from urllib.parse import urlparse
from io import BytesIO
import json

import click
import pycurl
import wget

from apyrat.utils import prepare_headers, check_domain_validity


# Enum declarations
class URLType(Enum):
    VIDEO = "video"
    PLAYLIST = "playlist"


class VideoQuality(Enum):
    FULL_HD = "1080p"
    HD = "720p"
    FOUR_EIGHTY = "480p"
    THREE_SIXTY = "360p"
    TWO_FORTY = "240p"
    ONE_FORTY_FOUR = "144p"


# CONSTANTS
API_BASE_URL = "https://www.aparat.com/api/fa/v1"


class Downloader:
    def __init__(self, url, filename=None) -> None:
        self.file_name = filename
        self.links = []
        self.url = self._cleanup_url(url)
        self.url_type = self._url_type()
        self.videos = self._get_available_videos()
        self.qualities = self._get_available_qualities()

    @staticmethod
    def _cleanup_url(url: str):
        url = url.lstrip("https://").lstrip("www.").rstrip("/")
        return url.split("?", 1)[0]

    def _url_type(self) -> URLType:
        if not check_domain_validity(self.url):
            raise ValueError("Invalid URL")
        if "/v/" in self.url:
            self.video_uid = self.url.rsplit("/", 1)[-1]
            return URLType.VIDEO
        elif "/playlist/" in self.url:
            self.playlist_id = self.url.rsplit("/", 1)[-1]
            return URLType.PLAYLIST
        else:
            raise ValueError("Invalid URL")

    def _get_available_videos(self) -> list:
        if self.url_type == URLType.VIDEO:
            return [self._get_single_video_qualities(self.video_uid)]
        elif self.url_type == URLType.PLAYLIST:
            click.echo("Loading playlist videos")
            all_videos = []
            playlist_data = self._make_request(
                f"{API_BASE_URL}/video/playlist/one/playlist_id/{self.playlist_id}"
            )
            video_urls = [
                item
                for item in playlist_data["included"]
                if item["type"] == "Video"  # noqa
            ]

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(
                        self._get_single_video_qualities,
                        video["attributes"]["uid"],
                        self.playlist_id,
                    )
                    for video in video_urls
                ]

            for future in as_completed(futures):
                all_videos.append(future.result())

            return all_videos

    def _get_single_video_qualities(self, video_uid, playlist_id=None):
        query = f"?playlist={playlist_id}&pr=1&mf=1" if playlist_id else ""
        video_data = self._make_request(
            f"{API_BASE_URL}/video/video/show/videohash/{video_uid}{query}"
        )
        video_attrs = video_data["data"]["attributes"]
        return [
            {
                "title": video_attrs["title"],
                "profile": attr.get("profile"),
                "url": attr.get("urls")[0],
            }
            for attr in video_attrs["file_link_all"]
        ]

    def _get_available_qualities(self):
        qualities = set(
            video_quality.get("profile")
            for video in self.videos
            for video_quality in video
        )
        return sorted(qualities, key=lambda x: int(x[:-1]))

    def default_quality(self):
        return (
            VideoQuality.HD.value
            if VideoQuality.HD.value in self.qualities
            else self.qualities[-1]
        )

    def find_closest_quality(self, video_list, target_quality):
        exact_quality_videos = [
            video for video in video_list if video["profile"] == target_quality
        ]
        if exact_quality_videos:
            return exact_quality_videos[0]

        video_qualities = [
            int(video["profile"][:-1]) for video in video_list
        ]  # Extract the qualities and convert to integers
        closest_quality = min(
            video_qualities, key=lambda x: abs(x - int(target_quality[:-1]))
        )

        for video in video_list:
            if video["profile"] == str(closest_quality) + "p":
                return video

    def download(self, quality: str):
        for video_qualities in self.videos:
            video = self.find_closest_quality(video_qualities, quality)
            self._download_video(video)

    def _download_video(self, video):
        url = video.get("url")
        title = video.get("title")
        click.echo(f"{title}\n{url}")
        file_name = self.file_name or video.get("title")
        output_file = f"{file_name}.{self._get_file_format(url)}"
        # Check if file already exists
        if os.path.isfile(output_file):
            # Create a hash of the filename
            hash_object = hashlib.md5(output_file.encode())
            hex_dig = hash_object.hexdigest()
            # Append the hash to the filename
            output_file = f"{hex_dig}{output_file}"
        wget.download(url, out=output_file)

    @staticmethod
    def _get_file_format(url):
        return urlparse(url).path.rsplit(".", 1)[-1]

    @staticmethod
    def _make_request(url):
        """Make an HTTP GET request using pycurl."""
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, url)
        headers = prepare_headers()
        curl.setopt(curl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
        curl.setopt(curl.WRITEDATA, buffer)
        curl.perform()
        curl.close()
        response_data = buffer.getvalue().decode("utf-8")
        return json.loads(response_data)
```

---

### Key Changes:
1. Added `_make_request` method to handle HTTP GET requests using `pycurl`.
2. Replaced all `requests.get` calls with `_make_request`.
3. Converted headers to the format required by `pycurl` in `_make_request`.