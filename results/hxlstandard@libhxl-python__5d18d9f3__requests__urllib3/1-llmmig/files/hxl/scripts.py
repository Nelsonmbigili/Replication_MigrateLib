import argparse, json, logging, os, re, sys
import urllib3  # Replacing requests with urllib3

# Do not import hxl, to avoid circular imports
import hxl.converters, hxl.filters, hxl.input

logger = logging.getLogger(__name__)

def hxlspec_main(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
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
            http = urllib3.PoolManager()  # Using urllib3's PoolManager
            try:
                response = http.request(
                    'GET',
                    url_or_filename,
                    headers=headers,
                    cert_reqs='CERT_NONE' if args.ignore_certs else 'CERT_REQUIRED'
                )
                if response.status != 200:
                    raise Exception(f"HTTP error {response.status}: {url_or_filename}")
                return json.loads(response.data.decode('utf-8'))  # Decode and parse JSON
            except Exception as e:
                logger.error(f"Error fetching JSON from {url_or_filename}: {e}")
                raise
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


def make_headers(args):
    # get custom headers
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
