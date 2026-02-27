import functools
import re
import sys
import textwrap
import unittest

from plac import Interpreter, call

from beancount import loader
from beancount.utils import test_utils

from beanquery import shell


@functools.lru_cache(None)
def load():
    entries, errors, options = loader.load_string(textwrap.dedent("""
      2022-01-01 open Assets:Checking         USD
      2022-01-01 open Assets:Federal:401k     IRAUSD
      2022-01-01 open Assets:Gold             GLD
      2022-01-01 open Assets:Vacation         VACHR
      2022-01-01 open Assets:Vanguard:RGAGX   RGAGX
      2022-01-01 open Expenses:Commissions    USD
      2022-01-01 open Expenses:Food           USD
      2022-01-01 open Expenses:Home:Rent      USD
      2022-01-01 open Expenses:Taxes:401k     IRAUSD
      2022-01-01 open Expenses:Taxes:Federal  USD
      2022-01-01 open Expenses:Tests          USD
      2022-01-01 open Expenses:Vacation       VACHR
      2022-01-01 open Income:ACME             USD
      2022-01-01 open Income:Gains            USD
      2022-01-01 open Income:Vacation         VACHR

      2022-01-01 * "ACME" "Salary"
        Assets:Checking           10.00 USD
        Income:ACME              -11.00 USD
        Expenses:Taxes:Federal     1.00 USD
        Assets:Federal:401k       -2.00 IRAUSD
        Expenses:Taxes:401k        2.00 IRAUSD
        Assets:Vacation               5 VACHR
        Income:Vacation              -5 VACHR

      2022-01-01 * "Rent"
        Assets:Checking           42.00 USD
        Expenses:Home:Rent        42.00 USD

      2022-01-02 * "Holidays"
        Assets:Vacation              -1 VACHR
        Expenses:Vacation

      2022-01-03 * "Test 01"
        Assets:Checking            1.00 USD
        Expenses:Tests

      2022-01-04 * "My Fovorite Plase" "Eating out alone"
        Assets:Checking            4.00 USD
        Expenses:Food

      2022-01-05 * "Invest"
        Assets:Checking         -359.94 USD
        Assets:Vanguard:RGAGX     2.086 RGAGX {172.55 USD}

      2013-10-23 * "Buy Gold"
        Assets:Checking        -1278.67 USD
        Assets:Gold                   9 GLD {141.08 USD}
        Expenses:Commissions          8.95 USD

      2022-01-07 * "Sell Gold"
        Assets:Gold                 -16 GLD {147.01 USD} @ 135.50 USD
        Assets:Checking         2159.05 USD
        Expenses:Commissions       8.95 USD
        Income:Gains             184.16 USD

      2022-01-08 * "Sell Gold"
        Assets:Gold                 -16 GLD {147.01 USD} @ 135.50 USD
        Assets:Checking         2159.05 USD
        Expenses:Commissions       8.95 USD
        Income:Gains             184.16 USD

      2022-02-01 * "ACME" "Salary"
        Assets:Checking           10.00 USD
        Income:ACME              -11.00 USD
        Expenses:Taxes:Federal     1.00 USD
        Assets:Federal:401k       -2.00 IRAUSD
        Expenses:Taxes:401k        2.00 IRAUSD
        Assets:Vacation               5 VACHR
        Income:Vacation              -5 VACHR

      2022-02-01 * "Rent"
        Assets:Checking           43.00 USD
        Expenses:Home:Rent        43.00 USD

      2022-02-02 * "Test 02"
        Assets:Checking            2.00 USD
        Expenses:Tests

      2030-01-01 query "taxes" "
        SELECT
          date, description, position, balance
        WHERE
          account ~ 'Taxes'
        ORDER BY date DESC
        LIMIT 20"

      2015-01-01 query "home" "
        SELECT
          last(date) as latest,
          account,
          sum(position) as total
        WHERE
          account ~ ':Home:'
        GROUP BY account"

    """))
    return entries, errors, options


def run_shell_command(cmd):
    """Run a shell command and return its output."""
    with test_utils.capture('stdout') as stdout, test_utils.capture('stderr') as stderr:
        shell_obj = shell.BQLShell(None, sys.stdout)
        entries, errors, options = load()
        shell_obj.context.attach('beancount:', entries=entries, errors=errors, options=options)
        shell_obj._extract_queries(entries)  # pylint: disable=protected-access
        shell_obj.onecmd(cmd)
    return stdout.getvalue(), stderr.getvalue()


def runshell(function):
    """Decorate a function to run the shell and return the output."""
    def wrapper(self):
        out, err = run_shell_command(function.__doc__)
        return function(self, out, err)
    return wrapper


class TestShell(unittest.TestCase):
    """Base class for command-line program test cases."""

    def main(self, *args):
        init_filename = shell.INIT_FILENAME
        history_filename = shell.HISTORY_FILENAME
        try:
            shell.INIT_FILENAME = ''
            shell.HISTORY_FILENAME = ''
            result = call(shell.main, args)
            self.assertEqual(result, 0)
            return result
        finally:
            shell.INIT_FILENAME = init_filename
            shell.HISTORY_FILENAME = history_filename


if __name__ == '__main__':
    unittest.main()
