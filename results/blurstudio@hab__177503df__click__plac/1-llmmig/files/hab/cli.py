import logging
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path

import plac
from colorama import Fore

from . import Resolver, Site, __version__, utils
from .parsers.unfrozen_config import UnfrozenConfig

logger = logging.getLogger(__name__)


class SharedSettings(object):
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

    @classmethod
    def log_context(cls, uri):
        """Writes a logger.info call for the given uri string or dictionary."""
        if isinstance(uri, dict):
            logger.info(f"Context: {uri['uri']}")
        else:
            logger.info(f"Context: {uri}")

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

    def write_script(
        self,
        uri,
        launch=None,
        exit=False,
        args=None,
        create_launch=False,
    ):
        """Generate the script the calling shell scripts expect to setup the environment"""
        self.log_context(uri)
        logger.debug(f"Script dir: {self.script_dir} ext: {self.script_ext}")

        if args:
            # convert to list, subprocess.list2cmdline does not like tuples
            args = list(args)

        if isinstance(uri, dict):
            # Load frozen json data instead of processing the URI
            cfg = UnfrozenConfig(uri, self.resolver)
        elif uri is None:
            raise ValueError("Missing argument 'URI'.")
        else:
            # Otherwise just process the uri like normal
            cfg = self.resolver.resolve(uri)

        if launch:
            _args = f" {' '.join(args)}" if args else ""
            launch_msg = f"Launching alias: {launch}{_args} for URI: {cfg.uri}"
        if self.script_dir:
            if launch:
                logger.info(f"{launch_msg} using shell.")
            cfg.write_script(
                self.script_dir,
                self.script_ext,
                launch=launch,
                exit=exit,
                args=args,
                create_launch=create_launch,
            )
        elif launch:
            kwargs = {}
            blocking = not sys.executable.endswith("w.exe")
            if blocking:
                kwargs["stderr"] = None
                kwargs["stdout"] = None

            logger.info(f"{launch_msg} as subprocess.")
            proc = cfg.launch(launch, args, blocking=blocking, **kwargs)
            if blocking:
                sys.exit(proc.returncode)


def set_uri(settings: SharedSettings, uri: str = None):
    """Allows for saving a local URI default by passing
    a URI argument. If no argument is passed, prompts for input."""
    settings.log_context(uri)
    current_uri = settings.resolver.user_prefs().uri
    if uri is None:
        uri = input(
            f"Please enter a URI value [{Fore.LIGHTBLUE_EX}{current_uri}{Fore.RESET}]: "
        ) or current_uri
    print(f"\nSetting default URI to: {Fore.LIGHTBLUE_EX}{uri}{Fore.RESET}\n")
    settings.resolver.user_prefs().uri = uri


def env(settings: SharedSettings, uri: str, launch: str = None):
    """Configures and launches a new shell with the resolved setup."""
    settings.write_script(uri, create_launch=True, launch=launch)


def dump(
    settings: SharedSettings,
    uri: str = None,
    env: bool = True,
    env_config: bool = False,
    report_type: str = "nice",
    flat: bool = True,
    verbosity: int = 0,
    format_type: str = "nice",
):
    """Resolves and prints the requested setup."""
    settings.log_context(uri)
    resolver = settings.resolver

    if report_type in ("uris", "versions", "forest"):
        from .parsers.format_parser import FormatParser

        formatter = FormatParser(verbosity, color=True)
        truncate = None if verbosity > 1 else 3

        if report_type in ("uris", "forest"):
            print(f'{Fore.YELLOW}{" URIs ".center(50, "-")}{Fore.RESET}')
            with utils.verbosity_filter(resolver, verbosity):
                for line in resolver.dump_forest(
                    resolver.configs, fmt=formatter.format
                ):
                    print(line)
        if report_type in ("versions", "forest"):
            print(f'{Fore.YELLOW}{" Versions ".center(50, "-")}{Fore.RESET}')
            for line in resolver.dump_forest(
                resolver.distros,
                attr="name",
                fmt=formatter.format,
                truncate=truncate,
            ):
                print(line)
    elif report_type == "all-uris":
        ret = resolver.freeze_configs()
        ret = utils.dumps_json(ret, indent=2)
        print(ret)
    elif report_type == "site":
        print(resolver.site.dump(verbosity=verbosity))
    else:
        if isinstance(uri, dict):
            ret = UnfrozenConfig(uri, resolver)
        elif flat:
            ret = resolver.resolve(uri)
        else:
            ret = resolver.closest_config(uri)

        if format_type == "freeze":
            ret = utils.encode_freeze(ret.freeze(), site=resolver.site)
        elif format_type == "json":
            ret = utils.dumps_json(ret.freeze(), indent=2)
        elif format_type == "versions":
            ret = "\n".join([v.name for v in ret.versions])
        else:
            ret = ret.dump(
                environment=env, environment_config=env_config, verbosity=verbosity
            )

        print(ret)


def activate(settings: SharedSettings, uri: str, launch: str = None):
    """Resolves the setup and updates in the current shell."""
    if settings.script_ext in (".bat", ".cmd"):
        print(
            f"{Fore.RED}Not Supported:{Fore.RESET} Using hab activate in the "
            "Command Prompt is not currently supported."
        )
        sys.exit(1)

    settings.write_script(uri, launch=launch)


def launch(settings: SharedSettings, uri: str, alias: str, *args):
    """Configure and launch an alias without modifying the current shell."""
    settings.write_script(uri, create_launch=True, launch=alias, exit=True, args=args)


def cache(settings: SharedSettings, path: str):
    """Create/update the cache for a given site file."""
    path = Path(path)
    print(f"Caching: {path}")
    s = datetime.now()
    out = settings.resolver.site.cache.save_cache(settings.resolver, path)
    e = datetime.now()
    print(f"Cache took: {e - s}, cache file: {out}")


def main():
    plac.call([
        set_uri,
        env,
        dump,
        activate,
        launch,
        cache
    ])


if __name__ == "__main__":
    main()
