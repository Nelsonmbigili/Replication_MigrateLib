### Explanation of Changes
To migrate the code from using `matplotlib` to `seaborn`, I replaced the import statement for `FontProperties` from `matplotlib.font_manager` with the appropriate import from `seaborn`. In this case, `seaborn` does not have a direct equivalent for `FontProperties`, so I will simply remove the import statement for `FontProperties`. The rest of the code remains unchanged, as it does not directly utilize any plotting or font management features that would require further modifications.

### Modified Code
```python
import pytest
from unittest.mock import patch, MagicMock
# Removed the import for FontProperties as it is not needed in seaborn
from pyfonts import preview_font, load_font


@pytest.fixture
def mock_load_font():
    with patch("pyfonts.load_font") as mock:
        mock.return_value = None  # Adjusted to return None since FontProperties is not used
        yield mock


def test_preview_font_raises_value_error_on_invalid_input(mock_load_font):
    mock_load_font.side_effect = ValueError(
        "You must provide only one of the following: `font_name`, `font_url` or `font_path`."
    )
    with pytest.raises(ValueError):
        preview_font(
            font_url="http://example.com/font.ttf", font_path="/path/to/font.ttf"
        )
``` 

In this modified code, the import for `FontProperties` has been removed, and the return value in the `mock_load_font` fixture has been set to `None` since it is no longer relevant. The rest of the code remains intact to ensure compatibility with the larger application.