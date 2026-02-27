import aiohttp
import asyncio

def hxlspec_main(args, stdin=STDIN, stdout=sys.stdout, stderr=sys.stderr):
    """ Run hxlspec with command-line arguments.

    Process a HXL JSON spec.

    Args:
        args (list): a list of command-line arguments
        stdin (io.IOBase): alternative standard input (mainly for testing)
        stdout (io.IOBase): alternative standard output (mainly for testing)
        stderr (io.IOBase): alternative standard error (mainly for testing)

    """

    async def get_json(url_or_filename):
        if not url_or_filename:
            return json.load(stdin)

        if re.match(r'^(?:https?|s?ftp)://', url_or_filename.lower()):
            headers = make_headers(args)
            ssl_context = None if args.ignore_certs else True
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url_or_filename, ssl=ssl_context) as response:
                    response.raise_for_status()
                    return await response.json()
        else:
            with open(url_or_filename, "r") as input:
                return json.load(input)

    async def main():
        parser = make_args('Process a HXL JSON spec')
        parser.add_argument(
            '-s',
            '--spec',
            help="JSON processing specification",
            required=True,
            metavar="spec.json",
            type=await get_json,
        )

        args = parser.parse_args(args)

        do_common_args(args)

        with make_input(args, stdin) as input, make_output(args, stdout) as output:
            source = hxl.input.from_spec(args.spec, input=input, allow_local_ok=True)
            hxl.input.write_hxl(output, source, show_tags=not args.strip_tags)

    asyncio.run(main())
