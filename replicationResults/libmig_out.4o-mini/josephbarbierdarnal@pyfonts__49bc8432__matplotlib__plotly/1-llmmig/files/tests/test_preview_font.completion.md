### Explanation of Changes
To migrate the code from using `matplotlib` to `plotly`, I replaced the `FontProperties` class from `matplotlib.font_manager` with an equivalent functionality in `plotly`. Since `plotly` does not have a direct equivalent for `FontProperties`, I removed the import and the mock return value for `FontProperties`. The rest of the code remains unchanged, as the focus is on the migration of the library without altering the original logic or structure.

### Modified Code
```python
import pytest
from unittest.mock import patch, MagicMock
# Removed the import for FontProperties as it is not needed in plotly
# from matplotlib.font_manager import FontProperties
from pyfonts import preview_font, load_font


@pytest.fixture
def mock_load_font():
    with patch("pyfonts.load_font") as mock:
        # Changed the return value to None since FontProperties is not used in plotly
        mock.return_value = None
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