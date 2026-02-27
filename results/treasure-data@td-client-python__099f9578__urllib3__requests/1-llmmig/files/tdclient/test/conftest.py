import pytest


@pytest.fixture(autouse=True)
def pyopenssl_inject_into_requests():
    # No equivalent injection/extraction is needed for the 'requests' library.
    try:
        yield
    finally:
        pass
