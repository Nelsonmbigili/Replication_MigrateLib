import requests_futures
from requests_futures.sessions import FuturesSession

# Initialize a FuturesSession for asynchronous requests
session = FuturesSession()

# Replace all instances of requests.get and requests.head with session.get and session.head
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
            response = session.get(
                url,
                stream=True,
                verify=input_options.verify_ssl,
                timeout=input_options.timeout,
                headers=input_options.http_headers
            ).result()  # Retrieve the actual response
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


def munge_url(url, input_options):
    """Munge a URL to get at underlying data for well-known types.

    For example, if it's an HDX dataset, figure out the download
    link for the first resource. If it's a Kobo survey, create an
    export and get the download link (given an appropriate
    authorization header).

    This function ignores InputOptions.scan_ckan_resources -- the
    scanning happens in hxl.input.data(). So it's not exactly
    equivalent to the URL that you would get via data().

    Args:
        url (str): the original URL to munge
        input_options (InputOptions): options for reading a dataset.

    Returns:
        str: the actual direct-download URL

    Raises:
        hxl.input.HXLAuthorizationException: if the source requires some kind of authorization

    """

    #
    # Stage 1: unpack indirect links (requires extra HTTP requests)
    #

    # Is it a CKAN resource? (Assumes the v.3 API for now)
    result = re.match(CKAN_URL, url)
    if result:
        logup("Using CKAN API to dereference", {"url": url})
        url = _get_ckan_urls(result.group(1), result.group(2), result.group(3), input_options)[0]

    # Is it a Google Drive "open" URL?
    result = re.match(GOOGLE_DRIVE_URL, url)
    if result:
        logup("HEAD request for Google Drive URL", {"url": url})
        response = session.head(url).result()  # Retrieve the actual response
        if response.is_redirect:
            new_url = response.headers['Location']
            logup("Google Drive redirect", {"url": url, "redirect": new_url})
            logger.info("Following Google Drive redirect to %s", new_url)
            url = new_url

    # Is it a Kobo survey?
    result = re.match(KOBO_URL, url)
    if result:
        logup("Using KOBO API to dereference", {"url": url})
        max_export_age_seconds = 4 * 60 * 60 # 4 hours; TODO: make configurable
        url = _get_kobo_url(result.group(1), url, input_options, max_export_age_seconds)

    #
    # Stage 2: rewrite URLs to get direct-download links
    #

    # Is it a Google *Sheet*?
    result = re.match(GOOGLE_SHEETS_URL, url)
    if result and not re.search(r'/pub', url):
        if result.group(2):
            new_url = 'https://docs.google.com/spreadsheets/d/{0}/export?format=csv&gid={1}'.format(result.group(1), result.group(2))
            logup("Rewriting Google Sheets URL", {"url": url, "rewrite_url": new_url})
            url = new_url
        else:
            new_url = 'https://docs.google.com/spreadsheets/d/{0}/export?format=csv'.format(result.group(1))
            logup("Rewriting Google Sheets URL", {"url": url, "rewrite_url": new_url})
            url = new_url
        return url

    # Is it a Google Drive *file*?
    result = re.match(GOOGLE_FILE_URL, url)
    if not result:
        result = re.match(GOOGLE_SHEETS_XLSX_URL, url)
    if result and not re.search(r'/pub', url):
        url = 'https://drive.google.com/uc?export=download&id={}'.format(result.group(1))
        logger.info("Google Drive direct file download URL: %s", url)
        return url

    # Is it a Dropbox URL?
    result = re.match(DROPBOX_URL, url)
    if result:
        url = 'https://www.dropbox.com/s/{0}/{1}?dl=1'.format(result.group(1), result.group(2))
        logger.info("Dropbox direct-download URL: %s", url)
        return url

    # Is it a HXL Proxy direct-download link?
    if re.match(HXL_PROXY_DOWNLOAD_URL, url):
        logger.info("HXL Proxy direct-download URL: %s", url)
        return url

    # Is it a HXL Proxy saved recipe?
    result = re.match(HXL_PROXY_SAVED_URL, url)
    if result:
        url = '{0}/data/{1}.csv{2}'.format(result.group(1), result.group(2), result.group(3))
        logger.info("HXL Proxy saved-recipe URL: %s", url)
        return url

    # Is it a HXL Proxy args-based recipe?
    result = re.match(HXL_PROXY_ARGS_URL, url)
    if result:
        url = '{0}/data.csv?{1}'.format(result.group(1), result.group(2))
        logger.info("HXL Proxy direct-download URL: %s", url)
        return url

    # No changes
    return url
