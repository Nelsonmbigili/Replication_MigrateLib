import pycurl
import pickle
from copy import deepcopy
import os
import time
import warnings
from io import BytesIO


class UnpywallCache:
    """
    This class stores query results from Unpaywall.
    It has a configurable timeout that can also be set to never expire.

    Attributes
    ----------
    name : string
        The filename used to save and load the cache by default.
    content : dict
        A dictionary mapping dois to response-like objects.
    access_times : dict
        A dictionary mapping dois to the datetime when each was last updated.

    """

    def __init__(self, name: str = None, timeout=None) -> None:
        """
        Create a cache object.

        Parameters
        ----------
        timeout : float or int
            The number of seconds that each entry should last.
        name : str
            The filename used to save and load the cache by default.
        """
        if not name:
            self.name = os.path.join(os.getcwd(), 'unpaywall_cache')
        else:
            self.name = name
        try:
            self.load(self.name)
        except FileNotFoundError:
            # print('No cache found. A new cache was initialized.')
            self.reset_cache()
        self.timeout = timeout

    def reset_cache(self) -> None:
        """
        Set the cache to a blank state.
        """
        self.content = {}
        self.access_times = {}
        self.save()

    def delete(self, doi: str) -> None:
        """
        Remove an individual doi from the cache.

        Parameters
        ----------
        doi : str
            The DOI to be removed from the cache.
        """
        if doi in self.access_times:
            del self.access_times[doi]
        if doi in self.content:
            del self.content[doi]
        self.save()

    def timed_out(self, doi: str) -> bool:
        """
        Return whether the record for the given doi has expired.

        Parameters
        ----------
        doi : str
            The DOI to be removed from the cache.

        Returns
        -------
        is_timed_out : bool
            Whether the given entry has timed out.
        """
        if not self.timeout:
            is_timed_out = False
        else:
            is_timed_out = time.time() > self.access_times[doi] + self.timeout
        return is_timed_out

    def get(self, doi: str, errors: str = 'raise',
            force: bool = False, ignore_cache: bool = False):
        """
        Return the record for the given doi.

        Parameters
        ----------
        doi : str
            The DOI to be retrieved.
        errors : str
            Whether to ignore or raise errors.
        force : bool
            Whether to force the cache to retrieve a new entry.
        ignore_cache : bool
            Whether to use or ignore the cache.

        Returns
        -------
        record : response-like object
            The response from Unpaywall.
        """
        record = None

        if not ignore_cache:
            if (doi not in self.content) or self.timed_out(doi) or force:
                downloaded = self.download(doi, errors)
                if downloaded:
                    self.access_times[doi] = time.time()
                    self.content[doi] = downloaded
                    self.save()
                    record = downloaded
            else:
                record = deepcopy(self.content[doi])
        else:
            record = self.download(doi, errors)
        return record

    def save(self, name=None) -> None:
        """
        Save the current cache contents to a file.

        Parameters
        ----------
        name : str or None
            The filename that the cache will be saved to.
            If None, self.name will be used.
        """
        if not name:
            name = self.name
        with open(name, 'wb') as handle:
            pickle.dump({'content': self.content,
                         'access_times': self.access_times},
                        handle)

    def load(self, name=None) -> None:
        """
        Load the cache from a file.

        Parameters
        ----------
        name : str or None
            The filename that the cache will be loaded from.
            If None, self.name will be used.
        """
        if not name:
            name = self.name
        with open(name, 'rb') as handle:
            data = pickle.load(handle)
        self.content = data['content']
        self.access_times = data['access_times']

    def download(self, doi: str, errors: str):
        """
        Retrieve a record from Unpaywall.

        Parameters
        ----------
        doi : str
            The DOI to be retrieved.
        errors : str
            Whether to ignore or raise errors.

        Returns
        -------
        response-like object
            A custom object containing status code, headers, and body.
        """
        from .utils import UnpywallURL

        mandatory_wait_time = int(os.environ.get('MANDATORY_WAIT_TIME', 1))
        time.sleep(mandatory_wait_time)
        url = UnpywallURL(doi=doi).doi_url

        buffer = BytesIO()
        headers = {}

        def header_function(header_line):
            # Parse header lines into a dictionary
            parts = header_line.decode('iso-8859-1').strip().split(':', 1)
            if len(parts) == 2:
                headers[parts[0].strip()] = parts[1].strip()

        try:
            curl = pycurl.Curl()
            curl.setopt(curl.URL, url)
            curl.setopt(curl.WRITEFUNCTION, buffer.write)
            curl.setopt(curl.HEADERFUNCTION, header_function)
            curl.perform()

            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            curl.close()

            # Create a response-like object
            class Response:
                def __init__(self, status_code, headers, body):
                    self.status_code = status_code
                    self.headers = headers
                    self.body = body

                def raise_for_status(self):
                    if not (200 <= self.status_code < 300):
                        raise Exception(f"HTTP Error: {self.status_code}")

            response = Response(status_code, headers, buffer.getvalue())
            response.raise_for_status()
            return response

        except pycurl.error as e:
            if errors == 'raise':
                raise Exception(f"pycurl error: {e}")
            warnings.warn(f"Could not download doi: {doi} - {e}")
            return None
