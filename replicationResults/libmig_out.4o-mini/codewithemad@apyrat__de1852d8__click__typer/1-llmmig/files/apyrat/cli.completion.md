### Explanation of Changes

To migrate the code from using the `click` library to the `typer` library, the following changes were made:

1. **Import Statement**: Changed the import from `click` to `typer`.
2. **Command and Option Decorators**: Replaced `@click.command` and `@click.option` with `@typer.command` and `@typer.Option`, respectively.
3. **Context Handling**: Removed the context parameter (`ctx`) from the function signatures and replaced the way to handle version and help display using Typer's built-in features.
4. **Error Handling**: Used `typer.echo` instead of `click.echo` for outputting messages.
5. **Prompting for Input**: Used `typer.prompt` instead of `click.prompt` for user input.
6. **Exit Handling**: Used `typer.Exit` for exiting the application instead of `ctx.exit()`.

The overall structure and logic of the code remain unchanged, adhering to the original coding style.

### Modified Code

```python
"""Console script for apyrat."""

import typer

from apyrat.apyrat import Downloader, URLType, VideoQuality
from apyrat.utils import get_about_information


def display_version(value: bool):
    if value:
        ABOUT = get_about_information()
        typer.echo(ABOUT["__version__"])
        raise typer.Exit()


def display_help(value: bool):
    if value:
        typer.echo(typer.get_help())
        raise typer.Exit()


app = typer.Typer()

@app.callback()
def main(version: bool = typer.Option(False, "--version", "-v", is_eager=True, help="Show version and exit.")):
    display_version(version)

@app.command()
def download(url: str, quality: str = None, filename: str = None, confirm: bool = False):
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
```