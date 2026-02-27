### Explanation of Changes:
The provided code does not directly use any plotting functionality from `matplotlib`. Instead, it uses `matplotlib.font_manager.FontProperties` to load and manage font properties. The `seaborn` library does not provide a direct equivalent to `matplotlib.font_manager.FontProperties`, as `seaborn` relies on `matplotlib` for font management and rendering.

Since the functionality in the code is specific to font management and does not involve plotting or visualization, **no changes are required to migrate this code to use `seaborn`**. The `FontProperties` class from `matplotlib` is still necessary for the described functionality, even if `seaborn` is used elsewhere in the application.

### Modified Code:
No modifications are needed, as the code is already compatible with `seaborn` and does not require migration. Here is the original code, unchanged:

```python
from matplotlib.font_manager import FontProperties
from typing import Optional

from .get_font import _get_font_from_url, _get_local_font


def load_font(
    font_url: Optional[str] = None,
    font_path: Optional[str] = None,
) -> FontProperties:
    """
    Loads a FontProperties object from a remote Github repo or a local file.

    Parameters:
    - font_url: A URL pointing to a binary font file from Github.
    - font_path: The local file path of the font.

    Returns:
    - matplotlib.font_manager.FontProperties: A FontProperties object containing the loaded font.
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

### Conclusion:
The code does not require any changes to migrate to `seaborn` because it does not involve any plotting or visualization functionality. The use of `matplotlib.font_manager.FontProperties` is still necessary for font management, even when using `seaborn`.