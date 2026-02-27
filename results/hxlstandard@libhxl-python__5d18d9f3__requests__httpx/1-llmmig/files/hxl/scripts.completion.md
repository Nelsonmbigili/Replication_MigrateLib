### Explanation of Changes:
To migrate the code from the `requests` library to the `httpx` library, the following changes were made:
1. **Import Replacement**: Replaced `import requests` with `import httpx`.
2. **HTTP Requests**: Updated all instances of `requests.get` to `httpx.get`. The `httpx` library has a similar API to `requests`, so the changes are minimal.
3. **SSL Verification**: The `verify` parameter in `httpx.get` works the same way as in `requests.get`.
4. **Response Handling**: The `httpx` response object (`httpx.Response`) is compatible with the `requests` response object for the methods used in the code (e.g., `.json()` and `.raise_for_status()`).

### Modified Code:
Below is the updated code with the migration to `httpx`:

```python
import argparse, json, logging, os, re, httpx, sys

# Do not import hxl, to avoid circular imports
import hxl.converters, hxl.filters, hxl.input

# Other parts of the code remain unchanged...

def hxlspec_main(args, stdin=STDIN, stdout=sys.stdout, stderr=sys.stderr):
    """ Run hxlspec with command-line arguments.

    Process a HXL JSON spec.

    Args:
        args (list): a list of command-line arguments
        stdin (io.IOBase): alternative standard input (mainly for testing)
        stdout (io.IOBase): alternative standard output (mainly for testing)
        stderr (io.IOBase): alternative standard error (mainly for testing)

    """

    def get_json (url_or_filename):

        if not url_or_filename:
            return json.load(stdin)

        if re.match(r'^(?:https?|s?ftp)://', url_or_filename.lower()):
            headers = make_headers(args)
            response = httpx.get(url_or_filename, verify=(not args.ignore_certs), headers=headers)
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

# Other parts of the code remain unchanged...
```

### Key Points:
- The `httpx.get` function is used in place of `requests.get`.
- The `verify` parameter and `headers` dictionary are passed to `httpx.get` in the same way as they were for `requests.get`.
- The rest of the code remains unchanged, as the `httpx` library is designed to be a drop-in replacement for `requests` in most cases.