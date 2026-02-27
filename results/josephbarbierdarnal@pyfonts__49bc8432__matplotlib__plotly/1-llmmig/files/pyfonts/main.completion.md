### Explanation of Changes:
The original code uses `matplotlib.font_manager.FontProperties` to load and manage font properties. Since `plotly` does not have a direct equivalent to `FontProperties`, the migration involves adapting the code to use `plotly`'s font configuration options. In `plotly`, fonts are typically specified as part of the layout configuration (e.g., `layout.font.family`), and there is no need for a separate `FontProperties` object.

To migrate the code:
1. Removed the import of `matplotlib.font_manager.FontProperties` since it is no longer needed.
2. Updated the return type of the `load_font` function to `str`, as `plotly` expects font family names as strings.
3. Modified the function to return the font family name (e.g., `"Arial"`) instead of a `FontProperties` object.
4. Kept the logic for loading fonts from a URL or local file intact, assuming `_get_font_from_url` and `_get_local_font` return the font family name as a string.

### Modified Code:
```python
from typing import Optional

from .get_font import _get_font_from_url, _get_local_font


def load_font(
    font_url: Optional[str] = None,
    font_path: Optional[str] = None,
) -> str:
    """
    Loads a font family name from a remote Github repo or a local file.

    Parameters:
    - font_url: A URL pointing to a binary font file from Github.
    - font_path: The local file path of the font.

    Returns:
    - str: The font family name as a string.
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

### Notes:
- The `_get_font_from_url` and `_get_local_font` functions are assumed to return the font family name as a string (e.g., `"Arial"`). If they return something else (e.g., a file path), additional changes may be needed to extract the font family name.
- This migration assumes that the rest of the application will use the returned font family name in `plotly` layout configurations (e.g., `layout.font.family`).