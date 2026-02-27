import aiohttp
import asyncio
import re
import io
import hashlib
import hxl.datatypes
import hxl.model
import hxl.converters
import hxl.filters
import logging
import datetime
import dateutil.parser
import zipfile
import collections
import json
import csv
import os

logger = logging.getLogger(__name__)

# Updated open_url_or_file function
async def open_url_or_file(url_or_filename, input_options):
    """Try opening a local or remote resource.

    Allows only HTTP(S) and (S)FTP URLs.

    Args:
        url_or_filename (string): the string to try opening.
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
        if file_ext is None:
            file_ext = os.path.splitext(url_or_filename)[1][1:]

        try:
            url = await munge_url(url_or_filename, input_options)
            logup("Trying to open remote resource", {"url": url_or_filename})

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    ssl=input_options.verify_ssl,
                    timeout=input_options.timeout,
                    headers=input_options.http_headers
                ) as response:
                    logup("Response status", {"url": url_or_filename, "status": response.status})
                    if response.status == 403:  # CKAN sends "403 Forbidden" for a private file
                        raise HXLAuthorizationException("Access not authorized", url=url)
                    response.raise_for_status()

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

                    return (io.BytesIO(await response.read()), mime_type, file_ext, encoding, content_length, fileno,)

        except Exception as e:
            logger.error("Cannot open URL %s (%s)", url_or_filename, str(e))
            raise e

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

# Updated munge_url function
async def munge_url(url, input_options):
    """Munge a URL to get at underlying data for well-known types.

    For example, if it's an HDX dataset, figure out the download
    link for the first resource. If it's a Kobo survey, create an
    export and get the download link (given an appropriate
    authorization header).

    Args:
        url (str): the original URL to munge
        input_options (InputOptions): options for reading a dataset.

    Returns:
        str: the actual direct-download URL

    Raises:
        hxl.input.HXLAuthorizationException: if the source requires some kind of authorization

    """
    # Example for Google Drive URL
    result = re.match(GOOGLE_DRIVE_URL, url)
    if result:
        logup("HEAD request for Google Drive URL", {"url": url})
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as response:
                if response.status in (301, 302):  # Redirect
                    new_url = response.headers['Location']
                    logup("Google Drive redirect", {"url": url, "redirect": new_url})
                    logger.info("Following Google Drive redirect to %s", new_url)
                    url = new_url

    # Add other URL munging logic here...

    return url
