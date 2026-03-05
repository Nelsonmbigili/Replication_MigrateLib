from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from tempfile import NamedTemporaryFile

from .is_valid import _is_url, _is_valid_raw_url


def _get_font_from_url(font_location: str) -> None:
    """
    Retrieves a font from a Github url. The function attempts to access the font
    at the given url by checking a few elements, creates a temporary file with the
    font found. Note: Altair does not use FontProperties.

    Params:
    - font_location: url that points to the binary font file on Github

    Returns:
    - None
    """

    if not _is_url(font_location):
        raise ValueError(f"`font_location` must be an url, not: {font_location}.")

    elif not _is_valid_raw_url(font_location):
        raise ValueError(
            f"""
            The URL provided ({font_location}) does not appear to be valid.
            It must point to a binary font file from Github.
            Have you forgotten to append `?raw=true` to the end of the URL?
            """
        )

    else:
        try:
            with NamedTemporaryFile(delete=False) as temp_file:
                response = urlopen(font_location)
                temp_file.write(response.read())

        except HTTPError as e:
            if e.code == 404:
                raise Exception(
                    "404 error. The url passed does not exist: font file not found."
                )

        except URLError:
            raise Exception(
                "Failed to load font. This may be due to a lack of internet connection."
            )

        # Note: Altair does not use FontProperties, so we do not return anything here.


def _get_local_font(font_location: str) -> None:
    """
    Retrieves a font from a local path. Note: Altair does not use FontProperties.

    Params:
    - font_location: path to a font file.

    Returns:
    - None
    """

    if _is_url(font_location):
        raise ValueError("`font_location` must point to a local file on your computer.")

    else:
        try:
            # Simulating font loading, but Altair does not require FontProperties.
            with open(font_location, 'rb') as f:
                f.read()  # Just to check if the file exists and can be read.
        except FileNotFoundError:
            raise ValueError(f"Font file not found at : '{font_location}'")

    # Note: Altair does not use FontProperties, so we do not return anything here.
