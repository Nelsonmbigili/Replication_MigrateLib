### Explanation of Changes:
The provided code does not directly involve any plotting or visualization functionality from `matplotlib`. Instead, it uses `matplotlib.font_manager.FontProperties` to load and manage font files. Since `plotly` does not have a direct equivalent for managing fonts in this way, the migration to `plotly` is not applicable here. 

However, if the goal is to remove the dependency on `matplotlib` entirely, we would need to replace `matplotlib.font_manager.FontProperties` with an alternative library for font management. A common choice for font handling in Python is the `Pillow` library (`PIL`), which can load and manage font files.

Below, I have modified the code to use `Pillow`'s `ImageFont` module instead of `matplotlib.font_manager.FontProperties`. This removes the dependency on `matplotlib`.

---

### Modified Code:
```python
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from tempfile import NamedTemporaryFile
from PIL import ImageFont

from .is_valid import _is_url, _is_valid_raw_url


def _get_font_from_url(font_location: str) -> ImageFont.FreeTypeFont:
    """
    Retrieves a font from a Github url. The function attempts to access the font
    at the given url by checking a few elements, creates a temporary file with the
    font found and returns a FreeTypeFont object.

    Params:
    - font_location: url that points to the binary font file on Github

    Returns:
    - PIL.ImageFont.FreeTypeFont: A FreeTypeFont object containing the loaded font.
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
                temp_file_path = temp_file.name

        except HTTPError as e:
            if e.code == 404:
                raise Exception(
                    "404 error. The url passed does not exist: font file not found."
                )

        except URLError:
            raise Exception(
                "Failed to load font. This may be due to a lack of internet connection."
            )

        try:
            font = ImageFont.truetype(temp_file_path)
        except Exception as e:
            raise ValueError(f"Failed to load font from URL: {e}")

        return font


def _get_local_font(font_location: str) -> ImageFont.FreeTypeFont:
    """
    Retrieves a font from a local path.

    Params:
    - font_location: path to a font file.

    Returns:
    - PIL.ImageFont.FreeTypeFont: A FreeTypeFont object containing the loaded font.
    """

    if _is_url(font_location):
        raise ValueError("`font_location` must point to a local file on your computer.")

    else:
        try:
            font = ImageFont.truetype(font_location)
        except FileNotFoundError:
            raise ValueError(f"Font file not found at : '{font_location}'")
        except Exception as e:
            raise ValueError(f"Failed to load font from local file: {e}")

    return font
```

---

### Key Changes:
1. **Replaced `matplotlib.font_manager.FontProperties`**:
   - The `FontProperties` class from `matplotlib` was replaced with `Pillow`'s `ImageFont.truetype` method, which provides similar functionality for loading font files.

2. **Updated Return Types**:
   - The return type of the functions was updated to `PIL.ImageFont.FreeTypeFont` instead of `matplotlib.font_manager.FontProperties`.

3. **Error Handling**:
   - Adjusted error handling to account for potential issues with `Pillow`'s `ImageFont.truetype` method, such as invalid font files.

4. **Temporary File Handling**:
   - Ensured that the temporary file path is passed to `ImageFont.truetype` for loading the font.

---

### Notes:
- This migration removes the dependency on `matplotlib` and replaces it with `Pillow`, which is a lightweight and widely used library for image and font handling.
- If `plotly` integration is required for visualization purposes elsewhere in the application, it can be added independently, as this part of the code is unrelated to plotting.