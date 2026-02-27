"""Console script for apyrat."""

import typer
from apyrat.apyrat import Downloader, URLType, VideoQuality
from apyrat.utils import get_about_information

app = typer.Typer(help="Download Aparat videos from your terminal")


def display_version(value: bool):
    if value:
        ABOUT = get_about_information()
        typer.echo(ABOUT["__version__"])
        raise typer.Exit()


@app.command()
def main(
    url: str = typer.Argument(..., help="The URL of the video to download."),
    filename: str = typer.Option(None, "--filename", "-f", help="Specify the output filename."),
    quality: str = typer.Option(None, "--quality", "-q", help="Quality of the video."),
    confirm: bool = typer.Option(False, "--confirm", "-y", help="Use default video quality if not available."),
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=display_version,
        is_eager=True,
        help="Show version and exit.",
    ),
):
    """
    Download Aparat videos from your terminal
    """
    try:
        downloader = Downloader(url)
    except ValueError:
        typer.echo("Invalid URL provided.", err=True)
        raise typer.Exit(1)

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


def get_quality(downloader: Downloader, quality: VideoQuality):
    if quality and quality not in downloader.qualities:
        typer.echo(f"Quality {quality} is not available", err=True)
        quality = None

    if not quality:
        quality_choice = typer.prompt(
            "Enter the quality you want to download",
            type=typer.Choice(downloader._get_available_qualities()),
            default=downloader.default_quality(),
        )
    else:
        quality_choice = quality

    return quality_choice


if __name__ == "__main__":
    app()
