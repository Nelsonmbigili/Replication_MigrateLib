"""
tests/test_api
~~~~~~~~~~~~~~
"""

import os
from pathlib import Path
from io import BytesIO

import pycurl
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
    endpoint, title, date, url = attr
    comics_inst = comics.search(endpoint).date(date)
    assert comics_inst.title == title
    assert comics_inst.date == date
    assert comics_inst.url == url
    # Check if comic strip URL content is an image
    assert _get_content_type(comics_inst.image_url).startswith("image/")


def test_random_date():
    """Test random date instance is equal to date instance when using fixed date."""
    ch_random = comics.search("calvinandhobbes").random_date()
    random_date = ch_random.date
    ch_date = comics.search("calvinandhobbes").date(random_date)
    assert ch_random.date == ch_date.date
    assert ch_random.url == ch_date.url


def test_stream():
    """Test comic image stream instance and status code."""
    ch = comics.search("calvinandhobbes").random_date()
    response_status_code = _get_status_code(ch.image_url)
    assert response_status_code == 200


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


def _get_content_type(url):
    """Perform an HTTP HEAD request to get the content type of a URL.

    Args:
        url (str): The URL to check.

    Returns:
        str: The content type of the URL.
    """
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.NOBODY, True)
    curl.setopt(curl.HEADERFUNCTION, buffer.write)
    curl.perform()
    curl.close()

    headers = buffer.getvalue().decode("utf-8")
    for line in headers.splitlines():
        if line.lower().startswith("content-type:"):
            return line.split(":", 1)[1].strip()
    return ""


def _get_status_code(url):
    """Perform an HTTP GET request to get the status code of a URL.

    Args:
        url (str): The URL to check.

    Returns:
        int: The HTTP status code.
    """
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.NOBODY, False)
    curl.setopt(curl.FOLLOWLOCATION, True)
    curl.perform()
    status_code = curl.getinfo(pycurl.RESPONSE_CODE)
    curl.close()
    return status_code
