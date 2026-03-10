### Explanation of Changes
To migrate the code from using the `click` library to the `typer` library, the following changes were made:

1. **Import Changes**: The import statement for `CliRunner` from `click.testing` was removed, as `typer` does not have a direct equivalent. Instead, we will use `typer.testing` for testing.
2. **Runner Initialization**: The `CliRunner` from `click` was replaced with `typer.testing.CliRunner`.
3. **Prompt Replacement**: The `click.prompt` function was replaced with `typer.prompt` to handle user input prompts.

These changes ensure that the code remains functional while adhering to the new library's structure.

### Modified Code
```python
from apyrat.apyrat import Downloader
from apyrat.cli import get_quality, main
from unittest.mock import patch
from typer.testing import CliRunner


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
    ), patch("typer.prompt", return_value="720"):
        result = runner.invoke(main, ["https://www.aparat.com/v/qur3I"])
    assert result.exit_code == 0


def test_get_quality_available():
    downloader = Downloader("https://www.aparat.com/v/qur3I")
    downloader.qualities = ["480", "720", "1080"]
    with patch("typer.prompt", return_value="720"):
        assert get_quality(downloader, "720") == "720"


def test_get_quality_not_available():
    downloader = Downloader("https://www.aparat.com/v/qur3I")
    downloader.qualities = ["480", "720", "1080"]
    with patch("typer.prompt", return_value="720"):
        assert get_quality(downloader, "240") == "720"


def test_get_quality_not_available_no_confirm():
    downloader = Downloader("https://www.aparat.com/v/qur3I")
    downloader.qualities = ["480", "720", "1080"]
    with patch("typer.prompt", return_value="480"):
        assert get_quality(downloader, "240") == "480"
```