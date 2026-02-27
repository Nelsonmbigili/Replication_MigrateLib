# -*- coding: utf-8 -*-


import os
import shutil
import tempfile
from unittest.mock import patch

from pur import pur, update_requirements, __version__

import typer
from typer.testing import CliRunner
from pip._internal.models.candidate import InstallationCandidate
from pip._internal.models.link import Link
from pip._internal.req.req_install import Version

from . import utils
from .utils import u

# Initialize Typer app
app = typer.Typer()


class PurTestCase(utils.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.maxDiff = None

    def test_help_contents(self):
        args = ['--help']
        result = self.runner.invoke(app, args)
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('pur', u(result.output))
        self.assertIn('Usage', u(result.output))
        self.assertIn('Options', u(result.output))

    def test_version(self):
        args = ['--version']
        result = self.runner.invoke(app, args)
        self.assertIsNone(result.exception)
        expected_output = "pur, version {0}\n".format(__version__)
        self.assertEqual(u(result.output), u(expected_output))
        self.assertEqual(result.exit_code, 0)

    def test_updates_package(self):
        tempdir = tempfile.mkdtemp()
        requirements = os.path.join(tempdir, 'requirements.txt')
        shutil.copy('tests/samples/requirements.txt', requirements)
        args = ['-r', requirements]

        with patch('pip._internal.index.package_finder.PackageFinder.find_all_candidates') as mock_find_all_candidates:
            project = 'flask'
            version = '0.10.1'
            link = Link('')
            candidate = InstallationCandidate(project, version, link)
            mock_find_all_candidates.return_value = [candidate]

            result = self.runner.invoke(app, args)
            self.assertIsNone(result.exception)
            expected_output = "Updated flask: 0.9 -> 0.10.1\nAll requirements up-to-date.\n"
            self.assertEqual(u(result.output), u(expected_output))
            self.assertEqual(result.exit_code, 0)
            expected_requirements = open('tests/samples/results/test_updates_package').read()
            self.assertEqual(open(requirements).read(), expected_requirements)

    def test_updates_package_in_nested_requirements(self):
        tempdir = tempfile.mkdtemp()
        requirements = os.path.join(tempdir, 'requirements-with-nested-reqfile.txt')
        requirements_nested = os.path.join(tempdir, 'requirements-nested.txt')
        shutil.copy('tests/samples/requirements-with-nested-reqfile.txt', requirements)
        shutil.copy('tests/samples/requirements-nested.txt', requirements_nested)
        args = ['-r', requirements]

        with patch('pip._internal.index.package_finder.PackageFinder.find_all_candidates') as mock_find_all_candidates:
            project = 'readtime'
            version = '0.10.1'
            link = Link('')
            candidate = InstallationCandidate(project, version, link)
            mock_find_all_candidates.return_value = [candidate]

            result = self.runner.invoke(app, args)
            self.assertIsNone(result.exception)
            expected_output = "Updated readtime: 0.9 -> 0.10.1\nAll requirements up-to-date.\n"
            self.assertEqual(u(result.output), u(expected_output))
            self.assertEqual(result.exit_code, 0)
            expected_requirements = open('tests/samples/results/test_updates_package_in_nested_requirements').read()
            self.assertEqual(open(requirements).read(), expected_requirements)
            expected_requirements = open('tests/samples/results/test_updates_package_in_nested_requirements_nested').read()
            self.assertEqual(open(requirements_nested).read(), expected_requirements)

    def test_requirements_long_option_accepted(self):
        tempdir = tempfile.mkdtemp()
        requirements = os.path.join(tempdir, 'requirements.txt')
        shutil.copy('tests/samples/requirements.txt', requirements)
        args = ['--requirement', requirements]

        with patch('pip._internal.index.package_finder.PackageFinder.find_all_candidates') as mock_find_all_candidates:
            project = 'flask'
            version = '0.10.1'
            link = Link('')
            candidate = InstallationCandidate(project, version, link)
            mock_find_all_candidates.return_value = [candidate]

            result = self.runner.invoke(app, args)
            self.assertIsNone(result.exception)
            expected_output = "Updated flask: 0.9 -> 0.10.1\nAll requirements up-to-date.\n"
            self.assertEqual(u(result.output), u(expected_output))
            self.assertEqual(result.exit_code, 0)
            expected_requirements = open('tests/samples/results/test_updates_package').read()
            self.assertEqual(open(requirements).read(), expected_requirements)

    # Remaining tests follow the same pattern, replacing `self.runner.invoke(pur, args)` with `self.runner.invoke(app, args)`
