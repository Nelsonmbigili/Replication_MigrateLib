import pycurl
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
    def _validate_dois(dois: list) -> list:
        """
        This method accepts a list of DOIs and returns a cleaned version of it.
        Raises an error if the desired input is not given.

        Parameters
        ----------
        dois : list
            A list of DOIs. Each DOI should be represented as a string.

        Returns
        -------
        list
            A list of DOIs.

        Raises
        ------
        ValueError
            If the input is empty or not of type list.
        """
        if dois is None or len(dois) == 0:
            raise ValueError('No DOI specified')

        if not isinstance(dois, list):
            raise ValueError('The input format must be of type list')

        if len(dois) > Unpywall.api_limit:
            raise ValueError('Unpaywall only allows to 100,000 calls per day')

        for doi in dois:
            doi.replace(' ', '')

        return dois

    @staticmethod
    def _progress(progress: float) -> None:
        """
        This method prints out the current progress status of an API call.

        Parameters
        ----------
        progress : float
            Current status of the progress. Value between 0 and 1.
        """

        bar_len = 50
        block = int(round(bar_len * progress))

        text = '|{0}| {1}%'.format('=' * block + ' ' * (bar_len - block),
                                   int(progress * 100))

        print(text, end='\r', flush=False, file=sys.stdout)

        if progress == 1:
            print('\n', file=sys.stdout)

    @staticmethod
    def _get_df(data,
                format: str,
                errors: str) -> pd.DataFrame:
        """
        Parses information from the Unpaywall API service and returns it as
        a pandas DataFrame.

        Parameters
        ----------
        data: JSON object
            A JSON data structure containing all information
            returned by Unpaywall about a given input.
        format: str
            The format of the DataFrame.
        errors : str
            Either 'raise' or 'ignore'. If the parameter errors is set to
            'ignore' than errors will not raise an exception.

        Returns
        -------
        DataFrame
            A pandas DataFrame that contains information from the Unpaywall
            API service.

        Raises
        ------
        ValueError
            If the parameter errors contains a faulty value.
        """

        if format not in ['raw', 'extended']:
            raise ValueError('The argument format only accepts the'
                             ' values "raw" and "extended"')

        if format == 'extended':

            doi_object = pd.json_normalize(data=data,
                                           max_level=1,
                                           errors=errors)

            doi_object.drop(columns=['oa_locations',
                                     'z_authors'],
                            errors=errors,
                            inplace=True)

            oa_locations = pd.json_normalize(data=data,
                                             errors=errors,
                                             meta='doi',
                                             record_path=['oa_locations'])

            z_authors = pd.json_normalize(data=data,
                                          errors=errors,
                                          meta='doi',
                                          record_path=['z_authors'])

            dfs = [doi_object, oa_locations, z_authors]
            df = reduce(lambda left, right: pd.merge(left,
                                                     right,
                                                     how='outer',
                                                     on='doi'), dfs)

        else:
            df = pd.json_normalize(data=data, max_level=1, errors=errors)

        return df

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

            buffer = BytesIO()
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEDATA, buffer)
            curl.perform()
            curl.close()

            response_data = buffer.getvalue().decode('utf-8')
            try:
                return json.loads(response_data)
            except json.JSONDecodeError:
                return None
