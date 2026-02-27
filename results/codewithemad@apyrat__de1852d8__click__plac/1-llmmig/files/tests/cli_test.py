from apyrat.apyrat import Downloader
from apyrat.cli import get_quality, main
from unittest.mock import patch
import plac


def test_main_download_video_with_quality():
    with patch(
        "apyrat.apyrat.Downloader._get_available_qualities",
        return_value=["480", "720", "1080"],
    ) as mock_qualities:
        result = plac.call(
            main,
            [
                "https://www.aparat.com/v/qur3I",
                "-q",
                "720",
            ],
        )
    assert result == 0
    mock_qualities.assert_called_once()


def test_main_download_video_without_quality():
    with patch(
        "apyrat.apyrat.Downloader._get_available_qualities",
        return_value=["480", "720", "1080"],
    ):
        # Simulate user input by passing the quality directly as an argument
        result = plac.call(main, ["https://www.aparat.com/v/qur3I", "-q", "720"])
    assert result == 0


def test_get_quality_available():
    downloader = Downloader("https://www.aparat.com/v/qur3I")
    downloader.qualities = ["480", "720", "1080"]
    # Simulate user input by directly passing the quality
    assert get_quality(downloader, "720") == "720"


def test_get_quality_not_available():
    downloader = Downloader("https://www.aparat.com/v/qur3I")
    downloader.qualities = ["480", "720", "1080"]
    # Simulate user input by directly passing the quality
    assert get_quality(downloader, "240") == "720"


def test_get_quality_not_available_no_confirm():
    downloader = Downloader("https://www.aparat.com/v/qur3I")
    downloader.qualities = ["480", "720", "1080"]
    # Simulate user input by directly passing the quality
    assert get_quality(downloader, "240") == "480"
