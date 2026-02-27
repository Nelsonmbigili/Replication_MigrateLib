The following Python code currently uses the library "click" version 8.1.7.
Migrate this code to use the library "typer" version 0.15.2 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "click" to "typer".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "click" and "typer".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from contextlib import suppress
from io import StringIO
from textwrap import dedent
import sys

from filesystems import Path
from filesystems.exceptions import FileExists, FileNotFound
import click.testing
import filesystems.memory

from venvs import _cli, _config
from venvs.common import _EX_OK, Locator, VirtualEnv


class CLIMixin:
    def setUp(self):
        super().setUp()

        self.stdin = StringIO()
        self.stdout = StringIO()
        self.stderr = StringIO()

        self.filesystem = filesystems.memory.FS()

        self.root_dir = Path("virtualenvs")
        self.filesystem.create_directory(self.root_dir)

        self.link_dir = Path("bin")
        self.filesystem.create_directory(self.link_dir)

        self.locator = Locator(
            root=self.root_dir,
            make_virtualenv=lambda **kwargs: VirtualEnv(
                create=self._fake_create,
                install=self._fake_install,
                **kwargs,
            ),
        )

    def assertConfigEqual(self, expected):
        actual = _config.Config.from_locator(
            filesystem=self.filesystem,
            locator=self.locator,
        )
        self.assertEqual(actual, _config.Config.from_string(expected))

    @property
    def linked(self):
        return {
            link.basename(): self.filesystem.readlink(link)
            for link in self.filesystem.children(self.link_dir)
            if self.filesystem.is_link(link)
        }

    def installed(self, virtualenv):
        base = virtualenv.path
        try:
            with self.filesystem.open(base / "packages") as f:
                packages = {line.strip() for line in f}
        except FileNotFound:
            packages = set()

        try:
            with self.filesystem.open(base / "reqs") as f:
                reqs = {line.strip() for line in f}
        except FileNotFound:
            reqs = set()

        return packages, reqs

    def _fake_create(self, virtualenv, **kwargs):
        # FIXME: ...
        if virtualenv.path.basename() == "magicexplodingvirtualenvoncreate":
            raise ZeroDivisionError("Hey you told me to blow up on create!")

        with suppress(FileExists):
            self.filesystem.create_directory(path=virtualenv.path.parent())

        with suppress(FileExists):
            self.filesystem.create_directory(path=virtualenv.path)

    def _fake_install(self, virtualenv, packages, requirements, **kwargs):
        # FIXME: ...
        if virtualenv.path.basename() == "magicexplodingvirtualenvoninstall":
            raise ZeroDivisionError("Hey you told me to blow up on install!")

        base = virtualenv.path
        with self.filesystem.open(base / "packages", "at") as f:
            f.writelines(package + "\n" for package in packages)
        with self.filesystem.open(base / "reqs", "at") as f:
            f.writelines(req + "\n" for req in requirements)

    def run_cli(self, argv=(), exit_status=_EX_OK):
        runner = click.testing.CliRunner()
        default_map = dict(
            link_dir=str(self.link_dir),
            locator=self.locator,
            filesystem=self.filesystem,
        )
        result = runner.invoke(
            self._fix_click(_cli.main),
            args=argv,
            default_map=dict(
                converge=default_map,
                create=default_map,
                find=default_map,
                remove=default_map,
                temporary=default_map,
            ),
            catch_exceptions=False,
        )

        self.assertEqual(
            result.exit_code,
            exit_status,
            msg=dedent(
                f"""
                Different exit code, {result.exit_code} != {exit_status}

                stderr:

                    {self.stderr.getvalue()!r}
                """,
            ),
        )
        return self.stdout.getvalue(), self.stderr.getvalue()

    def _fix_click(self, real_main):
        """
        Click is really really really annoying.

        It patches sys.stdout and sys.stderr to the same exact StringIO.
        """

        class Fixed:
            def __getattr__(self, attr):
                return getattr(real_main, attr)

            def main(this, *args, **kwargs):
                stdout, sys.stdout = sys.stdout, self.stdout
                stderr, sys.stderr = sys.stderr, self.stderr
                real_main.main(*args, **kwargs)
                sys.stdout = stdout
                sys.stderr = stderr

        return Fixed()

```