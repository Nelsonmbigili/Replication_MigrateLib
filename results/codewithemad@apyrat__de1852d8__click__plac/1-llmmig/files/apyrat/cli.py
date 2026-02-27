"""Console script for apyrat."""

import plac
from apyrat.apyrat import Downloader, URLType, VideoQuality
from apyrat.utils import get_about_information


def display_version():
    """
    Display the version of the application and exit.
    """
    ABOUT = get_about_information()
    print(ABOUT["__version__"])
    exit(0)


def get_quality(downloader: Downloader, quality: VideoQuality):
    """
    Prompt the user for video quality if not provided or invalid.
    """
    if quality and quality not in downloader.qualities:
        print(f"Quality {quality} is not available", file=sys.stderr)
        quality = None

    if not quality:
        available_qualities = downloader._get_available_qualities()
        default_quality = downloader.default_quality()
        print(f"Available qualities: {', '.join(available_qualities)}")
        quality_choice = input(
            f"Enter the quality you want to download (default: {default_quality}): "
        ) or default_quality
    else:
        quality_choice = quality

    return quality_choice


@plac.annotations(
    url=("URL of the video to download", "positional", None, str),
    version=("Show version and exit", "flag", "v"),
    filename=("Specify the output filename", "option", "f", str),
    quality=("Quality of the video", "option", "q", str),
    confirm=("Use default video quality if not available", "flag", "y"),
)
def main(url: str, version: bool = False, filename: str = None, quality: str = None, confirm: bool = False):
    """
    Download Aparat videos from your terminal.
    """
    if version:
        display_version()

    try:
        downloader = Downloader(url)
    except ValueError:
        print("Invalid URL provided.", file=sys.stderr)
        exit(1)

    # Set filename if the URL type is URLType.VIDEO
    if filename and downloader.url_type == URLType.VIDEO:
        downloader.file_name = filename

    quality_choice = str(
        downloader.default_quality()
        if confirm
        else get_quality(
            downloader,
            quality,
        )
    )

    downloader.download(quality_choice)


if __name__ == "__main__":
    plac.call(main)
