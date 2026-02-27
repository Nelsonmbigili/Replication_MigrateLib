import logging

from . import psapi
import pytest

@pytest.mark.asyncio
async def test_get_podcast_metadata():
    podcast_id = "kongerekka"

    metadata = await psapi.get_podcast_metadata(podcast_id)

    assert "title" in metadata["series"]["titles"]
    assert "url" in metadata["series"]["squareImage"][4]
    assert "href" in metadata["_links"]["share"]
    assert "name" in metadata["_links"]["seasons"][0]

@pytest.mark.asyncio
async def test_get_podcast_episodes():
    podcast_id = "berrum_beyer_snakker_om_greier"

    episodes = await psapi.get_podcast_episodes(podcast_id)

    for episode in episodes:
        assert "title" in episode['titles']
        assert "subtitle" in episode['titles']
        assert "date" in episode
        assert "episodeId" in episode
        assert "durationInSeconds" in episode

    assert len(episodes) == 10

@pytest.mark.asyncio
async def test_get_all_podcast_episodes():
    podcast_id = "kongerekka"

    episodes = await psapi.get_all_podcast_episodes(podcast_id)
    
    for episode in episodes:
        assert "title" in episode['titles']
        assert "subtitle" in episode['titles']
        assert "date" in episode
        assert "episodeId" in episode
        assert "durationInSeconds" in episode

    assert len(episodes) > 0

@pytest.mark.asyncio
async def test_get_all_podcast_episodes_all_seasons():
    podcast_id = "klassikere_fra_p3-arkivet"

    metadata = await psapi.get_podcast_metadata(podcast_id)
    episodes = await psapi.get_all_podcast_episodes_all_seasons(podcast_id, metadata)
    
    for episode in episodes:
        assert "title" in episode['titles']
        assert "subtitle" in episode['titles']
        assert "date" in episode
        assert "episodeId" in episode
        assert "durationInSeconds" in episode

    assert len(episodes) > 0

@pytest.mark.asyncio
async def test_get_episode_manifest():
    podcast_id = "kongerekka"

    episodes = await psapi.get_podcast_episodes(podcast_id)
    manifest = await psapi.get_episode_manifest(podcast_id, episodes[0]["episodeId"])

    assert "mimeType" in manifest["playable"]["assets"][0]
    assert "url" in manifest["playable"]["assets"][0]

@pytest.mark.asyncio
async def test_get_latest_podcast_season():
    podcast_id = "kongerekka"

    metadata = await psapi.get_podcast_metadata(podcast_id)
    latest_season = metadata["_links"]["seasons"][0]["name"]

    assert latest_season == "2023"

@pytest.mark.asyncio
async def test_get_podcast_episodes_by_season():
    podcast_id = "kongerekka"
    season_id = "2020"

    episodes = await psapi.get_podcast_episodes(podcast_id, season_id)

    assert len(episodes) == 10

@pytest.mark.asyncio
async def test_get_all_podcasts():
    podcasts = await psapi.get_all_podcasts()

    for podcast_k, podcast in podcasts.items():
        assert "seriesId" in podcast
        assert "title" in podcast
