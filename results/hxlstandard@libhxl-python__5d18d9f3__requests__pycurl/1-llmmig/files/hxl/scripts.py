import argparse, json, logging, os, re, pycurl, sys
from io import BytesIO

# Do not import hxl, to avoid circular imports
import hxl.converters, hxl.filters, hxl.input

logger = logging.getLogger(__name__)

# Function to fetch JSON data using pycurl
def get_json(url_or_filename):
    if not url_or_filename:
        return json.load(sys.stdin)

    if re.match(r'^(?:https?|s?ftp)://', url_or_filename.lower()):
        headers = make_headers(args)
        buffer = BytesIO()
        curl = pycurl.Curl()
        try:
            curl.setopt(pycurl.URL, url_or_filename)
            curl.setopt(pycurl.WRITEDATA, buffer)
            curl.setopt(pycurl.SSL_VERIFYPEER, not args.ignore_certs)
            curl.setopt(pycurl.SSL_VERIFYHOST, 2 if not args.ignore_certs else 0)
            if headers:
                curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
            curl.perform()
            curl.close()
        except pycurl.error as e:
            logger.error(f"Error fetching URL {url_or_filename}: {e}")
            sys.exit(EXIT_ERROR)

        response_body = buffer.getvalue().decode('utf-8')
        return json.loads(response_body)
    else:
        with open(url_or_filename, "r") as input:
            return json.load(input)

# Function to create HTTP headers
def make_headers(args):
    # Get custom headers
    header_strings = []
    header = os.environ.get("HXL_HTTP_HEADER")
    if header is not None:
        header_strings.append(header)
    if args.http_header is not None:
        header_strings += args.http_header
    http_headers = {}
    for header in header_strings:
        parts = header.partition(':')
        http_headers[parts[0].strip()] = parts[2].strip()
    return http_headers

# Example usage in hxlspec_main
def hxlspec_main(args, stdin=STDIN, stdout=sys.stdout, stderr=sys.stderr):
    """ Run hxlspec with command-line arguments.

    Process a HXL JSON spec.

    Args:
        args (list): a list of command-line arguments
        stdin (io.IOBase): alternative standard input (mainly for testing)
        stdout (io.IOBase): alternative standard output (mainly for testing)
        stderr (io.IOBase): alternative standard error (mainly for testing)

    """

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
