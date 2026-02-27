### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created a `FuturesSession` object to handle asynchronous requests.
3. **Asynchronous Requests**: Replaced synchronous `requests.get` calls with asynchronous `session.get` calls. The `FuturesSession` returns a `Future` object, so `.result()` is used to retrieve the response when needed.
4. **ThreadPoolExecutor Removal**: Since `requests_futures` handles asynchronous requests internally, the `ThreadPoolExecutor` was removed for the playlist video fetching logic.

### Modified Code:
```python
import hashlib
import os
from concurrent.futures import as_completed
from enum import Enum
from urllib.parse import urlparse

import click
from requests_futures.sessions import FuturesSession
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
        self.session = FuturesSession()  # Initialize FuturesSession

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
            playlist_response = self.session.get(
                f"{API_BASE_URL}/video/playlist/one/playlist_id/{self.playlist_id}",
                headers=prepare_headers(),
            ).result()  # Fetch the response
            playlist_data = playlist_response.json()
            video_urls = [
                item
                for item in playlist_data["included"]
                if item["type"] == "Video"
            ]

            # Use FuturesSession for asynchronous requests
            futures = [
                self.session.get(
                    f"{API_BASE_URL}/video/video/show/videohash/{video['attributes']['uid']}?playlist={self.playlist_id}&pr=1&mf=1",
                    headers=prepare_headers(),
                )
                for video in video_urls
            ]

            for future in as_completed(futures):
                video_data = future.result().json()
                all_videos.append(self._parse_video_data(video_data))

            return all_videos

    def _get_single_video_qualities(self, video_uid, playlist_id=None):
        query = f"?playlist={playlist_id}&pr=1&mf=1" if playlist_id else ""
        video_response = self.session.get(
            f"{API_BASE_URL}/video/video/show/videohash/{video_uid}{query}",
            headers=prepare_headers(),
        ).result()  # Fetch the response
        video_data = video_response.json()
        return self._parse_video_data(video_data)

    @staticmethod
    def _parse_video_data(video_data):
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
- Replaced `requests.get` with `session.get` from `FuturesSession`.
- Used `.result()` to retrieve the response from the `Future` object.
- Removed `ThreadPoolExecutor` since `requests_futures` handles asynchronous requests internally.