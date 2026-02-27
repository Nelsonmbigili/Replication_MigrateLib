### Explanation of Changes
The `requests_futures` library is an extension of the `requests` library that provides asynchronous capabilities by using Python's `concurrent.futures`. To migrate the code:
1. **Import Change**: Replaced `import requests` with `from requests_futures.sessions import FuturesSession`.
2. **Session Initialization**: Created a `FuturesSession` object to handle asynchronous requests.
3. **Request Method Changes**: Replaced `requests.get` with `session.get` to use the `FuturesSession` object.
4. **Response Handling**: Since `requests_futures` returns a `Future` object, `.result()` is called on the response to block and retrieve the actual response object (to maintain synchronous behavior in the existing code).

The rest of the code remains unchanged to ensure compatibility with the existing application.

---

### Modified Code
```python
import logging
from requests_futures.sessions import FuturesSession

from common.helpers import get_version

api_base_url = "https://psapi.nrk.no"
headers = {
    "User-Agent": f"nrk-pod-feeder {get_version()}"
}

# Initialize a FuturesSession
session = FuturesSession()

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
        r = session.get(url, headers=headers).result()  # Use session.get and call .result() to get the response
        if not r.ok:
            logging.info(f"Unable to fetch podcast episodes ({url} returned {r.status_code})")
            return None

        if season:
             for episode in r.json()["_embedded"]["episodes"]["_embedded"]["episodes"]:
                 episodes.append(episode)
        else:
            for episode in r.json()["_embedded"]["episodes"]:
                episodes.append(episode)
        
        if not "next" in r.json()["_links"]:
            break

        url = api_base_url + r.json()["_links"]["next"]["href"]

    return episodes

def get_podcast_episodes(podcast_id, season = None, format = "json"):
    logging.info(f"Fetching episodes for podcast {podcast_id} ({season})...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/episodes?page=1&pageSize=10&sort=desc"
    if season:
        url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/seasons/{season}?page=1&pageSize=10&sort=desc"

    r = session.get(url, headers=headers).result()  # Use session.get and call .result() to get the response
    if not r.ok:
        logging.info(f"Unable to fetch podcast episodes ({url} returned {r.status_code})")
        return None

    if format == "text":
        return r.text

    if season:
        return r.json()["_embedded"]["episodes"]["_embedded"]["episodes"]

    return r.json()["_embedded"]["episodes"]

def get_episode_manifest(podcast_id, episode_id, format = "json"):
    logging.debug(f"  Fetching assets for episode {episode_id}...")

    url = f"{api_base_url}/playback/manifest/podcast/{podcast_id}/{episode_id}"
    r = session.get(url, headers=headers).result()  # Use session.get and call .result() to get the response

    if not r.ok:
        logging.info(f"  Unable to fetch episode manifest ({url} returned {r.status_code})")
        return None

    if format == "text":
        return r.text

    return r.json()

def get_podcast_metadata(podcast_id, format = "json"):
    logging.debug(f"Fetching metadata for podcast {podcast_id}...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}"
    r = session.get(url, headers=headers).result()  # Use session.get and call .result() to get the response

    if not r.ok:
        logging.info(f"Unable to fetch podcast metadata ({url} returned {r.status_code})")
        return None

    if format == "text":
        return r.text

    return r.json()

def get_all_podcasts():
    url = f"{api_base_url}/radio/search/categories/podcast?take=1000"

    podcasts = {}
    series_c = 0

    while True:
        r = session.get(url, headers=headers).result()  # Use session.get and call .result() to get the response
        if not r.ok:
            logging.error(f"Unable to fetch podcasts ({url} returned {r.status_code})")
            return None

        for series in r.json()["series"]:
            if series['type'] != "podcast":
                continue

            logging.debug(f"Found seriesId {series['title']} ({series['seriesId']})")

            podcasts[series['seriesId']] = {
                "seriesId" : series['seriesId'],
                "title" : series['title'],
            }

            series_c+=1
        
        if not "next" in r.json()["_links"]:
            break

        url = api_base_url + r.json()["_links"]["next"]["href"]

    logging.info(f"Discovered {len(podcasts)} podcast(s) in a total of {series_c} items in search result")
    return podcasts
```