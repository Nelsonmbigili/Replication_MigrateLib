"""Console scripts
David Megginson
April 2015

This module implements the command-line scripts for HXL
processing. Most of them produce HXL output that another command can
use as input, so you can chain them together into a pipeline, e.g.


The ``-h`` option will provide more information about each script.

### About this module

**Author:** David Megginson

**Organisation:** UN OCHA

**License:** Public Domain

**Started:** April 2015

"""

from __future__ import print_function

import argparse, json, logging, os, re, sys
import treq  # Replaced requests with treq
from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks

# Do not import hxl, to avoid circular imports
import hxl.converters, hxl.filters, hxl.input


logger = logging.getLogger(__name__)


# Export only the script entry points
# (add any new scripts here)
__all__ = (
    'hxladd',
    'hxlappend',
    'hxlclean',
    'hxlcount',
    'hxlcut',
    'hxldedup',
    'hxlexpand',
    'hxlexplode',
    'hxlfill',
    'hxlimplode',
    'hxlhash',
    'hxlinfo',
    'hxlmerge',
    'hxlrename',
    'hxlreplace',
    'hxlselect',
    'hxlsort',
    'hxlspec',
    'hxltag',
    'hxlvalidate',
)


STDIN = sys.stdin.buffer
""" Constant: standard input (Python3) """

# Posix exit codes

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_SYNTAX = 2


#
# Console script entry points
#


def hxladd():
    """ Entry point for hxladd console script """
    run_script(hxladd_main)


def hxlappend():
    """ Entry point for hxlappend console script """
    run_script(hxlappend_main)


def hxlclean():
    """ Entry point for hxlclean console script """
    run_script(hxlclean_main)


def hxlcount():
    """ Entry point for hxlcount console script """
    run_script(hxlcount_main)


def hxlcut():
    """ Entry point for hxlcut console script """
    run_script(hxlcut_main)


def hxldedup():
    """ Entry point for hxldedup console script """
    run_script(hxldedup_main)


def hxlhash():
    """ Entry point for hxlhash console script """
    run_script(hxlhash_main)


def hxlinfo():
    """ Entry point for hxlinfo console script """
    run_script(hxlinfo_main)


def hxlmerge():
    """ Entry point for hxlmerge console script """
    run_script(hxlmerge_main)


def hxlrename():
    """ Entry point for hxlrename console script """
    run_script(hxlrename_main)


def hxlreplace():
    """ Entry point for hxlreplace console script """
    run_script(hxlreplace_main)


def hxlfill():
    """ Entry point for hxlfill console script """
    run_script(hxlfill_main)


def hxlexpand():
    """ Entry point for hxlexpand console script """
    run_script(hxlexpand_main)


def hxlexplode():
    """ Entry point for hxlexplode console script """
    run_script(hxlexplode_main)


def hxlimplode():
    """ Entry point for hxlimplode console script """
    run_script(hxlimplode_main)


def hxlselect():
    """ Entry point for hxlselect console script """
    run_script(hxlselect_main)


def hxlsort():
    """ Entry point for hxlsort console script """
    run_script(hxlsort_main)


def hxlspec():
    """ Entry point for hxlspec console script """
    run_script(hxlspec_main)


def hxltag():
    """ Entry point for hxltag console script """
    run_script(hxltag_main)


def hxlvalidate():
    """ Entry point for hxlvalidate console script """
    run_script(hxlvalidate_main)


#
# Main scripts for command-line tools.
#

@inlineCallbacks
def hxlspec_main(args, stdin=STDIN, stdout=sys.stdout, stderr=sys.stderr):
    """ Run hxlspec with command-line arguments.

    Process a HXL JSON spec.

    Args:
        args (list): a list of command-line arguments
        stdin (io.IOBase): alternative standard input (mainly for testing)
        stdout (io.IOBase): alternative standard output (mainly for testing)
        stderr (io.IOBase): alternative standard error (mainly for testing)

    """

    @inlineCallbacks
    def get_json(url_or_filename):
        if not url_or_filename:
            return json.load(stdin)

        if re.match(r'^(?:https?|s?ftp)://', url_or_filename.lower()):
            headers = make_headers(args)
            response = yield treq.get(
                url_or_filename,
                headers=headers,
                verify=(not args.ignore_certs),
            )
            response.raise_for_status()
            result = yield treq.json_content(response)
            return result
        else:
            with open(url_or_filename, "r") as input:
                return json.load(input)

    parser = make_args('Process a HXL JSON spec')
    parser.add_argument(
        '-s',
        '--spec',
        help="JSON processing specification",
        required=True,
        metavar="spec.json",
        type=get_json,
    )

    args = parser.parse_args(args)

    do_common_args(args)

    with make_input(args, stdin) as input, make_output(args, stdout) as output:
        source = hxl.input.from_spec(args.spec, input=input, allow_local_ok=True)
        hxl.input.write_hxl(output, source, show_tags=not args.strip_tags)
