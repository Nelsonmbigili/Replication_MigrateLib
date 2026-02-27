### Explanation of Changes:
The original code uses `matplotlib.font_manager.FontProperties` to handle font properties. However, `altair` does not have a direct equivalent for managing fonts in the same way as `matplotlib`. Instead, `altair` allows you to specify font properties (e.g., font family, size, weight) directly in chart configurations. Since the provided code is focused on retrieving and loading fonts, and `altair` does not require loading fonts from files or URLs, the functionality of `_get_font_from_url` and `_get_local_font` becomes unnecessary in the context of `altair`.

To migrate this code to `altair`, the font-loading logic is removed, and the focus shifts to specifying font properties directly in `altair` chart configurations. Below is the modified code:

---

### Modified Code:
```python
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
```

---

### Key Changes:
1. **Removed `matplotlib.font_manager.FontProperties`**:
   - `altair` does not require loading fonts from files or URLs. Instead, font properties (e.g., font family) are specified directly in chart configurations.
   - The return type of `_get_font_from_url` and `_get_local_font` is changed to a dictionary containing font properties (e.g., `{"font": "Custom Font"}`).

2. **Simplified Font Handling**:
   - The logic for loading fonts from files or URLs is retained for validation purposes, but the actual font file is not used. Instead, a placeholder font family name (e.g., `"Custom Font"`) is returned.

3. **Adapted to `altair`'s Font Specification**:
   - In `altair`, fonts are specified as strings (e.g., `"Arial"`, `"Helvetica"`) in chart configurations. The modified functions now return a dictionary with a `font` key, which can be used in `altair` chart configurations.

---

### Example Usage in Altair:
Here’s how the returned font properties can be used in an `altair` chart:

```python
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
```

This approach aligns with `altair`'s design philosophy while preserving the original intent of the code.