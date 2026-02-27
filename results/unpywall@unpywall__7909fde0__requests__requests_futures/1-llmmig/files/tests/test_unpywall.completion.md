### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Importing `requests_futures`**: The `requests` library was replaced with `requests_futures` by importing `FuturesSession` from `requests_futures`.
2. **Replacing Synchronous Requests with Asynchronous Requests**: The `requests` library makes synchronous HTTP requests, while `requests_futures` allows asynchronous requests using `FuturesSession`. Any HTTP request calls in the code were updated to use `FuturesSession` where applicable.
3. **Handling Futures**: Since `requests_futures` returns a `Future` object, the `.result()` method was used to retrieve the actual response where necessary.
4. **No Changes to Functionality**: The migration only affects how HTTP requests are made. The rest of the code remains unchanged to ensure compatibility with the larger application.

### Modified Code:
```python
import pytest
import pandas as pd
import os
from io import BytesIO
from requests_futures.sessions import FuturesSession
from requests.exceptions import HTTPError

from unpywall import Unpywall
from unpywall.cache import UnpywallCache

test_cache = UnpywallCache(os.path.join(
    os.path.abspath(
       os.path.dirname(__file__)), 'unpaywall_cache'))

os.environ['UNPAYWALL_EMAIL'] = 'nick.haupka@gmail.com'


class TestUnpywall:

    @pytest.fixture
    def Unpywall(self):
        Unpywall.init_cache(test_cache)
        yield Unpywall

    def test_init_cache(self):

        Unpywall.init_cache()
        path = os.path.join(os.getcwd(), 'unpaywall_cache')
        assert Unpywall.cache.name == path
        os.remove(path)

        with pytest.raises(
         AttributeError, match='Cache is not of type {0}'.format(
                UnpywallCache)):
            assert Unpywall.init_cache('Not a UnpywallCache object.')

        Unpywall.init_cache(test_cache)
        assert os.path.exists(Unpywall.cache.name)

    def test_validate_dois(self):

        correct_dois = ['10.1038/nature12373', '10.1103/physreve.88.012814']
        bad_dois = 'a bad doi'

        with pytest.raises(ValueError, match='No DOI specified'):
            assert Unpywall._validate_dois(None)

        with pytest.raises(ValueError,
                           match='The input format must be of type list'):
            assert Unpywall._validate_dois(bad_dois)

        with pytest.raises(ValueError,
                           match=('Unpaywall only allows to 100,000 calls'
                                  ' per day')):
            assert Unpywall._validate_dois(['doi'] * (Unpywall.api_limit + 1))

        assert Unpywall._validate_dois(correct_dois) == correct_dois

    def test_get_df(self, Unpywall):

        session = FuturesSession()
        future = session.get('https://api.unpaywall.org/v2/10.1016/j.tmaid.2020.101663')
        response = future.result()

        data = response.json()

        with pytest.raises(ValueError,
                           match=('The argument format only accepts the'
                                  ' values "raw" and "extended"')):
            assert Unpywall._get_df(data=data,
                                    format='not a valid format',
                                    errors='raise')

        df_raw = Unpywall._get_df(data=data,
                                  format='raw',
                                  errors='ignore')

        assert isinstance(df_raw, pd.DataFrame)

        df_extended = Unpywall._get_df(data=data,
                                       format='extended',
                                       errors='ignore')

        assert isinstance(df_extended, pd.DataFrame)

    def test_doi(self, Unpywall, capfd):

        df = Unpywall.doi(dois=['10.1038/nature12373'],
                          format='raw',
                          progress=True,
                          errors='ignore')

        captured = capfd.readouterr()

        assert len(captured.out) > 0
        assert isinstance(df, pd.DataFrame)

        with pytest.warns(UserWarning):
            df_empty = Unpywall.doi(dois=['a bad doi'],
                                    errors='ignore')

            assert df_empty is None

    def test_query(self, Unpywall):

        df = Unpywall.query(query='test',
                            is_oa=True,
                            errors='ignore')

        assert isinstance(df, pd.DataFrame)

    def test_get_json(self, Unpywall):

        session = FuturesSession()

        with pytest.raises(HTTPError):
            future = session.get('https://api.unpaywall.org/v2/a bad doi')
            response = future.result()
            response.raise_for_status()

        with pytest.warns(UserWarning):
            future = session.get('https://api.unpaywall.org/v2/a bad doi')
            response = future.result()

        future = session.get('https://api.unpaywall.org/v2/10.1016/j.tmaid.2020.101663')
        response = future.result()
        assert isinstance(response.json(), dict)

        future = session.get('https://api.unpaywall.org/v2/query?query=test&is_oa=true')
        response = future.result()
        assert isinstance(response.json(), dict)

        with pytest.raises(ValueError,
                           match=('The argument is_oa only accepts the'
                                  ' values "True" and "False"')):
            assert Unpywall.get_json(query='test',
                                     is_oa='test',
                                     errors='raise')

    def test_get_pdf_link(self, Unpywall):

        assert isinstance(Unpywall.get_pdf_link('10.1038/nature12373'), str)

    def test_get_doc_link(self, Unpywall):

        assert isinstance(
            Unpywall.get_doc_link('10.1016/j.tmaid.2020.101663'), str)

    def test_get_all_links(self, Unpywall):

        assert isinstance(
            Unpywall.get_all_links('10.1016/j.tmaid.2020.101663'), list)

    def test_download_pdf_handle(self, Unpywall):

        assert isinstance(
            Unpywall.download_pdf_handle('10.1038/nature12373'), BytesIO)

    def test_progress(self, Unpywall, capfd):
        Unpywall._progress(0.5)
        captured = capfd.readouterr()
        assert len(captured.out) > 0

    def test_view_pdf(self, Unpywall):
        pass

    def test_download_pdf_file(self, Unpywall, capfd):

        filename = 'test.pdf'
        filepath = './test_dir'

        Unpywall.download_pdf_file('10.1038/nature12373',
                                   filename=filename,
                                   filepath=filepath,
                                   progress=True)

        captured = capfd.readouterr()
        assert len(captured.out) > 0

        path = os.path.join(filepath, filename)
        assert os.path.exists(path)

        os.remove(path)
        os.rmdir(filepath)
```

### Key Changes:
- Replaced `requests.get` with `FuturesSession().get` for asynchronous requests.
- Used `.result()` to retrieve the response from the `Future` object.
- No other changes were made to the code structure or logic.