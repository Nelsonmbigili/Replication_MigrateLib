The following Python code currently uses the library "click" version 7.1.2.
Migrate this code to use the library "typer" version 0.15.2 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "click" to "typer".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "click" and "typer".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from apyrat.apyrat import Downloader
from apyrat.cli import get_quality, main
from unittest.mock import patch
from click.testing import CliRunner


def test_main_download_video_with_quality():
    runner = CliRunner()
    with patch(
        "apyrat.apyrat.Downloader._get_available_qualities",
        return_value=["480", "720", "1080"],
    ) as mock_qualities:
        result = runner.invoke(
            main,
            [
                "https://www.aparat.com/v/qur3I",
                "-q",
                "720",
            ],
        )
    assert result.exit_code == 0
    mock_qualities.assert_called_once()


def test_main_download_video_without_quality():
    runner = CliRunner()
    with patch(
        "apyrat.apyrat.Downloader._get_available_qualities",
        return_value=["480", "720", "1080"],
    ), patch("click.prompt", return_value="720"):
        result = runner.invoke(main, ["https://www.aparat.com/v/qur3I"])
    assert result.exit_code == 0


def test_get_quality_available():
    downloader = Downloader("https://www.aparat.com/v/qur3I")
    downloader.qualities = ["480", "720", "1080"]
    with patch("click.prompt", return_value="720"):
        assert get_quality(downloader, "720") == "720"


def test_get_quality_not_available():
    downloader = Downloader("https://www.aparat.com/v/qur3I")
    downloader.qualities = ["480", "720", "1080"]
    with patch("click.prompt", return_value="720"):
        assert get_quality(downloader, "240") == "720"


def test_get_quality_not_available_no_confirm():
    downloader = Downloader("https://www.aparat.com/v/qur3I")
    downloader.qualities = ["480", "720", "1080"]
    with patch("click.prompt", return_value="480"):
        assert get_quality(downloader, "240") == "480"

```