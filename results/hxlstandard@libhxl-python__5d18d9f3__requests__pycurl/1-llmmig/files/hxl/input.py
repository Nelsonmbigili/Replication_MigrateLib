import pycurl
from io import BytesIO
import json
import re
import datetime
import dateutil.parser
import logging

logger = logging.getLogger(__name__)

def _pycurl_request(url, method="GET", headers=None, data=None, verify_ssl=True, timeout=None):
    """
    Perform an HTTP request using pycurl.

    Args:
        url (str): The URL to request.
        method (str): HTTP method ("GET", "POST", "HEAD").
        headers (dict): Optional HTTP headers.
        data (str): Optional data for POST requests.
        verify_ssl (bool): Whether to verify SSL certificates.
        timeout (int): Timeout in seconds.

    Returns:
        tuple: (status_code, response_body, response_headers)
    """
    buffer = BytesIO()
    header_buffer = BytesIO()
    curl = pycurl.Curl()

    try:
        curl.setopt(pycurl.URL, url.encode('utf-8'))
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.setopt(pycurl.HEADERFUNCTION, header_buffer.write)

        if headers:
            curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])

        if method == "POST":
            curl.setopt(pycurl.POST, 1)
            if data:
                curl.setopt(pycurl.POSTFIELDS, data)
        elif method == "HEAD":
            curl.setopt(pycurl.NOBODY, 1)

        if not verify_ssl:
            curl.setopt(pycurl.SSL_VERIFYHOST, 0)
            curl.setopt(pycurl.SSL_VERIFYPEER, 0)

        if timeout:
            curl.setopt(pycurl.TIMEOUT, timeout)

        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        response_body = buffer.getvalue().decode('utf-8')
        response_headers = header_buffer.getvalue().decode('utf-8')

        return status_code, response_body, response_headers

    except pycurl.error as e:
        logger.error(f"pycurl error: {e}")
        raise IOError(f"pycurl error: {e}")
    finally:
        curl.close()


def open_url_or_file(url_or_filename, input_options):
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

        # grab the file extension again, but remove the leading '.'

        if file_ext is None:
            file_ext = os.path.splitext(urllib.parse.urlparse(url_or_filename).path)[1][1:]

        try:
            url = munge_url(url_or_filename, input_options)
            logup("Trying to open remote resource", {"url": url_or_filename})
            status_code, response_body, response_headers = _pycurl_request(
                url,
                method="GET",
                headers=input_options.http_headers,
                verify_ssl=input_options.verify_ssl,
                timeout=input_options.timeout
            )
            logup("Response status", {"url": url_or_filename, "status": status_code})
            if status_code == 403:  # CKAN sends "403 Forbidden" for a private file
                raise HXLAuthorizationException("Access not authorized", url=url)
            elif status_code >= 400:
                raise IOError(f"HTTP error {status_code} for URL: {url}")
        except Exception as e:
            logger.error("Cannot open URL %s (%s)", url_or_filename, str(e))
            raise e

        # Extract content type and encoding from headers
        content_type = None
        for line in response_headers.splitlines():
            if line.lower().startswith("content-type:"):
                content_type = line.split(":", 1)[1].strip()
                break

        if content_type:
            result = re.match(r'^(\S+)\s*;\s*charset=(\S+)$', content_type)
            if result:
                mime_type = result.group(1).lower()
                encoding = result.group(2).lower()
            else:
                mime_type = content_type.lower()

        content_length = len(response_body)

        return (BytesIO(response_body.encode('utf-8')), mime_type, file_ext, encoding, content_length, fileno,)

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
