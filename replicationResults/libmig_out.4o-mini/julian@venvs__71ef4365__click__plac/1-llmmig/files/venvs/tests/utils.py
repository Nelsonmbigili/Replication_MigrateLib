from contextlib import suppress
from io import StringIO
from textwrap import dedent
import sys

from filesystems import Path
from filesystems.exceptions import FileExists, FileNotFound
import filesystems.memory

from venvs import _cli, _config
from venvs.common import _EX_OK, Locator, VirtualEnv
import plac


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
        default_map = dict(
            link_dir=str(self.link_dir),
            locator=self.locator,
            filesystem=self.filesystem,
        )
        try:
            plac.call(self._fix_plac(_cli.main), *argv, **default_map)
        except SystemExit as e:
            result_exit_code = e.code
        else:
            result_exit_code = 0

        self.assertEqual(
            result_exit_code,
            exit_status,
            msg=dedent(
                f"""
                Different exit code, {result_exit_code} != {exit_status}

                stderr:

                    {self.stderr.getvalue()!r}
                """,
            ),
        )
        return self.stdout.getvalue(), self.stderr.getvalue()

    def _fix_plac(self, real_main):
        """
        Plac does not require the same output redirection as Click.
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
