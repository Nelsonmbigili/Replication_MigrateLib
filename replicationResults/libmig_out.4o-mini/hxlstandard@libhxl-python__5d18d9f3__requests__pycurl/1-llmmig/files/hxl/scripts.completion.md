### Explanation of Changes

To migrate the provided code from using the `requests` library to the `pycurl` library, the following changes were made:

1. **Import Statement**: The `requests` library was removed and replaced with `pycurl`.
2. **HTTP Request Handling**: The code that previously used `requests.get()` to make HTTP requests was replaced with `pycurl` functionality. This involved setting up a `pycurl.Curl` object, configuring it with the necessary options (like URL, headers, etc.), and performing the request.
3. **Response Handling**: The response from `pycurl` is handled differently than `requests`. The response data is captured using a callback function that writes the output to a buffer, which is then read into a variable.
4. **Error Handling**: The error handling for HTTP requests was adjusted to accommodate `pycurl`'s way of reporting errors.

### Modified Code

Here is the modified code with the changes applied:

```python
"""Console scripts
David Megginson
April 2015

This module implements the command-line scripts for HXL
processing. Most of them produce HXL output that another command can
use as input, so you can chain them together into a pipeline, e.g.

``` shell
$ cat dataset.csv | hxlselect -q "#org=UNICEF" \\
  | hxlsort -t "#value+committed" > output.csv
```

The ``-h`` option will provide more information about each script.

### About this module

**Author:** David Megginson

**Organisation:** UN OCHA

**License:** Public Domain

**Started:** April 2015

"""

from __future__ import print_function

import argparse, json, logging, os, re, pycurl, sys
from io import BytesIO

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

# ... (other functions remain unchanged)

def hxlspec_main(args, stdin=STDIN, stdout=sys.stdout, stderr=sys.stderr):
    """ Run hxlspec with command-line arguments.

    Process a HXL JSON spec.

    Args:
        args (list): a list of command-line arguments
        stdin (io.IOBase): alternative standard input (mainly for testing)
        stdout (io.IOBase): alternative standard output (mainly for testing)
        stderr (io.IOBase): alternative standard error (mainly for testing)

    """

    def get_json(url_or_filename):
        if not url_or_filename:
            return json.load(stdin)

        if re.match(r'^(?:https?|s?ftp)://', url_or_filename.lower()):
            headers = make_headers(args)
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, url_or_filename)
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.HTTPHEADER, headers)
            c.setopt(c.SSL_VERIFYPEER, not args.ignore_certs)
            try:
                c.perform()
            except pycurl.error as e:
                logger.error("HTTP request failed: %s", e)
                raise
            finally:
                c.close()
            response_data = buffer.getvalue()
            return json.loads(response_data)
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

# ... (rest of the code remains unchanged)
```

In this modified code, the `requests` library has been replaced with `pycurl`, and the HTTP request handling has been adjusted accordingly. The rest of the code remains unchanged to maintain the original functionality and structure.