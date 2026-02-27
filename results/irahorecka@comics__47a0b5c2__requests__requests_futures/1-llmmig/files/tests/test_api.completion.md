### Explanation of Changes

To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:

1. **Import Change**: Replaced the `requests` import with `requests_futures`.
2. **Asynchronous Requests**: The `requests_futures` library provides asynchronous capabilities by using `FuturesSession`. This requires creating a `FuturesSession` instance and using it for HTTP requests.
3. **Synchronous Behavior**: Since the original code uses synchronous requests, the `.result()` method is called on the future object returned by `FuturesSession` to maintain the same behavior.
4. **Modified `requests.head` and `requests.models.Response`**: Replaced `requests.head` with `session.head` (from `FuturesSession`) and ensured `.result()` is called to get the actual response object.

### Modified Code

```python
"""
tests/test_api
~~~~~~~~~~~~~~
"""

import os
from pathlib import Path

from requests_futures.sessions import FuturesSession
from pytest import mark
from PIL import Image

import comics


# fmt: off
attributes = (
    ("calvinandhobbes", "Calvin and Hobbes", "2017-02-14", "https://www.gocomics.com/calvinandhobbes/2017/02/14"),
    ("jim-benton-cartoons", "Jim Benton Cartoons", "2020-05-10", "https://www.gocomics.com/jim-benton-cartoons/2020/05/10"),
    ("foxtrot", "FoxTrot", "1992-04-17", "https://www.gocomics.com/foxtrot/1992/04/17"),
    ("garfield", "Garfield", "2010-06-30", "https://www.gocomics.com/garfield/2010/06/30"),
    ("peanuts", "Peanuts", "1965-07-04", "https://www.gocomics.com/peanuts/1965/07/04"),
)
# fmt: on
@mark.parametrize("attr", attributes)
def test_attributes(attr):
    """Test proper instance attributes.

    Args:
        attr (tuple): Args to unpack for testing proper instance attributes.
    """
    session = FuturesSession()
    endpoint, title, date, url = attr
    comics_inst = comics.search(endpoint).date(date)
    assert comics_inst.title == title
    assert comics_inst.date == date
    assert comics_inst.url == url
    # Check if comic strip URL content is an image
    response = session.head(comics_inst.image_url).result()
    assert response.headers.get("content-type", "").startswith("image/")


def test_random_date():
    """Test random date instance is equal to date instance when using fixed date."""
    ch_random = comics.search("calvinandhobbes").random_date()
    random_date = ch_random.date
    ch_date = comics.search("calvinandhobbes").date(random_date)
    assert ch_random.date == ch_date.date
    assert ch_random.url == ch_date.url


def test_stream():
    """Test comic image stream instance and status code."""
    session = FuturesSession()
    ch = comics.search("calvinandhobbes").random_date()
    response = ch.stream()
    assert isinstance(response, session.head("").result().__class__)  # Ensure response type matches
    assert response.status_code == 200


def test_download_comic_and_verify_content():
    """Test proper comic download execution and valid download image content."""
    ch = comics.search("calvinandhobbes").random_date()
    _download_comic_and_verify_content(ch)


def test_download_static_gif_to_png():
    """Test proper comic download execution and valid download image content of static GIF
    to PNG."""
    bad_ch_date = "2009-09-10"
    ch = comics.search("calvinandhobbes").date(bad_ch_date)
    _download_comic_and_verify_content(ch)


def _download_comic_and_verify_content(comics_inst):
    """Private function. Verify proper download execution and valid download image content
    of a `ComicsAPI` instance.

    Args:
        comics_inst (ComicsAPI): `ComicsAPI` instance.
    """
    img_filepath = Path(__file__).parent / "downloads" / "comics_test.png"
    # Start by deleting the image if present - this allows me to keep the file tracked in Git to enable
    # GitHub Actions testing
    os.remove(img_filepath)
    # Verify download method works
    comics_inst.download(img_filepath)
    # Raises `PIL.UnidentifiedImageError` if invalid image
    Image.open(img_filepath).verify()
```

### Key Points
- A `FuturesSession` instance is created where asynchronous requests are needed.
- `.result()` is called on the future object to block and retrieve the actual response, ensuring synchronous behavior.
- The `requests.models.Response` type check is updated to match the response type returned by `FuturesSession`.