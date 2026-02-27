"""Command-line interface."""

from pathlib import Path
from typing import List, Optional
import pluggy
from tomlkit import dumps

from edgetest import hookspecs, lib
from edgetest.core import TestPackage
from edgetest.logger import get_logger
from edgetest.report import gen_report
from edgetest.schema import EdgetestValidator, Schema
from edgetest.utils import (
    gen_requirements_config,
    parse_cfg,
    parse_toml,
    upgrade_pyproject_toml,
    upgrade_requirements,
    upgrade_setup_cfg,
)

import plac

LOG = get_logger(__name__)


def get_plugin_manager() -> pluggy.PluginManager:
    """Get the plugin manager.

    Registers the default ``venv`` plugin.

    Returns
    -------
    PluginManager
        The plugin manager.
    """
    pm = pluggy.PluginManager("edgetest")
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints("edgetest")
    pm.register(lib)

    return pm


def cli(
    config: Optional[str] = None,
    requirements: str = "requirements.txt",
    environment: Optional[str] = None,
    notest: bool = False,
    nosetup: bool = False,
    extras: Optional[List[str]] = None,
    deps: Optional[List[str]] = None,
    command: str = "pytest",
    export: bool = False,
):
    """Create the environments and test.

    If you do not supply a configuration file, this package will search for a
    ``requirements.txt`` file and create a conda environment for each package in that file.
    """
    # Get the hooks
    pm = get_plugin_manager()
    if config and Path(config).suffix == ".cfg":
        conf = parse_cfg(filename=config, requirements=requirements)
    elif config and Path(config).suffix == ".toml":
        conf = parse_toml(filename=config, requirements=requirements)
    else:
        # Find the path to the local directory using the requirements file
        conf = gen_requirements_config(
            fname_or_buf=requirements,
            extras=extras,
            deps=deps,
            command=command,
            package_dir=str(Path(requirements).parent),
        )
    # Validate the configuration file
    docstructure = Schema()
    pm.hook.addoption(schema=docstructure)
    validator = EdgetestValidator(schema=docstructure.schema)
    if not validator.validate(conf):
        print(f"Unable to validate configuration file. Error: {validator.errors}")
        raise ValueError("Unable to validate configuration file.")
    conf = validator.document

    if environment:
        conf["envs"] = [env for env in conf["envs"] if env["name"] == environment]

    # Run the pre-test hook
    pm.hook.pre_run_hook(conf=conf)
    testers: List[TestPackage] = []
    for env in conf["envs"]:
        testers.append(
            TestPackage(
                hook=pm.hook,
                envname=env["name"],
                upgrade=env.get("upgrade"),
                lower=env.get("lower"),
                package_dir=env["package_dir"],
            )
        )
        # Set up the test environment
        if nosetup:
            print(f"Using existing environment for {env['name']}...")
            testers[-1].setup(skip=True, **env)
        else:
            testers[-1].setup(**env)
        # Run the tests
        if notest or not testers[-1].setup_status:
            print(f"Skipping tests for {env['name']}")
        else:
            testers[-1].run_tests(env["command"])

    report = gen_report(testers)
    print(f"\n\n{report}")

    if export and testers[-1].status:
        if config is not None and Path(config).name == "setup.cfg":
            parser = upgrade_setup_cfg(
                upgraded_packages=testers[-1].upgraded_packages(),
                filename=config,
            )
            with open(config, "w") as outfile:
                parser.write(outfile)
            if "options" not in parser or not parser.get("options", "install_requires"):
                print(
                    "No PEP-517 style requirements in ``setup.cfg`` to update. Updating "
                    f"{requirements}"
                )
                upgraded = upgrade_requirements(
                    fname_or_buf=requirements,
                    upgraded_packages=testers[-1].upgraded_packages(),
                )
                with open(requirements, "w") as outfile:
                    outfile.write(upgraded)
        elif config is not None and Path(config).name == "pyproject.toml":
            parser = upgrade_pyproject_toml(
                upgraded_packages=testers[-1].upgraded_packages(),
                filename=config,
            )
            with open(config, "w") as outfile:
                outfile.write(dumps(parser))
            if "project" not in parser or not parser.get("project").get("dependencies"):
                print(
                    "No dependencies in ``pyproject.toml`` to update. Updating "
                    f"{requirements}"
                )
                upgraded = upgrade_requirements(
                    fname_or_buf=requirements,
                    upgraded_packages=testers[-1].upgraded_packages(),
                )
                with open(requirements, "w") as outfile:
                    outfile.write(upgraded)
        else:
            print(f"Overwriting the requirements file {requirements}...")
            upgraded = upgrade_requirements(
                fname_or_buf=requirements,
                upgraded_packages=testers[-1].upgraded_packages(),
            )
            with open(requirements, "w") as outfile:
                outfile.write(upgraded)

    # Run the post-test hook
    pm.hook.post_run_hook(testers=testers, conf=conf)


if __name__ == "__main__":
    plac.call(cli)
