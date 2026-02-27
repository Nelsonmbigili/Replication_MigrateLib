### Explanation of Changes
To migrate the code from the `requests` library to the `httpx` library, the following changes were made:
1. **Import Change**: Replaced `import requests` with `import httpx`.
2. **HTTP Methods**: Replaced `requests.get` with `httpx.get`. The syntax for `httpx.get` is almost identical to `requests.get`, so no major changes were needed.
3. **Response Handling**: The `httpx` response object is similar to `requests`, so no changes were required for accessing `.ok`, `.json()`, `.text`, or `.status_code`.
4. **Session Management**: Since the code does not use a session object, no changes were needed for session handling.
5. **Behavioral Consistency**: The `httpx` library is asynchronous by default, but the synchronous API (used here) behaves similarly to `requests`.

### Modified Code
Below is the complete code after migrating to `httpx`:

```python
import logging
import httpx

from common.helpers import get_version

api_base_url = "https://psapi.nrk.no"
headers = {
    "User-Agent": f"nrk-pod-feeder {get_version()}"
}

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
        r = httpx.get(url, headers=headers)
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

    r = httpx.get(url, headers=headers)
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
    r = httpx.get(url, headers=headers)

    if not r.ok:
        logging.info(f"  Unable to fetch episode manifest ({url} returned {r.status_code})")
        return None

    if format == "text":
        return r.text

    return r.json()

def get_podcast_metadata(podcast_id, format = "json"):
    logging.debug(f"Fetching metadata for podcast {podcast_id}...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}"
    r = httpx.get(url, headers=headers)

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
        r = httpx.get(url, headers=headers)
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

### Summary
The migration from `requests` to `httpx` was straightforward because both libraries have similar synchronous APIs. The changes were limited to replacing `requests.get` with `httpx.get` and ensuring the rest of the code remained unchanged.