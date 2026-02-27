### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Asynchronous Programming**: `aiohttp` is an asynchronous library, so all functions that make HTTP requests were converted to asynchronous functions using `async def`.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` for making requests. A session was created and used for all HTTP requests.
3. **Awaiting Responses**: The `requests.get` calls were replaced with `session.get` and the responses were awaited using `await`.
4. **JSON Parsing**: The `r.json()` method in `requests` was replaced with `await r.json()` in `aiohttp`.
5. **Error Handling**: The `ok` attribute in `requests` was replaced with `r.status` to check the HTTP status code.
6. **Text Responses**: The `r.text` method in `requests` was replaced with `await r.text()` in `aiohttp`.
7. **Loop Management**: Since `aiohttp` is asynchronous, the `while` loops were adjusted to work with asynchronous calls.

### Modified Code
```python
import logging
import aiohttp
import asyncio

from common.helpers import get_version

api_base_url = "https://psapi.nrk.no"
headers = {
    "User-Agent": f"nrk-pod-feeder {get_version()}"
}

async def get_all_podcast_episodes_all_seasons(podcast_id, metadata):
    episodes = []

    async with aiohttp.ClientSession(headers=headers) as session:
        for season in metadata["_links"]["seasons"]:
            name = season["name"]
            logging.info(f"  Fetching episodes from season {name}")

            season_episodes = await get_all_podcast_episodes(session, podcast_id, name)
            for episode in season_episodes:
                episodes.append(episode)
        
    return episodes

async def get_all_podcast_episodes(session, podcast_id, season=None):
    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/episodes?page=1&pageSize=30&sort=asc"

    if season:
        url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/seasons/{season}?page=1&pageSize=30&sort=asc"

    episodes = []
    while True:
        async with session.get(url) as r:
            if r.status != 200:
                logging.info(f"Unable to fetch podcast episodes ({url} returned {r.status})")
                return None

            data = await r.json()
            if season:
                for episode in data["_embedded"]["episodes"]["_embedded"]["episodes"]:
                    episodes.append(episode)
            else:
                for episode in data["_embedded"]["episodes"]:
                    episodes.append(episode)
            
            if "next" not in data["_links"]:
                break

            url = api_base_url + data["_links"]["next"]["href"]

    return episodes

async def get_podcast_episodes(podcast_id, season=None, format="json"):
    logging.info(f"Fetching episodes for podcast {podcast_id} ({season})...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/episodes?page=1&pageSize=10&sort=desc"
    if season:
        url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/seasons/{season}?page=1&pageSize=10&sort=desc"

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as r:
            if r.status != 200:
                logging.info(f"Unable to fetch podcast episodes ({url} returned {r.status})")
                return None

            if format == "text":
                return await r.text()

            data = await r.json()
            if season:
                return data["_embedded"]["episodes"]["_embedded"]["episodes"]

            return data["_embedded"]["episodes"]

async def get_episode_manifest(podcast_id, episode_id, format="json"):
    logging.debug(f"  Fetching assets for episode {episode_id}...")

    url = f"{api_base_url}/playback/manifest/podcast/{podcast_id}/{episode_id}"
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as r:
            if r.status != 200:
                logging.info(f"  Unable to fetch episode manifest ({url} returned {r.status})")
                return None

            if format == "text":
                return await r.text()

            return await r.json()

async def get_podcast_metadata(podcast_id, format="json"):
    logging.debug(f"Fetching metadata for podcast {podcast_id}...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}"
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as r:
            if r.status != 200:
                logging.info(f"Unable to fetch podcast metadata ({url} returned {r.status})")
                return None

            if format == "text":
                return await r.text()

            return await r.json()

async def get_all_podcasts():
    url = f"{api_base_url}/radio/search/categories/podcast?take=1000"

    podcasts = {}
    series_c = 0

    async with aiohttp.ClientSession(headers=headers) as session:
        while True:
            async with session.get(url) as r:
                if r.status != 200:
                    logging.error(f"Unable to fetch podcasts ({url} returned {r.status})")
                    return None

                data = await r.json()
                for series in data["series"]:
                    if series['type'] != "podcast":
                        continue

                    logging.debug(f"Found seriesId {series['title']} ({series['seriesId']})")

                    podcasts[series['seriesId']] = {
                        "seriesId": series['seriesId'],
                        "title": series['title'],
                    }

                    series_c += 1
                
                if "next" not in data["_links"]:
                    break

                url = api_base_url + data["_links"]["next"]["href"]

    logging.info(f"Discovered {len(podcasts)} podcast(s) in a total of {series_c} items in search result")
    return podcasts
```

### Notes
- All functions that make HTTP requests are now asynchronous (`async def`).
- The `aiohttp.ClientSession` is used for managing HTTP requests, and it is properly closed after use with `async with`.
- The `await` keyword is used to handle asynchronous operations like fetching responses and parsing JSON or text.
- The overall structure and logic of the code remain unchanged to ensure compatibility with the rest of the application.