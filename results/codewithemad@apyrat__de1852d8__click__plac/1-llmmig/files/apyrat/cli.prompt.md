The following Python code currently uses the library "click" version 7.1.2.
Migrate this code to use the library "plac" version 1.4.3 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "click" to "plac".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "click" and "plac".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
"""Console script for apyrat."""

import click

from apyrat.apyrat import Downloader, URLType, VideoQuality
from apyrat.utils import get_about_information


def display_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    else:
        ABOUT = get_about_information()
        click.echo(ABOUT["__version__"])
        ctx.exit()


def display_help(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(ctx.get_help())
    ctx.exit()


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-v",
    "--version",
    is_flag=True,
    callback=display_version,
    expose_value=False,
    is_eager=True,
    help="Show version and exit.",
)
@click.option(
    "-f",
    "--filename",
    type=click.Path(),
    default=None,
    help="Specify the output filename.",
)
@click.option(
    "-q",
    "--quality",
    type=str,
    default=None,
    help="Quality of the video.",
)
@click.option(
    "-y",
    "--confirm",
    is_flag=True,
    default=False,
    help="Use default video quality if not available.",
)
@click.argument("url", type=str, required=True)
@click.pass_context
def main(ctx, url: str, quality: str, filename: str, confirm: bool):
    """
    Download Aparat videos from your terminal
    """
    try:
        downloader = Downloader(url)
    except ValueError:
        click.echo("Invalid URL provided.", err=True)
        ctx.exit(1)

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
        click.echo(f"Quality {quality} is not available", err=True)
        quality = None

    if not quality:
        quality_choice = click.prompt(
            "Enter the quality you want to download",
            type=click.Choice(downloader._get_available_qualities()),
            default=downloader.default_quality(),
        )
    else:
        quality_choice = quality

    return quality_choice


if __name__ == "__main__":
    main()

```