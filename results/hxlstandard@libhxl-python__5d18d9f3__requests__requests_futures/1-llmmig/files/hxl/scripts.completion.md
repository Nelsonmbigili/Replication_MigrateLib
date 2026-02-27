### Explanation of Changes

To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:

1. **Library Import**: Replaced the `requests` import with `requests_futures.sessions.FuturesSession`. The `requests_futures` library provides asynchronous capabilities by wrapping `requests` in a `FuturesSession`.

2. **Session Creation**: Replaced direct calls to `requests.get` with the use of a `FuturesSession` object. This allows for asynchronous HTTP requests.

3. **Handling Futures**: Since `requests_futures` returns a `Future` object, the `.result()` method is used to retrieve the actual response when needed.

4. **Backward Compatibility**: The synchronous behavior of `requests` is preserved by calling `.result()` immediately after making the request, ensuring the rest of the code remains unchanged.

---

### Modified Code

Below is the updated code with the migration to `requests_futures`:

```python
from __future__ import print_function

import argparse, json, logging, os, re, sys
from requests_futures.sessions import FuturesSession  # Updated import

# Do not import hxl, to avoid circular imports
import hxl.converters, hxl.filters, hxl.input

logger = logging.getLogger(__name__)

# Other constants and functions remain unchanged...

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
            session = FuturesSession()  # Use FuturesSession for asynchronous requests
            future = session.get(url_or_filename, verify=(not args.ignore_certs), headers=headers)
            response = future.result()  # Wait for the response and retrieve it
            response.raise_for_status()
            return response.json()
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
```

---

### Key Points

1. **Asynchronous Requests**: The `FuturesSession` object allows for asynchronous HTTP requests. However, since the original code is synchronous, `.result()` is called immediately to block until the response is available.

2. **Minimal Changes**: Only the parts of the code that directly interact with `requests` were modified. The rest of the code remains unchanged to ensure compatibility with the existing application.

3. **Backward Compatibility**: The behavior of the code remains the same as before, with the added benefit of being able to handle asynchronous requests in the future if needed.