import logging
import treq

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

async def get_all_podcast_episodes(podcast_id, season=None):
    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/episodes?page=1&pageSize=30&sort=asc"

    if season:
        url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/seasons/{season}?page=1&pageSize=30&sort=asc"

    episodes = []
    while True:
        r = await treq.get(url, headers=headers)
        if r.code != 200:
            logging.info(f"Unable to fetch podcast episodes ({url} returned {r.code})")
            return None

        response_json = await r.json()
        if season:
            for episode in response_json["_embedded"]["episodes"]["_embedded"]["episodes"]:
                episodes.append(episode)
        else:
            for episode in response_json["_embedded"]["episodes"]:
                episodes.append(episode)
        
        if "next" not in response_json["_links"]:
            break

        url = api_base_url + response_json["_links"]["next"]["href"]

    return episodes

async def get_podcast_episodes(podcast_id, season=None, format="json"):
    logging.info(f"Fetching episodes for podcast {podcast_id} ({season})...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/episodes?page=1&pageSize=10&sort=desc"
    if season:
        url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}/seasons/{season}?page=1&pageSize=10&sort=desc"

    r = await treq.get(url, headers=headers)
    if r.code != 200:
        logging.info(f"Unable to fetch podcast episodes ({url} returned {r.code})")
        return None

    if format == "text":
        return await r.text()

    response_json = await r.json()
    if season:
        return response_json["_embedded"]["episodes"]["_embedded"]["episodes"]

    return response_json["_embedded"]["episodes"]

async def get_episode_manifest(podcast_id, episode_id, format="json"):
    logging.debug(f"  Fetching assets for episode {episode_id}...")

    url = f"{api_base_url}/playback/manifest/podcast/{podcast_id}/{episode_id}"
    r = await treq.get(url, headers=headers)

    if r.code != 200:
        logging.info(f"  Unable to fetch episode manifest ({url} returned {r.code})")
        return None

    if format == "text":
        return await r.text()

    return await r.json()

async def get_podcast_metadata(podcast_id, format="json"):
    logging.debug(f"Fetching metadata for podcast {podcast_id}...")

    url = f"{api_base_url}/radio/catalog/podcast/{podcast_id}"
    r = await treq.get(url, headers=headers)

    if r.code != 200:
        logging.info(f"Unable to fetch podcast metadata ({url} returned {r.code})")
        return None

    if format == "text":
        return await r.text()

    return await r.json()

async def get_all_podcasts():
    url = f"{api_base_url}/radio/search/categories/podcast?take=1000"

    podcasts = {}
    series_c = 0

    while True:
        r = await treq.get(url, headers=headers)
        if r.code != 200:
            logging.error(f"Unable to fetch podcasts ({url} returned {r.code})")
            return None

        response_json = await r.json()
        for series in response_json["series"]:
            if series['type'] != "podcast":
                continue

            logging.debug(f"Found seriesId {series['title']} ({series['seriesId']})")

            podcasts[series['seriesId']] = {
                "seriesId": series['seriesId'],
                "title": series['title'],
            }

            series_c += 1
        
        if "next" not in response_json["_links"]:
            break

        url = api_base_url + response_json["_links"]["next"]["href"]

    logging.info(f"Discovered {len(podcasts)} podcast(s) in a total of {series_c} items in search result")
    return podcasts
