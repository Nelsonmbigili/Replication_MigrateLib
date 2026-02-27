from nyaapy.nyaasi.nyaa import Nyaa
from nyaapy.torrent import Torrent
import pytest


@pytest.mark.asyncio
async def test_nyaa_last_uploads():
    request = await Nyaa.last_uploads(number_of_results=10)
    torrent = request[0]

    assert isinstance(torrent, Torrent) == True
    assert len(request) == 10


@pytest.mark.asyncio
async def test_nyaa_search():
    request = await Nyaa.search(keyword="koe no katachi")
    torrent = request[0]

    assert isinstance(torrent, Torrent) == True


@pytest.mark.asyncio
async def test_nyaa_get_single():
    request = await Nyaa.get(view_id="1847113")

    assert isinstance(request, Torrent) == True


@pytest.mark.asyncio
async def test_nyaa_get_from_user():
    request = await Nyaa.get_from_user(username="Erai-raws")
    torrent = request[0]

    assert isinstance(torrent, Torrent) == True
    assert len(request) <= 75
