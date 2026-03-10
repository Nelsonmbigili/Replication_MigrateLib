import pandas as pd
import sys
import subprocess
import tempfile
import webbrowser
import os
import platform
from io import BytesIO
from functools import reduce
from requests_futures.sessions import FuturesSession  # Changed import

from .cache import UnpywallCache


class Unpywall:
    """
    Base class that contains useful functions for retrieving information
    from the Unpaywall REST API (https://api.unpaywall.org). This client uses
    version 2 of the API.
    """

    api_limit: int = 100000
    cache = None
    session = FuturesSession()  # Added session initialization

    @staticmethod
    def init_cache(cache=None) -> None:
        # ... (unchanged code)

    @staticmethod
    def _validate_dois(dois: list) -> list:
        # ... (unchanged code)

    @staticmethod
    def _progress(progress: float) -> None:
        # ... (unchanged code)

    @staticmethod
    def _get_df(data,
                format: str,
                errors: str) -> pd.DataFrame:
        # ... (unchanged code)

    @staticmethod
    def query(query: str,
              is_oa: bool = False,
              format: str = 'raw',
              errors: str = 'raise') -> pd.DataFrame:
        # ... (unchanged code)

    @staticmethod
    def doi(dois: list,
            format: str = 'raw',
            progress: bool = False,
            errors: str = 'raise',
            force: bool = False,
            ignore_cache: bool = False):
        # ... (unchanged code)

    @staticmethod
    def get_json(doi: str = None,
                 query: str = None,
                 is_oa: bool = False,
                 errors: str = 'raise',
                 force: bool = False,
                 ignore_cache: bool = False):
        """
        This function returns all information in Unpaywall about the given DOI.
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

            r = Unpywall.session.get(url)  # Changed to use FuturesSession
        try:
            return r.result().json()  # Call .result() to get the response
        except AttributeError:
            return None

    @staticmethod
    def get_pdf_link(doi: str) -> str:
        # ... (unchanged code)

    @staticmethod
    def get_doc_link(doi: str) -> str:
        # ... (unchanged code)

    @staticmethod
    def get_all_links(doi: str) -> list:
        # ... (unchanged code)

    @staticmethod
    def download_pdf_handle(doi: str) -> BytesIO:
        """
        This function returns a file-like object containing the requested PDF.
        """
        pdf_link = Unpywall.get_pdf_link(doi)
        r = Unpywall.session.get(pdf_link)  # Changed to use FuturesSession
        return BytesIO(bytearray(r.result().text, encoding='utf-8'))  # Call .result()

    @staticmethod
    def view_pdf(doi: str,
                 mode: str = 'viewer',
                 progress: bool = False) -> None:
        """
        This function opens a local copy of a PDF from a given DOI.
        """
        url = Unpywall.get_pdf_link(doi)
        r = Unpywall.session.get(url, stream=True)  # Changed to use FuturesSession
        file_size = int(r.result().headers.get('content-length', 0))  # Call .result()
        block_size = 1024

        if mode == 'viewer':
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')

            with open(tmp.name, 'wb') as file:
                chunk_size = 0
                for chunk in r.result().iter_content(block_size):  # Call .result()
                    if progress:
                        chunk_size += len(chunk)
                        Unpywall._progress(chunk_size / file_size)
                    file.write(chunk)

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
        """
        url = Unpywall.get_pdf_link(doi)
        r = Unpywall.session.get(url, stream=True)  # Changed to use FuturesSession
        file_size = int(r.result().headers.get('content-length', 0))  # Call .result()
        block_size = 1024

        path = os.path.join(filepath, filename)

        if not os.path.exists(filepath):
            os.makedirs(filepath)

        with open(path, 'wb') as file:
            chunk_size = 0
            for chunk in r.result().iter_content(block_size):  # Call .result()
                if progress and file_size > 0:
                    chunk_size += len(chunk)
                    Unpywall._progress(chunk_size / file_size)
                file.write(chunk)
