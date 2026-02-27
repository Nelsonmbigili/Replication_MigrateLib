import treq
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
    async def query(query: str,
                    is_oa: bool = False,
                    format: str = 'raw',
                    errors: str = 'raise') -> pd.DataFrame:
        data = await Unpywall.get_json(query=query, is_oa=is_oa, errors=errors)

        df = pd.DataFrame()

        for obj in data['results']:
            df2 = Unpywall._get_df(data=obj['response'],
                                   format=format,
                                   errors=errors)
            df = pd.concat([df, df2], ignore_index=True)

        if df.empty:
            return None

        return df

    @staticmethod
    async def doi(dois: list,
                  format: str = 'raw',
                  progress: bool = False,
                  errors: str = 'raise',
                  force: bool = False,
                  ignore_cache: bool = False):
        dois = Unpywall._validate_dois(dois)

        df = pd.DataFrame()

        for n, doi in enumerate(dois, start=1):

            if progress:
                Unpywall._progress(n / len(dois))

            data = await Unpywall.get_json(doi,
                                           errors=errors,
                                           force=force,
                                           ignore_cache=ignore_cache)

            if not bool(data):
                continue

            df2 = Unpywall._get_df(data=data,
                                   format=format,
                                   errors=errors)
            df = pd.concat([df, df2], ignore_index=True)

        if df.empty:
            return None

        return df

    @staticmethod
    async def get_json(doi: str = None,
                       query: str = None,
                       is_oa: bool = False,
                       errors: str = 'raise',
                       force: bool = False,
                       ignore_cache: bool = False):
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
            from .utils import UnpywallURL

            url = UnpywallURL(query=query, is_oa=is_oa).query_url

            r = await treq.get(url)
        try:
            return await r.json()
        except AttributeError:
            return None

    @staticmethod
    async def download_pdf_handle(doi: str) -> BytesIO:
        pdf_link = await Unpywall.get_pdf_link(doi)
        r = await treq.get(pdf_link)
        content = await r.content()
        return BytesIO(content)

    @staticmethod
    async def view_pdf(doi: str,
                       mode: str = 'viewer',
                       progress: bool = False) -> None:
        url = await Unpywall.get_pdf_link(doi)
        r = await treq.get(url, unbuffered=True)
        file_size = int(r.headers.get('content-length', 0))
        block_size = 1024

        if mode == 'viewer':
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')

            with open(tmp.name, 'wb') as file:
                chunk_size = 0
                async for chunk in r.iter_content(block_size):
                    if progress:
                        chunk_size += len(chunk)
                        Unpywall._progress(chunk_size / file_size)
                    file.write(chunk)

                if platform.system() == 'Darwin':
                    subprocess.run(['open', tmp.name], check=True)
                elif platform.system() == 'Windows':
                    os.startfile(tmp.name)
                else:
                    subprocess.run(['xdg-open', tmp.name], check=True)
        else:
            webbrowser.open_new(url)

    @staticmethod
    async def download_pdf_file(doi: str,
                                 filename: str,
                                 filepath: str = '.',
                                 progress: bool = False) -> None:
        url = await Unpywall.get_pdf_link(doi)
        r = await treq.get(url, unbuffered=True)
        file_size = int(r.headers.get('content-length', 0))
        block_size = 1024

        path = os.path.join(filepath, filename)

        if not os.path.exists(filepath):
            os.makedirs(filepath)

        with open(path, 'wb') as file:
            chunk_size = 0
            async for chunk in r.iter_content(block_size):
                if progress and file_size > 0:
                    chunk_size += len(chunk)
                    Unpywall._progress(chunk_size / file_size)
                file.write(chunk)
