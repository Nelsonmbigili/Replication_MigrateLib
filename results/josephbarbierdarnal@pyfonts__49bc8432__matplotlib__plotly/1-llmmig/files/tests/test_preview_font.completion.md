### Explanation of Changes:
The provided code does not contain any direct usage of `matplotlib` for plotting or visualization. The only reference to `matplotlib` is the import of `FontProperties` from `matplotlib.font_manager`. Since this is unrelated to plotting and is used for font management, there is no need to migrate this part to `plotly`. 

Additionally, the code does not include any plotting functionality that would require migration to `plotly`. Therefore, no changes are necessary to migrate this code to use `plotly`.

However, if the intention is to replace `matplotlib` entirely in the application, you would need to identify and replace any actual plotting code elsewhere in the application. For this specific snippet, no modifications are required.

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

### Notes:
- The code remains unchanged because it does not involve any plotting or visualization that would require `plotly`.
- If there are other parts of the application that use `matplotlib` for plotting, those would need to be reviewed and migrated to `plotly`.