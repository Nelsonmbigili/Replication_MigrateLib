### Explanation of Changes
To migrate the code from using `matplotlib` to `plotly`, the primary change involves replacing the `FontProperties` class from `matplotlib` with an appropriate alternative in `plotly`. Since `plotly` does not have a direct equivalent for `FontProperties`, we will simply return a dictionary containing the font information instead. This change reflects the different ways that `plotly` handles fonts and styling compared to `matplotlib`. The rest of the logic remains unchanged, as it pertains to loading fonts from a URL or local path.

### Modified Code
```python
from typing import Optional

from .get_font import _get_font_from_url, _get_local_font


def load_font(
    font_url: Optional[str] = None,
    font_path: Optional[str] = None,
) -> dict:
    """
    Loads font information from a remote Github repo or a local file.

    Parameters:
    - font_url: A URL pointing to a binary font file from Github.
    - font_path: The local file path of the font.

    Returns:
    - dict: A dictionary containing the loaded font information.
    """
    if font_url and font_path:
        raise ValueError(
            "You must provide only one of the following: `font_url` or `font_path`."
        )
    elif font_url:
        font = _get_font_from_url(font_url)
    elif font_path:
        font = _get_local_font(font_path)
    else:
        raise ValueError(
            "You must provide one of the following: `font_url` or `font_path`."
        )
    return font
```