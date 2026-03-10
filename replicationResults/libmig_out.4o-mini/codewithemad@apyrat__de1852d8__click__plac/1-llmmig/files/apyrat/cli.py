"""Console script for apyrat."""

import plac

from apyrat.apyrat import Downloader, URLType, VideoQuality
from apyrat.utils import get_about_information


def display_version():
    ABOUT = get_about_information()
    print(ABOUT["__version__"])


def get_quality(downloader: Downloader, quality: VideoQuality):
    if quality and quality not in downloader.qualities:
        print(f"Quality {quality} is not available", file=sys.stderr)
        quality = None

    if not quality:
        quality_choice = input(
            "Enter the quality you want to download: "
        )
        if quality_choice not in downloader._get_available_qualities():
            print(f"Quality {quality_choice} is not available", file=sys.stderr)
            quality_choice = None
        else:
            return quality_choice
    else:
        return quality


@plac.annotations(
    version=("Show version and exit", "flag", "v"),
    filename=("Specify the output filename", "option", "f"),
    quality=("Quality of the video", "option", "q"),
    confirm=("Use default video quality if not available", "flag", "y"),
    url=("The URL of the video", "positional", None)
)
def main(version, filename=None, quality=None, confirm=False, url=None):
    """
    Download Aparat videos from your terminal
    """
    if version:
        display_version()
        return

    if url is None:
        print("URL is required.", file=sys.stderr)
        return

    try:
        downloader = Downloader(url)
    except ValueError:
        print("Invalid URL provided.", file=sys.stderr)
        return

    # set filename if the url type is URLType.VIDEO
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
