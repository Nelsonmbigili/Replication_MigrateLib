from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from tempfile import NamedTemporaryFile

from .is_valid import _is_url, _is_valid_raw_url


def _get_font_from_url(font_location: str) -> dict:
    """
    Retrieves a font from a Github url. The function attempts to access the font
    at the given url by checking a few elements and returns a dictionary with font properties.

    Params:
    - font_location: url that points to the binary font file on Github

    Returns:
    - dict: A dictionary containing font properties for use in Altair charts.
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

        # Altair does not use font files directly. Instead, return font family name.
        return {"font": "Custom Font"}  # Replace "Custom Font" with the actual font family name.


def _get_local_font(font_location: str) -> dict:
    """
    Retrieves a font from a local path.

    Params:
    - font_location: path to a font file.

    Returns:
    - dict: A dictionary containing font properties for use in Altair charts.
    """

    if _is_url(font_location):
        raise ValueError("`font_location` must point to a local file on your computer.")

    else:
        try:
            # Altair does not use font files directly. Instead, return font family name.
            return {"font": "Local Font"}  # Replace "Local Font" with the actual font family name.
        except FileNotFoundError:
            raise ValueError(f"Font file not found at : '{font_location}'")
import altair as alt

# Example font properties returned by the modified functions
font_properties = _get_local_font("path/to/local/font.ttf")

# Create an Altair chart and apply the font
chart = alt.Chart(data).mark_point().encode(
    x='x:Q',
    y='y:Q'
).configure_axis(
    labelFont=font_properties["font"],
    titleFont=font_properties["font"]
).configure_title(
    font=font_properties["font"]
)

chart.show()
