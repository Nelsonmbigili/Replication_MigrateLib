To migrate the provided code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Asynchronous Functions**: The functions that make HTTP requests were modified to be asynchronous. This involves using the `async def` syntax and the `await` keyword when calling asynchronous methods.
  
2. **Session Management**: Instead of calling `requests.get()`, we create an `aiohttp.ClientSession` and use `session.get()` to perform the requests. This is necessary because `aiohttp` requires a session to manage connections.

3. **Response Handling**: The response from `aiohttp` is handled asynchronously, so we need to await the response and then call `.json()` on it to parse the JSON data.

4. **Error Handling**: The error handling remains similar, but we need to ensure that we await the response before checking its status.

5. **Event Loop**: Since the functions are now asynchronous, they need to be called within an event loop. This is typically done using `asyncio.run()` or similar constructs in the main application.

Here is the modified code using `aiohttp`:

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

    for season in metadata["_links"]["seasons"]:
        name = season["name"]
        logging.info(f"  Fetching episodes from season {name}")

        season_episodes = await get_all_podcast_episodes(podcast_id, name)
        for episode in season_episodes:
            episodes.append(episode)
        
    return episodes

async def get_all_podcast_episodes(podcast_id, season = None):
    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/episodes?page=1&pageSize=30&sort=asc"

    if season:
        url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/seasons/{season}?page=1&pageSize=30&sort=asc"

    episodes = []
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers) as r:
                if r.status != 200:
                    logging.info(f"Unable to fetch podcast episodes ({url} returned {r.status})")
                    return None

                json_response = await r.json()
                if season:
                    for episode in json_response["_embedded"]["episodes"]["_embedded"]["episodes"]:
                        episodes.append(episode)
                else:
                    for episode in json_response["_embedded"]["episodes"]:
                        episodes.append(episode)
                
                if "next" not in json_response["_links"]:
                    break

                url = api_base_url + json_response["_links"]["next"]["href"]

    return episodes

async def get_podcast_episodes(podcast_id, season = None, format = "json"):
    logging.info(f"Fetching episodes for podcast {podcast_id} ({season})...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/episodes?page=1&pageSize=10&sort=desc"
    if season:
        url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/seasons/{season}?page=1&pageSize=10&sort=desc"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
            if r.status != 200:
                logging.info(f"Unable to fetch podcast episodes ({url} returned {r.status})")
                return None

            if format == "text":
                return await r.text()

            if season:
                return (await r.json())["_embedded"]["episodes"]["_embedded"]["episodes"]

            return (await r.json())["_embedded"]["episodes"]

async def get_episode_manifest(podcast_id, episode_id, format = "json"):
    logging.debug(f"  Fetching assets for episode {episode_id}...")

    url = f"{api_base_url}/playback/manifest/podcast/{podcast_id}/{episode_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
            if r.status != 200:
                logging.info(f"  Unable to fetch episode manifest ({url} returned {r.status})")
                return None

            if format == "text":
                return await r.text()

            return await r.json()

async def get_podcast_metadata(podcast_id, format = "json"):
    logging.debug(f"Fetching metadata for podcast {podcast_id}...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
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

    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers) as r:
                if r.status != 200:
                    logging.error(f"Unable to fetch podcasts ({url} returned {r.status})")
                    return None

                json_response = await r.json()
                for series in json_response["series"]:
                    if series['type'] != "podcast":
                        continue

                    logging.debug(f"Found seriesId {series['title']} ({series['seriesId']})")

                    podcasts[series['seriesId']] = {
                        "seriesId" : series['seriesId'],
                        "title" : series['title'],
                    }

                    series_c += 1
                
                if "next" not in json_response["_links"]:
                    break

                url = api_base_url + json_response["_links"]["next"]["href"]

    logging.info(f"Discovered {len(podcasts)} podcast(s) in a total of {series_c} items in search result")
    return podcasts
```

This code now uses `aiohttp` for asynchronous HTTP requests, allowing for non-blocking I/O operations, which is beneficial for applications that require high concurrency.