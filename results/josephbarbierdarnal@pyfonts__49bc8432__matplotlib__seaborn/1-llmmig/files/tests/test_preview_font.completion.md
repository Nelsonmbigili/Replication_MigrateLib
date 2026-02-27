### Explanation of Changes:
The provided code does not directly use any plotting functionality from `matplotlib`. Instead, it imports `FontProperties` from `matplotlib.font_manager` and uses it in a mocked function. Since the code does not involve any plotting or visualization, there is no need to migrate to `seaborn`. `seaborn` is a data visualization library built on top of `matplotlib`, and it does not provide a replacement for `FontProperties` or related functionality.

Thus, no changes are required to migrate this code to use `seaborn`. The code remains the same because it does not utilize any plotting features that would necessitate a switch to `seaborn`.

### Modified Code:
```python
import pytest
from unittest.mock import patch, MagicMock
from matplotlib.font_manager import FontProperties
from pyfonts import preview_font, load_font


@pytest.fixture
def mock_load_font():
    with patch("pyfonts.load_font") as mock:
        mock.return_value = FontProperties()
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

### Key Notes:
- The code does not involve any plotting or visualization, so there is no need to replace `matplotlib` with `seaborn`.
- `FontProperties` is a utility from `matplotlib` for managing font properties, and `seaborn` does not provide an equivalent feature.
- The code remains unchanged as it does not use any functionality that would benefit from or require `seaborn`.