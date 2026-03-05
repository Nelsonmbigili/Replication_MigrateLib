### Explanation of Changes
To migrate the code from using `matplotlib` to `altair`, the primary change involves replacing the `FontProperties` class from `matplotlib` with an appropriate alternative in `altair`. However, `altair` does not have a direct equivalent for `FontProperties` since it handles fonts differently, primarily through the use of CSS styles in its visualizations. Therefore, the return type of the `load_font` function will be changed to `None`, as `altair` does not require a font object to be returned in the same way `matplotlib` does. The logic for loading the font remains unchanged, but we will not return a font object.

### Modified Code
```python
from typing import Optional

from .get_font import _get_font_from_url, _get_local_font


def load_font(
    font_url: Optional[str] = None,
    font_path: Optional[str] = None,
) -> None:
    """
    Loads a font from a remote Github repo or a local file.

    Parameters:
    - font_url: A URL pointing to a binary font file from Github.
    - font_path: The local file path of the font.

    Returns:
    - None
    """
    if font_url and font_path:
        raise ValueError(
            "You must provide only one of the following: `font_url` or `font_path`."
        )
    elif font_url:
        _get_font_from_url(font_url)
    elif font_path:
        _get_local_font(font_path)
    else:
        raise ValueError(
            "You must provide one of the following: `font_url` or `font_path`."
        )
```