### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`. The `requests` library is a higher-level abstraction over HTTP, while `urllib3` is a lower-level library that requires more manual handling of connections and responses.

2. **Creating a PoolManager**: A `PoolManager` instance was created to manage connections. This is necessary in `urllib3` to handle requests.

3. **Making Requests**: The `requests.get()` method was replaced with `http.request('GET', url, headers=headers)`. The `http` object is an instance of `PoolManager`.

4. **Handling Responses**: The response handling was adjusted to use `response.data` for raw data and `response.json()` for JSON parsing. The `requests` library automatically handles JSON parsing, while `urllib3` requires manual decoding.

5. **Checking Response Status**: The status check was changed from `r.ok` to `response.status == 200`, as `urllib3` does not have the `ok` attribute.

6. **Error Handling**: The error handling was adjusted to check the status code directly.

Here is the modified code:

```python
import logging
import urllib3
import json

from common.helpers import get_version

api_base_url = "https://psapi.nrk.no"
headers = {
    "User-Agent": f"nrk-pod-feeder {get_version()}"
}

http = urllib3.PoolManager()

def get_all_podcast_episodes_all_seasons(podcast_id, metadata):
    episodes = []

    for season in metadata["_links"]["seasons"]:
        name = season["name"]
        logging.info(f"  Fetching episodes from season {name}")

        season_episodes = get_all_podcast_episodes(podcast_id, name)
        for episode in season_episodes:
            episodes.append(episode)
        
    return episodes

def get_all_podcast_episodes(podcast_id, season = None):
    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/episodes?page=1&pageSize=30&sort=asc"

    if season:
        url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/seasons/{season}?page=1&pageSize=30&sort=asc"

    episodes = []
    while True:
        response = http.request('GET', url, headers=headers)
        if response.status != 200:
            logging.info(f"Unable to fetch podcast episodes ({url} returned {response.status})")
            return None

        if season:
            for episode in json.loads(response.data)["_embedded"]["episodes"]["_embedded"]["episodes"]:
                episodes.append(episode)
        else:
            for episode in json.loads(response.data)["_embedded"]["episodes"]:
                episodes.append(episode)
        
        if not "next" in json.loads(response.data)["_links"]:
            break

        url = api_base_url + json.loads(response.data)["_links"]["next"]["href"]

    return episodes

def get_podcast_episodes(podcast_id, season = None, format = "json"):
    logging.info(f"Fetching episodes for podcast {podcast_id} ({season})...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/episodes?page=1&pageSize=10&sort=desc"
    if season:
        url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/seasons/{season}?page=1&pageSize=10&sort=desc"

    response = http.request('GET', url, headers=headers)
    if response.status != 200:
        logging.info(f"Unable to fetch podcast episodes ({url} returned {response.status})")
        return None

    if format == "text":
        return response.data.decode('utf-8')

    if season:
        return json.loads(response.data)["_embedded"]["episodes"]["_embedded"]["episodes"]

    return json.loads(response.data)["_embedded"]["episodes"]

def get_episode_manifest(podcast_id, episode_id, format = "json"):
    logging.debug(f"  Fetching assets for episode {episode_id}...")

    url = f"{api_base_url}/playback/manifest/podcast/{podcast_id}/{episode_id}"
    response = http.request('GET', url, headers=headers)

    if response.status != 200:
        logging.info(f"  Unable to fetch episode manifest ({url} returned {response.status})")
        return None

    if format == "text":
        return response.data.decode('utf-8')

    return json.loads(response.data)

def get_podcast_metadata(podcast_id, format = "json"):
    logging.debug(f"Fetching metadata for podcast {podcast_id}...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}"
    response = http.request('GET', url, headers=headers)

    if response.status != 200:
        logging.info(f"Unable to fetch podcast metadata ({url} returned {response.status})")
        return None

    if format == "text":
        return response.data.decode('utf-8')

    return json.loads(response.data)

def get_all_podcasts():
    url = f"{api_base_url}/radio/search/categories/podcast?take=1000"

    podcasts = {}
    series_c = 0

    while True:
        response = http.request('GET', url, headers=headers)
        if response.status != 200:
            logging.error(f"Unable to fetch podcasts ({url} returned {response.status})")
            return None

        for series in json.loads(response.data)["series"]:
            if series['type'] != "podcast":
                continue

            logging.debug(f"Found seriesId {series['title']} ({series['seriesId']})")

            podcasts[series['seriesId']] = {
                "seriesId" : series['seriesId'],
                "title" : series['title'],
            }

            series_c+=1
        
        if not "next" in json.loads(response.data)["_links"]:
            break

        url = api_base_url + json.loads(response.data)["_links"]["next"]["href"]

    logging.info(f"Discovered {len(podcasts)} podcast(s) in a total of {series_c} items in search result")
    return podcasts
```