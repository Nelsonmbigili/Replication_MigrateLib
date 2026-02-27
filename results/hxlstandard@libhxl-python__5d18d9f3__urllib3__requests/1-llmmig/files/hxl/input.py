"""Input/output library for the Humanitarian Exchange Language (HXL) v1.0

This module handles all contact with the outside world (reading and
writing data in different formats through different channels).

Examples:
    ```
    # Read a HXL-hashtagged dataset
    dataset = hxl.input.data("http://example.org/hxl-example.csv")

    # Read a non-HXL dataset and add hashtags
    specs = [['Cluster', '#sector'], ["Province", "#adm1+name"]]
    tagged_data = hxl.input.tagger("http://example.org/non-hxl-example.csv", specs)

    # Write out a dataset as JSON
    hxl.input.write_json(sys.stdout, dataset)

    # Write out a dataset as CSV
    hxl.input.write_csv(sys.stdout, dataset)
    ```

Author:
    David Megginson

License:
    Public Domain

"""

import hxl, hxl.filters

from hxl.util import logup

import abc, collections, csv, datetime, dateutil.parser, hashlib, \
    io, io_wrapper, json, jsonpath_ng.ext, logging, \
    os.path, re, requests, shutil, six, sys, \
    tempfile, time, xlrd3 as xlrd, zipfile

logger = logging.getLogger(__name__)

__all__ = (
    "data",
    "tagger",
    "write_hxl",
    "write_json",
    "make_input",
    "HXLIOException",
    "HXLAuthorizationException",
    "HXLParseException",
    "HXLTagsNotFoundException",
    "AbstractInput",
    "CSVInput",
    "JSONInput",
    "ExcelInput",
    "ArrayInput",
    "InputOptions",
    "HXLReader",
    "from_spec",
)


########################################################################
# Exported functions
########################################################################


def open_url_or_file(url_or_filename, input_options):
    """Try opening a local or remote resource.

    Allows only HTTP(S) and (S)FTP URLs.

    Args:
        url_or_filename (string): the string to try openining.
        input_options (InputOptions): options for reading a dataset.

    Returns:
        sequence of
          input (io.IOBase)
          mime_type (string or None)
          file_ext (string or None)
          encoding (string or None)
          content_length (long or None)
          fileno (int)

    Raises:
        IOError: if there's an error opening the data stream
    """
    mime_type = None
    file_ext = None
    encoding = None
    content_length = None
    fileno = None

    # Try for file extension
    result = re.search(r'\.([A-Za-z0-9]{1,5})$', url_or_filename)
    if result:
        file_ext = result.group(1).lower()

    result = re.match(r'^(?:https?|s?ftp)://([^/]+)', url_or_filename.lower())
    if result:

        # Check for possible exploits when allow_local is False
        if not input_options.allow_local:

            hostname = result.group(1).lower().strip()

            # forbid dotted quads
            if re.match(r'^[0-9.]+$', hostname):
                raise HXLIOException("Security settings forbid accessing host via IP address {}", hostname)

            # forbid localhost
            if hostname == "localhost":
                raise HXLIOException("Security settings forbid accessing localhost")

            # forbid localhost
            if hostname.endswith(".localdomain"):
                raise HXLIOException("Security settings forbid accessing hostnames ending in .localdomain: {}", hostname)

        # It looks like a URL

        # grab the file extension again, but remove the leading '.'

        if file_ext is None:
            file_ext = os.path.splitext(urllib.parse.urlparse(url_or_filename).path)[1][1:]
        
        try:
            url = munge_url(url_or_filename, input_options)
            logup("Trying to open remote resource", {"url": url_or_filename})
            response = requests.get(
                url,
                stream=True,
                verify=input_options.verify_ssl,
                timeout=input_options.timeout,
                headers=input_options.http_headers
            )
            logup("Response status", {"url": url_or_filename, "status": response.status_code})
            if (response.status_code == 403): # CKAN sends "403 Forbidden" for a private file
                raise HXLAuthorizationException("Access not authorized", url=url)
            else:
                response.raise_for_status()
        except Exception as e:
            logger.error("Cannot open URL %s (%s)", url_or_filename, str(e))
            raise e

        content_type = response.headers.get('content-type')
        if content_type:
            result = re.match(r'^(\S+)\s*;\s*charset=(\S+)$', content_type)
            if result:
                mime_type = result.group(1).lower()
                encoding = result.group(2).lower()
            else:
                mime_type = content_type.lower()

        content_length = response.headers.get('content-length')
        if content_length is not None:
            try:
                content_length = int(content_length)
            except:
                content_length = None

        # return (RequestResponseIOWrapper(response), mime_type, file_ext, encoding, content_length, fileno,)
        return (io.BytesIO(response.content), mime_type, file_ext, encoding, content_length, fileno,)

    elif input_options.allow_local:
        # Default to a local file, if allowed
        try:
            info = os.stat(url_or_filename)
            content_length = info.st_size
            file = io.open(url_or_filename, 'rb')
            fileno = file.fileno()
            return (file, mime_type, file_ext, encoding, content_length, fileno,)
        except Exception as e:
            logger.error("Cannot open local HXL file %s (%s)", url_or_filename, str(e))
            raise e

    else:
        # Forbidden to try local (allow_local is False), so give up.
        logger.error('Security settings forbid accessing local files or non http(s)/ftp(s) URL schemes: %s', url_or_filename)
        raise HXLIOException(
            "Only http(s) and (s)ftp URLs allowed: {}".format(url_or_filename),
            url=url_or_filename
        )
