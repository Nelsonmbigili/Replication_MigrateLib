import pytest

@pytest.fixture(autouse=True)
def pyopenssl_inject_into_urllib3():
    try:
        yield
    finally:
        pass
