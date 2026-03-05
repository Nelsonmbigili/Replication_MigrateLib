import pytest

try:
    import httpx
except ImportError:
    httpx = None  # noqa: E731


@pytest.fixture(autouse=True)
def pyopenssl_inject_into_urllib3():
    # No need to inject or extract anything for httpx
    try:
        yield
    finally:
        pass  # No cleanup needed for httpx
