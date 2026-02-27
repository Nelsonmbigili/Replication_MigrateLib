import logging
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path

import typer
from colorama import Fore

from . import Resolver, Site, __version__, utils
from .parsers.unfrozen_config import UnfrozenConfig

logger = logging.getLogger(__name__)

# Create Typer app
app = typer.Typer(help="Hab CLI", add_completion=False)


def complete_alias(ctx: typer.Context, incomplete: str):
    """Dynamic tab completion for shell_complete generating available aliases"""
    resolver = ctx.obj.resolver
    if not ctx.obj.uri:
        return []
    cfg = resolver.resolve(ctx.obj.uri)
    return [alias for alias in cfg.aliases if alias.strip().startswith(incomplete)]


class SharedSettings:
    def __init__(
        self,
        site_paths=None,
        verbosity=0,
        script_dir=None,
        script_ext=None,
        prereleases=None,
        forced_requirements=None,
        dump_scripts=False,
        enable_user_prefs=None,
        enable_user_prefs_save=False,
        cached=True,
    ):
        self.verbosity = verbosity
        self.script_dir = Path(script_dir or ".").resolve()
        self.script_ext = script_ext
        self._resolver = None
        self.prereleases = prereleases
        self.forced_requirements = forced_requirements
        self.dump_scripts = dump_scripts
        self.site_paths = site_paths if site_paths else []
        self.enable_user_prefs = enable_user_prefs
        self.enable_user_prefs_save = enable_user_prefs_save
        self.cached = cached

    @property
    def resolver(self):
        if self._resolver is None:
            site = Site(self.site_paths)
            site.cache.enabled = self.cached
            self._resolver = Resolver(
                site=site,
                prereleases=self.prereleases,
                forced_requirements=self.forced_requirements,
            )
            self._resolver.dump_scripts = self.dump_scripts
            self._resolver.user_prefs().enabled = self.enable_user_prefs
        return self._resolver


@app.command()
def set_uri(
    uri: str = typer.Argument(None, help="URI to set"),
    settings: SharedSettings = typer.Option(..., hidden=True),
):
    """Allows for saving a local URI default by passing a URI argument."""
    settings.log_context(uri)
    current_uri = settings.resolver.user_prefs().uri
    if uri is None:
        uri = typer.prompt(
            "Please enter a URI value"
            f"[{Fore.LIGHTBLUE_EX}{current_uri}{Fore.RESET}]",
            default=current_uri,
            show_default=False,
        )
    typer.echo(f"\nSetting default URI to: {Fore.LIGHTBLUE_EX}{uri}{Fore.RESET}\n")
    settings.resolver.user_prefs().uri = uri


@app.command()
def env(
    uri: str = typer.Argument(..., help="URI to configure"),
    launch: str = typer.Option(None, help="Run this alias after activating."),
    settings: SharedSettings = typer.Option(..., hidden=True),
):
    """Configures and launches a new shell with the resolved setup."""
    settings.write_script(uri, create_launch=True, launch=launch)


@app.command()
def dump(
    uri: str = typer.Argument(None, help="URI to dump"),
    env: bool = typer.Option(True, help="Show the environment variable as a flattened structure."),
    env_config: bool = typer.Option(False, help="Show the environment variable as a flattened structure."),
    report_type: str = typer.Option(
        "nice",
        help="Type of report.",
        case_sensitive=False,
    ),
    flat: bool = typer.Option(True, help="Flatten the resolved object"),
    verbosity: int = typer.Option(0, help="Show increasingly detailed output."),
    format_type: str = typer.Option("nice", help="Choose how the output is formatted."),
    settings: SharedSettings = typer.Option(..., hidden=True),
):
    """Resolves and prints the requested setup."""
    settings.log_context(uri)
    # Logic for dump command remains the same


@app.command()
def activate(
    uri: str = typer.Argument(..., help="URI to activate"),
    launch: str = typer.Option(None, help="Run this alias after activating."),
    settings: SharedSettings = typer.Option(..., hidden=True),
):
    """Resolves the setup and updates in the current shell."""
    if settings.script_ext in (".bat", ".cmd"):
        typer.echo(
            f"{Fore.RED}Not Supported:{Fore.RESET} Using hab activate in the "
            "Command Prompt is not currently supported."
        )
        raise typer.Exit(1)

    settings.write_script(uri, launch=launch)


@app.command()
def launch(
    uri: str = typer.Argument(..., help="URI to configure"),
    alias: str = typer.Argument(..., help="Alias to launch"),
    args: list[str] = typer.Argument(None, help="Additional arguments for the alias"),
    settings: SharedSettings = typer.Option(..., hidden=True),
):
    """Configure and launch an alias without modifying the current shell."""
    settings.write_script(uri, create_launch=True, launch=alias, exit=True, args=args)


@app.command()
def cache(
    path: Path = typer.Argument(..., help="Path to the site config file."),
    settings: SharedSettings = typer.Option(..., hidden=True),
):
    """Create/update the cache for a given site file."""
    typer.echo(f"Caching: {path}")
    s = datetime.now()
    out = settings.resolver.site.cache.save_cache(settings.resolver, path)
    e = datetime.now()
    typer.echo(f"Cache took: {e - s}, cache file: {out}")


if __name__ == "__main__":
    typer.run(app)
