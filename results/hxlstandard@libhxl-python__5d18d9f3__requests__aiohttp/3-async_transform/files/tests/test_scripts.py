"""
Unit tests for the hxl.scripts module
David Megginson
December 2014

License: Public Domain
"""

from __future__ import print_function

import unittest
import os
import sys
import subprocess
import filecmp
import difflib
import tempfile

import hxl
import hxl.scripts

root_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))
import pytest


########################################################################
# Test classes
########################################################################

class BaseTest(unittest.TestCase):
    """
    Base for test classes
    """

    async def assertOutput(self, options, output_file, input_file=None):
        if not input_file:
            input_file = self.input_file
        self.assertTrue(
            await try_script(
                self.function,
                options,
                input_file,
                expected_output_file = output_file
                )
            )

    async def assertExitStatus(self, options, exit_status=hxl.scripts.EXIT_OK, input_file=None):
        if not input_file:
            input_file = self.input_file
        self.assertTrue(
            await try_script(
                self.function,
                options,
                input_file,
                expected_exit_status = exit_status
            )
        )


class TestAdd(BaseTest):
    """
    Test the hxladd command-line tool.
    """

    def setUp(self):
        self.function = hxl.scripts.hxladd_main
        self.input_file = 'input-simple.csv'

    @pytest.mark.asyncio
    async def test_default(self):
        await self.assertOutput(['-s', 'date+reported=2015-03-31'], 'add-output-default.csv')
        await self.assertOutput(['--spec', 'date+reported=2015-03-31'], 'add-output-default.csv')

    @pytest.mark.asyncio
    async def test_headers(self):
        await self.assertOutput(['-s', 'Report Date#date+reported=2015-03-31'], 'add-output-headers.csv')
        await self.assertOutput(['--spec', 'Report Date#date+reported=2015-03-31'], 'add-output-headers.csv')

    @pytest.mark.asyncio
    async def test_before(self):
        await self.assertOutput(['-b', '-s', 'date+reported=2015-03-31'], 'add-output-before.csv')
        await self.assertOutput(['--before', '--spec', 'date+reported=2015-03-31'], 'add-output-before.csv')

        
class TestAppend(BaseTest):
    """ Test the hxlappend command-line tool. """

    def setUp(self):
        self.function = hxl.scripts.hxlappend_main
        self.input_file = 'input-simple.csv'

    @pytest.mark.asyncio
    async def test_append(self):
        await self.assertOutput(['-a', resolve_file('input-simple.csv')], 'append-dataset.csv')
        await self.assertOutput(['--append', resolve_file('input-simple.csv')], 'append-dataset.csv')


class TestClean(BaseTest):
    """
    Test the hxlclean command-line tool.
    """

    def setUp(self):
        self.function = hxl.scripts.hxlclean_main
        self.input_file = 'input-simple.csv'

    @pytest.mark.asyncio
    async def test_noheaders(self):
        await self.assertOutput(['--remove-headers'], 'clean-output-noheaders.csv')

    @pytest.mark.asyncio
    async def test_headers(self):
        await self.assertOutput([], 'clean-output-headers.csv')

    @pytest.mark.asyncio
    async def test_whitespace(self):
        await self.assertOutput(['-w', 'subsector'], 'clean-output-whitespace-tags.csv', 'input-whitespace.csv')

    @pytest.mark.asyncio
    async def test_case(self):
        await self.assertOutput(['-u', 'sector,subsector'], 'clean-output-upper.csv')
        await self.assertOutput(['-l', 'sector,subsector'], 'clean-output-lower.csv')

    # TODO: test dates and numbers


class TestCount(BaseTest):
    """
    Test the hxlcount command-line tool.
    """

    def setUp(self):
        self.function = hxl.scripts.hxlcount_main
        self.input_file = 'input-simple.csv'

    @pytest.mark.asyncio
    async def test_simple(self):
        await self.assertOutput(['-t', 'org,adm1'], 'count-output-simple.csv')
        await self.assertOutput(['--tags', 'org,adm1'], 'count-output-simple.csv')

    @pytest.mark.asyncio
    async def test_aggregated(self):
        await self.assertOutput(['-t', 'org,adm1', '-a', 'sum(targeted) as Total targeted#targeted+total'], 'count-output-aggregated.csv')

    @pytest.mark.asyncio
    async def test_count_colspec(self):
        await self.assertOutput(['-t', 'org,adm1', '-a', 'count() as Activities#output+activities'], 'count-output-colspec.csv')


class TestCut(BaseTest):
    """
    Test the hxlcut command-line tool.
    """

    def setUp(self):
        self.function = hxl.scripts.hxlcut_main
        self.input_file = 'input-simple.csv'

    @pytest.mark.asyncio
    async def test_includes(self):
        await self.assertOutput(['-i', 'sector,org,adm1'], 'cut-output-includes.csv')
        await self.assertOutput(['--include', 'sector,org,adm1'], 'cut-output-includes.csv')

    @pytest.mark.asyncio
    async def test_excludes(self):
        await self.assertOutput(['-x', 'population+sex,targeted'], 'cut-output-excludes.csv')
        await self.assertOutput(['--exclude', 'population+sex,targeted'], 'cut-output-excludes.csv')


class TestMerge(BaseTest):
    """
    Test the hxlmerge command-line tool.
    """

    def setUp(self):
        self.function = hxl.scripts.hxlmerge_main
        self.input_file = 'input-simple.csv'

    @pytest.mark.asyncio
    async def test_merge(self):
        await self.assertOutput(['-k', 'sector', '-t', 'status', '-m', resolve_file('input-merge.csv')], 'merge-output-basic.csv')
        await self.assertOutput(['--keys', 'sector', '--tags', 'status', '-m', resolve_file('input-merge.csv')], 'merge-output-basic.csv')

    @pytest.mark.asyncio
    async def test_replace(self):
        self.input_file = 'input-status.csv'
        await self.assertOutput(['-r', '-k', 'sector', '-t', 'status', '-m', resolve_file('input-merge.csv')], 'merge-output-replace.csv')
        await self.assertOutput(['--replace', '-k', 'sector', '-t', 'status', '-m', resolve_file('input-merge.csv')], 'merge-output-replace.csv')

    @pytest.mark.asyncio
    async def test_overwrite (self):
        self.input_file = 'input-status.csv'
        await self.assertOutput(['-O', '-r', '-k', 'sector', '-t', 'status', '-m', resolve_file('input-merge.csv')], 'merge-output-overwrite.csv')
        await self.assertOutput(['--overwrite', '--replace', '-k', 'sector', '-t', 'status', '-m', resolve_file('input-merge.csv')], 'merge-output-overwrite.csv')

class TestRename(BaseTest):
    """
    Test the hxlrename command-line tool.
    """

    def setUp(self):
        self.function = hxl.scripts.hxlrename_main
        self.input_file = 'input-simple.csv'

    @pytest.mark.asyncio
    async def test_single(self):
        await self.assertOutput(['-r', 'targeted:affected'], 'rename-output-single.csv')
        await self.assertOutput(['--rename', 'targeted:affected'], 'rename-output-single.csv')

    @pytest.mark.asyncio
    async def test_header(self):
        await self.assertOutput(['-r', 'targeted:Affected#affected'], 'rename-output-header.csv')

    @pytest.mark.asyncio
    async def test_multiple(self):
        await self.assertOutput(['-r', 'targeted:affected', '-r', 'org:funding'], 'rename-output-multiple.csv')


class TestSelect(BaseTest):
    """
    Test the hxlselect command-line tool.
    """

    def setUp(self):
        self.function = hxl.scripts.hxlselect_main
        self.input_file = 'input-simple.csv'

    @pytest.mark.asyncio
    async def test_eq(self):
        await self.assertOutput(['-q', 'sector=WASH'], 'select-output-eq.csv')
        await self.assertOutput(['--query', 'sector=WASH'], 'select-output-eq.csv')

    @pytest.mark.asyncio
    async def test_ne(self):
        await self.assertOutput(['-q', 'sector!=WASH'], 'select-output-ne.csv')

    @pytest.mark.asyncio
    async def test_lt(self):
        await self.assertOutput(['-q', 'targeted<200'], 'select-output-lt.csv')

    @pytest.mark.asyncio
    async def test_le(self):
        await self.assertOutput(['-q', 'targeted<=100'], 'select-output-le.csv')

    @pytest.mark.asyncio
    async def test_gt(self):
        await self.assertOutput(['-q', 'targeted>100'], 'select-output-gt.csv')

    @pytest.mark.asyncio
    async def test_ge(self):
        await self.assertOutput(['-q', 'targeted>=100'], 'select-output-ge.csv')

    @pytest.mark.asyncio
    async def test_re(self):
        await self.assertOutput(['-q', 'sector~^W..H'], 'select-output-re.csv')

    @pytest.mark.asyncio
    async def test_nre(self):
        await self.assertOutput(['-q', 'sector!~^W..H'], 'select-output-nre.csv')

    @pytest.mark.asyncio
    async def test_reverse(self):
        await self.assertOutput(['-r', '-q', 'sector=WASH'], 'select-output-reverse.csv')
        await self.assertOutput(['--reverse', '--query', 'sector=WASH'], 'select-output-reverse.csv')

    @pytest.mark.asyncio
    async def test_multiple(self):
        await self.assertOutput(['-q', 'sector=WASH', '-q', 'sector=Salud'], 'select-output-multiple.csv')


class TestSort(BaseTest):
    """
    Test the hxlsort command-line tool,.
    """

    def setUp(self):
        self.function = hxl.scripts.hxlsort_main
        self.input_file = 'input-simple.csv'

    @pytest.mark.asyncio
    async def test_default(self):
        await self.assertOutput([], 'sort-output-default.csv')

    @pytest.mark.asyncio
    async def test_tags(self):
        await self.assertOutput(['-t', 'country'], 'sort-output-tags.csv')
        await self.assertOutput(['--tags', 'country'], 'sort-output-tags.csv')

    @pytest.mark.asyncio
    async def test_numeric(self):
        await self.assertOutput(['-t', 'targeted'], 'sort-output-numeric.csv')

    @pytest.mark.asyncio
    async def test_date(self):
        self.input_file = 'input-date.csv'
        await self.assertOutput(['-t', 'date+reported'], 'sort-output-date.csv')

    @pytest.mark.asyncio
    async def test_reverse(self):
        await self.assertOutput(['-r'], 'sort-output-reverse.csv')
        await self.assertOutput(['--reverse'], 'sort-output-reverse.csv')


class TestTag(BaseTest):
    """
    Test the hxltag command-line tool.
    """

    def setUp(self):
        self.function = hxl.scripts.hxltag_main
        self.input_file = 'input-untagged.csv'

    @pytest.mark.asyncio
    async def test_full(self):
        """Use full header text for tagging."""
        await self.assertOutput([
            '-m', 'Organisation#org',
            '-m', 'Cluster#sector',
            '-m', 'Country#country',
            '-m', 'Subdivision#adm1'
        ], 'tag-output-full.csv')


    @pytest.mark.asyncio
    async def test_substrings(self):
        """Use header substrings for tagging."""
        await self.assertOutput([
            '-m', 'org#org',
            '-m', 'cluster#sector',
            '-m', 'ntry#country',
            '-m', 'div#adm1'
        ], 'tag-output-full.csv')
        await self.assertOutput([
            '-a', # force match_all
            '-m', 'org#org', # should fail
            '-m', 'cluster#sector' #should succeed
        ], 'tag-output-notsubstrings.csv')

    @pytest.mark.asyncio
    async def test_partial(self):
        """Try tagging only one row."""
        await self.assertOutput([
            '--map', 'cluster#sector'
        ], 'tag-output-partial.csv')

    @pytest.mark.asyncio
    async def test_ambiguous(self):
        """Use an ambiguous header for the second one."""
        await self.assertOutput([
            '-m', 'organisation#org',
            '-m', 'is#adm1'
        ], 'tag-output-ambiguous.csv')

    @pytest.mark.asyncio
    async def test_default_tag(self):
        """Supply a default tag."""
        await self.assertOutput([
            '-m', 'organisation#org',
            '-d', '#meta'
        ], 'tag-output-default.csv')


class TestValidate(BaseTest):
    """
    Test the hxltag command-line tool.
    """

    def setUp(self):
        self.function = hxl.scripts.hxlvalidate_main
        self.input_file = 'input-simple.csv'

    @pytest.mark.asyncio
    async def test_default_valid_status(self):
        await self.assertExitStatus([])

    def test_bad_hxl_status(self):
        self.input_file = 'input-untagged.csv'
        async def try_script():
            await self.assertExitStatus([], exit_status = hxl.scripts.EXIT_ERROR),
        # from the command line, this will get intercepted
        self.assertRaises(hxl.input.HXLTagsNotFoundException, try_script)

    def test_default_valid_status(self):
        await self.assertExitStatus([
            '--schema', resolve_file('validation-schema-valid.csv')
        ], hxl.scripts.EXIT_OK)
        await self.assertExitStatus([
            '-s', resolve_file('validation-schema-valid.csv')
        ], hxl.scripts.EXIT_OK)

    @pytest.mark.asyncio
    async def test_default_invalid_status(self):
        await self.assertExitStatus([
            '--schema', resolve_file('validation-schema-invalid.csv')
        ], hxl.scripts.EXIT_ERROR)
        await self.assertExitStatus([
            '-s', resolve_file('validation-schema-invalid.csv')
        ], hxl.scripts.EXIT_ERROR)


########################################################################
# Support functions
########################################################################


def resolve_file(name):
    """
    Resolve a file name in the test directory.
    """
    return os.path.join(root_dir, 'tests', 'files', 'test_scripts', name)

async def try_script(script_function, args, input_file, expected_output_file=None, expected_exit_status=hxl.scripts.EXIT_OK):
    """
    Test run a script in its own subprocess.
    @param args A list of arguments, including the script name first
    @param input_file The name of the input HXL file in ./files/test_scripts/
    @param expected_output_file The name of the expected output HXL file in ./files/test_scripts
    @return True if the actual output matches the expected output
    """

    with open(resolve_file(input_file), 'rb') as input:
        if expected_output_file is None:
            output = sys.stdout
        output = tempfile.NamedTemporaryFile(mode='w', newline='', delete=False)
        try:
            status = script_function(args, stdin=input, stdout=output)
            if status == expected_exit_status:
                result = True
                if expected_output_file:
                    output.close()
                    result = diff(output.name, resolve_file(expected_output_file))
            else:
                print("Script exit status: {}".format(status))
                result = False
        finally:
            # Not using with, because Windows won't allow file to be opened twice
            os.remove(output.name)
        return result


def diff(file1, file2):
    """
    Compare two files, ignoring line end differences

    If there are differences, print them to stderr in unified diff format.

    @param file1 The full pathname of the first file to compare
    @param file2 The full pathname of the second file to compare
    @return True if the files are the same, o
    """
    with open(file1, 'r') as input1:
        with open(file2, 'r') as input2:
            diffs = difflib.unified_diff(
                input1.read().splitlines(),
                input2.read().splitlines()
                )
    no_diffs = True
    for diff in diffs:
        no_diffs = False
        print(diff, file=sys.stderr)
    return no_diffs

# end
