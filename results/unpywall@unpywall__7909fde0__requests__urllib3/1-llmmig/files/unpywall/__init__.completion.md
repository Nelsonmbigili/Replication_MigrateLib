### Explanation of Changes:
To migrate the code from the `requests` library to `urllib3`, the following changes were made:
1. **Import Replacement**: Removed the `requests` import and replaced it with `urllib3`.
2. **HTTP Connection Management**: Created an `urllib3.PoolManager` instance to handle HTTP requests.
3. **GET Requests**: Replaced `requests.get()` with `urllib3.PoolManager.request()` for making GET requests.
4. **Streaming and Content Handling**: Replaced `r.iter_content()` with `response.read()` and handled chunked reading manually.
5. **Response JSON Parsing**: Replaced `r.json()` with `json.loads(response.data.decode('utf-8'))` to parse JSON responses.
6. **Headers and Content-Length**: Accessed headers using `response.headers` instead of `r.headers`.
7. **Error Handling**: Ensured compatibility with `urllib3`'s response handling and exceptions.

Below is the modified code:

---

### Modified Code:
```python
import urllib3
import json
import pandas as pd
import sys
import subprocess
import tempfile
import webbrowser
import os
import platform
from io import BytesIO
from functools import reduce

from .cache import UnpywallCache


class Unpywall:
    """
    Base class that contains useful functions for retrieving information
    from the Unpaywall REST API (https://api.unpaywall.org). This client uses
    version 2 of the API.
    """

    api_limit: int = 100000
    cache = None
    http = urllib3.PoolManager()  # Initialize a PoolManager for HTTP requests

    @staticmethod
    def init_cache(cache=None) -> None:
        """
        This method initializes a cache that is used to store records
        from the Unpaywall database.

        Parameters
        ----------
        cache: UnpywallCache
            A custom cache to be used instead of the standard cache.

        Raises
        ------
        AttributeError
            If the custom cache is not of type UnpywallCache.
        """
        if cache:
            if not isinstance(cache, UnpywallCache):
                raise AttributeError(
                 'Cache is not of type {0}'.format(UnpywallCache))
            else:
                Unpywall.cache = cache
        else:
            Unpywall.cache = UnpywallCache()

    @staticmethod
    def get_json(doi: str = None,
                 query: str = None,
                 is_oa: bool = False,
                 errors: str = 'raise',
                 force: bool = False,
                 ignore_cache: bool = False):
        """
        This function returns all information in Unpaywall about the given DOI.

        Parameters
        ----------
        doi : str
            The DOI of the requested paper.
        query : str
            The text to search for.
        is_oa : bool
            A boolean value indicating whether the returned records should be
            Open Access or not.
        errors : str
            Either 'raise' or 'ignore'. If the parameter errors is set to
            'ignore' than errors will not raise an exception.
        force : bool
            Whether to force the cache to retrieve a new entry.
        ignore_cache : bool
            Whether to use or ignore the cache.

        Returns
        -------
        JSON object
            A JSON data structure containing all information
            returned by Unpaywall about the given DOI.

        Raises
        ------
        AttributeError
            If the Unpaywall API did not respond with json.
        """
        if not Unpywall.cache:
            Unpywall.init_cache()

        if doi:
            r = Unpywall.cache.get(doi,
                                   errors=errors,
                                   force=force,
                                   ignore_cache=ignore_cache)
        if query:
            if type(is_oa) != bool:
                raise ValueError('The argument is_oa only accepts the'
                                 ' values "True" and "False"')
            # TODO: implementation -> cache.py
            from .utils import UnpywallURL

            url = UnpywallURL(query=query, is_oa=is_oa).query_url

            response = Unpywall.http.request('GET', url)
            if response.status != 200:
                return None
            r = json.loads(response.data.decode('utf-8'))
        try:
            return r
        except AttributeError:
            return None

    @staticmethod
    def download_pdf_handle(doi: str) -> BytesIO:
        """
        This function returns a file-like object containing the requested PDF.

        Parameters
        ----------
        doi : str
            The DOI of the requested paper.

        Returns
        -------
        BytesIO
            The handle of the PDF file.
        """
        pdf_link = Unpywall.get_pdf_link(doi)
        response = Unpywall.http.request('GET', pdf_link)
        return BytesIO(response.data)

    @staticmethod
    def view_pdf(doi: str,
                 mode: str = 'viewer',
                 progress: bool = False) -> None:
        """
        This function opens a local copy of a PDF from a given DOI.

        Parameters
        ----------
        doi : str
            The DOI of the requested paper.
        mode : str
            The mode for viewing a PDF.
        progress : bool
            Whether the progress of the API call should be printed out or not.
        """

        url = Unpywall.get_pdf_link(doi)
        response = Unpywall.http.request('GET', url, preload_content=False)
        file_size = int(response.headers.get('content-length', 0))
        block_size = 1024

        if mode == 'viewer':

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')

            with open(tmp.name, 'wb') as file:
                chunk_size = 0
                while True:
                    data = response.read(block_size)
                    if not data:
                        break
                    if progress:
                        chunk_size += len(data)
                        Unpywall._progress(chunk_size / file_size)
                    file.write(data)

                # macOS
                if platform.system() == 'Darwin':
                    subprocess.run(['open', tmp.name], check=True)
                # Windows
                elif platform.system() == 'Windows':
                    os.startfile(tmp.name)
                # Linux
                else:
                    subprocess.run(['xdg-open', tmp.name], check=True)

        else:
            webbrowser.open_new(url)

    @staticmethod
    def download_pdf_file(doi: str,
                          filename: str,
                          filepath: str = '.',
                          progress: bool = False) -> None:
        """
        This function downloads a PDF from a given DOI.

        Parameters
        ----------
        doi : str
            The DOI of the requested paper.
        filename : str
            The filename for the PDF.
        filepath : str
            The path to store the downloaded PDF.
        progress : bool
            Whether the progress of the API call should be printed out or not.
        """

        url = Unpywall.get_pdf_link(doi)
        response = Unpywall.http.request('GET', url, preload_content=False)
        file_size = int(response.headers.get('content-length', 0))
        block_size = 1024

        path = os.path.join(filepath, filename)

        if not os.path.exists(filepath):
            os.makedirs(filepath)

        with open(path, 'wb') as file:
            chunk_size = 0
            while True:
                data = response.read(block_size)
                if not data:
                    break
                if progress and file_size > 0:
                    chunk_size += len(data)
                    Unpywall._progress(chunk_size / file_size)
                file.write(data)
```

---

### Key Notes:
- The `urllib3.PoolManager` is used for managing HTTP connections.
- JSON responses are parsed using `json.loads()` after decoding the response data.
- Streaming and progress tracking are handled manually using `response.read()` in chunks.
- The `preload_content=False` parameter is used for streaming large files.