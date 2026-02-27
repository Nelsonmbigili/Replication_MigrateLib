### Explanation of Changes:
To migrate the code from the `requests` library to `urllib3`, the following changes were made:
1. **Replaced `requests.get` with `urllib3.PoolManager`**:
   - `urllib3` does not have a direct `get` method like `requests`. Instead, we use a `PoolManager` to make HTTP requests.
   - The `PoolManager` is initialized once and reused for all HTTP requests.
2. **Modified JSON Parsing**:
   - In `requests`, the `.json()` method is used to parse JSON responses. In `urllib3`, the response body is accessed via `response.data`, which is a byte string. This needs to be decoded and then parsed using the `json.loads` method from the `json` module.
3. **Headers Handling**:
   - Headers are passed as a dictionary in `urllib3` requests, similar to `requests`.
4. **Error Handling**:
   - `urllib3` does not raise exceptions for HTTP errors by default. To handle HTTP errors, we check the `status` attribute of the response and raise an exception if the status code indicates an error.

### Modified Code:
```python
import hashlib
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from urllib.parse import urlparse

import click
import wget
import urllib3

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
        self.http = urllib3.PoolManager()  # Initialize PoolManager for HTTP requests

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
            response = self.http.request(
                "GET",
                f"{API_BASE_URL}/video/playlist/one/playlist_id/{self.playlist_id}",
                headers=prepare_headers(),
            )
            if response.status != 200:
                raise Exception(f"Failed to fetch playlist data: {response.status}")
            playlist_data = json.loads(response.data.decode("utf-8"))
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
        response = self.http.request(
            "GET",
            f"{API_BASE_URL}/video/video/show/videohash/{video_uid}{query}",
            headers=prepare_headers(),
        )
        if response.status != 200:
            raise Exception(f"Failed to fetch video data: {response.status}")
        video_data = json.loads(response.data.decode("utf-8"))
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
```

### Summary of Changes:
- Replaced `requests.get` with `urllib3.PoolManager().request`.
- Used `json.loads` to parse JSON responses from `urllib3`.
- Added error handling for HTTP status codes using `response.status`.
- Initialized a single `PoolManager` instance for all HTTP requests.