import logging
import urllib3
import json

from common.helpers import get_version

api_base_url = "https://psapi.nrk.no"
headers = {
    "User-Agent": f"nrk-pod-feeder {get_version()}"
}

# Create a connection pool manager
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
        r = http.request("GET", url, headers=headers)
        if r.status != 200:
            logging.info(f"Unable to fetch podcast episodes ({url} returned {r.status})")
            return None

        response_data = json.loads(r.data.decode("utf-8"))
        if season:
             for episode in response_data["_embedded"]["episodes"]["_embedded"]["episodes"]:
                 episodes.append(episode)
        else:
            for episode in response_data["_embedded"]["episodes"]:
                episodes.append(episode)
        
        if not "next" in response_data["_links"]:
            break

        url = api_base_url + response_data["_links"]["next"]["href"]

    return episodes

def get_podcast_episodes(podcast_id, season = None, format = "json"):
    logging.info(f"Fetching episodes for podcast {podcast_id} ({season})...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/episodes?page=1&pageSize=10&sort=desc"
    if season:
        url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/seasons/{season}?page=1&pageSize=10&sort=desc"

    r = http.request("GET", url, headers=headers)
    if r.status != 200:
        logging.info(f"Unable to fetch podcast episodes ({url} returned {r.status})")
        return None

    response_data = json.loads(r.data.decode("utf-8"))
    if format == "text":
        return r.data.decode("utf-8")

    if season:
        return response_data["_embedded"]["episodes"]["_embedded"]["episodes"]

    return response_data["_embedded"]["episodes"]

def get_episode_manifest(podcast_id, episode_id, format = "json"):
    logging.debug(f"  Fetching assets for episode {episode_id}...")

    url = f"{api_base_url}/playback/manifest/podcast/{podcast_id}/{episode_id}"
    r = http.request("GET", url, headers=headers)

    if r.status != 200:
        logging.info(f"  Unable to fetch episode manifest ({url} returned {r.status})")
        return None

    if format == "text":
        return r.data.decode("utf-8")

    return json.loads(r.data.decode("utf-8"))

def get_podcast_metadata(podcast_id, format = "json"):
    logging.debug(f"Fetching metadata for podcast {podcast_id}...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}"
    r = http.request("GET", url, headers=headers)

    if r.status != 200:
        logging.info(f"Unable to fetch podcast metadata ({url} returned {r.status})")
        return None

    if format == "text":
        return r.data.decode("utf-8")

    return json.loads(r.data.decode("utf-8"))

def get_all_podcasts():
    url = f"{api_base_url}/radio/search/categories/podcast?take=1000"

    podcasts = {}
    series_c = 0

    while True:
        r = http.request("GET", url, headers=headers)
        if r.status != 200:
            logging.error(f"Unable to fetch podcasts ({url} returned {r.status})")
            return None

        response_data = json.loads(r.data.decode("utf-8"))
        for series in response_data["series"]:
            if series['type'] != "podcast":
                continue

            logging.debug(f"Found seriesId {series['title']} ({series['seriesId']})")

            podcasts[series['seriesId']] = {
                "seriesId" : series['seriesId'],
                "title" : series['title'],
            }

            series_c+=1
        
        if not "next" in response_data["_links"]:
            break

        url = api_base_url + response_data["_links"]["next"]["href"]

    logging.info(f"Discovered {len(podcasts)} podcast(s) in a total of {series_c} items in search result")
    return podcasts
