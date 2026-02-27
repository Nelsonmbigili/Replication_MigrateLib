### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Asynchronous Programming**: Since `aiohttp` is an asynchronous library, the methods that make HTTP requests (`_get_available_videos`, `_get_single_video_qualities`) were converted to asynchronous functions using `async def`.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` for making requests. A session is created and reused for all requests to avoid creating a new session for each request.
3. **Awaiting Requests**: The `requests.get` calls were replaced with `await session.get` to make asynchronous HTTP requests.
4. **JSON Parsing**: The `.json()` method in `aiohttp` is an asynchronous coroutine, so it was replaced with `await response.json()`.
5. **ThreadPoolExecutor**: Since `aiohttp` is asynchronous, the `ThreadPoolExecutor` was replaced with `asyncio.gather` to handle multiple asynchronous tasks concurrently.
6. **Initialization of `aiohttp.ClientSession`**: A session is initialized in the `Downloader` class and closed explicitly when the object is deleted.

### Modified Code
```python
import hashlib
import os
import asyncio
from enum import Enum
from urllib.parse import urlparse

import click
import aiohttp
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
        self.session = aiohttp.ClientSession()  # Initialize aiohttp session
        self.videos = asyncio.run(self._get_available_videos())
        self.qualities = self._get_available_qualities()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def __del__(self):
        # Ensure the session is closed when the object is deleted
        if not self.session.closed:
            asyncio.run(self.session.close())

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

    async def _get_available_videos(self) -> list:
        if self.url_type == URLType.VIDEO:
            return [await self._get_single_video_qualities(self.video_uid)]
        elif self.url_type == URLType.PLAYLIST:
            click.echo("Loading playlist videos")
            all_videos = []
            async with self.session.get(
                f"{API_BASE_URL}/video/playlist/one/playlist_id/{self.playlist_id}",
                headers=prepare_headers(),
            ) as response:
                playlist_data = await response.json()
            video_urls = [
                item
                for item in playlist_data["included"]
                if item["type"] == "Video"
            ]

            tasks = [
                self._get_single_video_qualities(
                    video["attributes"]["uid"], self.playlist_id
                )
                for video in video_urls
            ]
            all_videos = await asyncio.gather(*tasks)
            return all_videos

    async def _get_single_video_qualities(self, video_uid, playlist_id=None):
        query = f"?playlist={playlist_id}&pr=1&mf=1" if playlist_id else ""
        async with self.session.get(
            f"{API_BASE_URL}/video/video/show/videohash/{video_uid}{query}",
            headers=prepare_headers(),
        ) as response:
            video_data = await response.json()
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

### Key Notes
- The `Downloader` class now uses `aiohttp.ClientSession` for all HTTP requests.
- The `_get_available_videos` and `_get_single_video_qualities` methods are now asynchronous.
- The `asyncio.gather` function is used to handle multiple asynchronous tasks concurrently.
- The `aiohttp.ClientSession` is explicitly closed when the `Downloader` object is deleted or goes out of scope.