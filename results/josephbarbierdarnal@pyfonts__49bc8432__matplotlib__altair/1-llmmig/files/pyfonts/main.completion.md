### Explanation of Changes:
The original code uses `matplotlib.font_manager.FontProperties` to load and manage font properties. Since `Altair` does not have a direct equivalent to `FontProperties` (as it is a declarative visualization library and does not manage fonts in the same way), the concept of loading fonts needs to be adapted. 

In Altair, font customization is typically done by specifying font names directly in chart configurations (e.g., `config.title.font`, `config.axis.labelFont`). Therefore, the `load_font` function is not directly applicable in the context of Altair. However, to preserve the functionality of loading a font file (e.g., from a URL or local path), we can modify the function to return the font name as a string, which can then be used in Altair chart configurations.

### Modified Code:
```python
from typing import Optional

from .get_font import _get_font_from_url, _get_local_font


def load_font(
    font_url: Optional[str] = None,
    font_path: Optional[str] = None,
) -> str:
    """
    Loads a font name from a remote Github repo or a local file.

    Parameters:
    - font_url: A URL pointing to a binary font file from Github.
    - font_path: The local file path of the font.

    Returns:
    - str: The name of the loaded font, which can be used in Altair chart configurations.
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
    
    # Assuming `_get_font_from_url` and `_get_local_font` return the font name
    return font
```

### Key Changes:
1. **Return Type**: Changed the return type from `FontProperties` (specific to `matplotlib`) to `str`, which represents the font name.
2. **Altair Compatibility**: The returned font name can now be used in Altair chart configurations (e.g., `config.title.font`).
3. **Preserved Functionality**: The logic for loading a font from a URL or local path remains unchanged, assuming `_get_font_from_url` and `_get_local_font` return the font name.

This modified function is now compatible with Altair, as it provides the font name that can be used in Altair's declarative chart configurations.