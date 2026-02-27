"""
tests/test_exceptions
~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

import comics
from comics import InvalidDateError, InvalidEndpointError


def test_invalid_endpoint():
    """Tests proper raise of `InvalidEndpointError` when using an endpoint that does
    not exist in GoComics."""
    with pytest.raises(InvalidEndpointError):
        comics.search("invalid_endpoint").date("2000-01-01")


@pytest.mark.asyncio
async def test_date_before_creation():
    """Tests proper raise of `InvalidDateError` when using date that is before the
    comic's creation date."""
    with pytest.raises(InvalidDateError):
        await comics.search("calvinandhobbes").date("1900-01-01")


@pytest.mark.asyncio
async def test_invalid_date():
    """Tests proper raise of `InvalidDateError` when using an invalid / unregistered
    date for the comic of interest."""
    ch = await comics.search("calvinandhobbes").date("2050-01-01")
    with pytest.raises(InvalidDateError):
        await ch.show()
