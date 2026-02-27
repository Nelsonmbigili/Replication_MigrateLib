import pytest

@pytest.fixture(autouse=True)
def pyopenssl_inject_into_aiohttp():
    # No equivalent injection/extraction needed for aiohttp
    yield
