### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, several changes were made:

1. **Importing PyCurl**: The `requests` library was replaced with `pycurl`. The `pycurl` library requires a different approach to handle HTTP requests.
  
2. **Creating a Curl Object**: Instead of using `requests.get()`, a `pycurl.Curl` object is created to handle the HTTP request.

3. **Setting Options**: The options for the request (like URL, headers, etc.) are set using the `setopt` method of the `Curl` object.

4. **Handling Response**: The response from the server is captured using a `BytesIO` object, which allows us to read the response data after the request is executed.

5. **Error Handling**: The error handling is adjusted to check for HTTP response codes using the `getinfo` method of the `Curl` object.

6. **JSON Parsing**: The response data is decoded and parsed using the `json` module, as `pycurl` does not automatically handle JSON responses.

Here is the modified code:

```python
import logging
import pycurl
import json
from io import BytesIO
from common.helpers import get_version

api_base_url = "https://psapi.nrk.no"
headers = [
    f"User-Agent: nrk-pod-feeder {get_version()}"
]

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
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.HTTPHEADER, headers)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()

        http_code = c.getinfo(c.RESPONSE_CODE)
        c.close()

        if http_code != 200:
            logging.info(f"Unable to fetch podcast episodes ({url} returned {http_code})")
            return None

        response_data = buffer.getvalue().decode('utf-8')
        if season:
            for episode in json.loads(response_data)["_embedded"]["episodes"]["_embedded"]["episodes"]:
                episodes.append(episode)
        else:
            for episode in json.loads(response_data)["_embedded"]["episodes"]:
                episodes.append(episode)
        
        if not "next" in json.loads(response_data)["_links"]:
            break

        url = api_base_url + json.loads(response_data)["_links"]["next"]["href"]

    return episodes

def get_podcast_episodes(podcast_id, season = None, format = "json"):
    logging.info(f"Fetching episodes for podcast {podcast_id} ({season})...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/episodes?page=1&pageSize=10&sort=desc"
    if season:
        url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/seasons/{season}?page=1&pageSize=10&sort=desc"

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()

    http_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if http_code != 200:
        logging.info(f"Unable to fetch podcast episodes ({url} returned {http_code})")
        return None

    response_data = buffer.getvalue().decode('utf-8')

    if format == "text":
        return response_data

    if season:
        return json.loads(response_data)["_embedded"]["episodes"]["_embedded"]["episodes"]

    return json.loads(response_data)["_embedded"]["episodes"]

def get_episode_manifest(podcast_id, episode_id, format = "json"):
    logging.debug(f"  Fetching assets for episode {episode_id}...")

    url = f"{api_base_url}/playback/manifest/podcast/{podcast_id}/{episode_id}"
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()

    http_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if http_code != 200:
        logging.info(f"  Unable to fetch episode manifest ({url} returned {http_code})")
        return None

    response_data = buffer.getvalue().decode('utf-8')

    if format == "text":
        return response_data

    return json.loads(response_data)

def get_podcast_metadata(podcast_id, format = "json"):
    logging.debug(f"Fetching metadata for podcast {podcast_id}...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}"
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()

    http_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if http_code != 200:
        logging.info(f"Unable to fetch podcast metadata ({url} returned {http_code})")
        return None

    response_data = buffer.getvalue().decode('utf-8')

    if format == "text":
        return response_data

    return json.loads(response_data)

def get_all_podcasts():
    url = f"{api_base_url}/radio/search/categories/podcast?take=1000"

    podcasts = {}
    series_c = 0

    while True:
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.HTTPHEADER, headers)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()

        http_code = c.getinfo(c.RESPONSE_CODE)
        c.close()

        if http_code != 200:
            logging.error(f"Unable to fetch podcasts ({url} returned {http_code})")
            return None

        response_data = buffer.getvalue().decode('utf-8')
        for series in json.loads(response_data)["series"]:
            if series['type'] != "podcast":
                continue

            logging.debug(f"Found seriesId {series['title']} ({series['seriesId']})")

            podcasts[series['seriesId']] = {
                "seriesId" : series['seriesId'],
                "title" : series['title'],
            }

            series_c+=1
        
        if not "next" in json.loads(response_data)["_links"]:
            break

        url = api_base_url + json.loads(response_data)["_links"]["next"]["href"]

    logging.info(f"Discovered {len(podcasts)} podcast(s) in a total of {series_c} items in search result")
    return podcasts
```