### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the following changes were made:
1. **Import Changes**: The `requests` library is replaced with `requests_futures`. Specifically, `requests_futures` provides an `HTTPError` exception in the same way as `requests`, so no changes are needed for exception handling.
2. **No Additional Changes**: Since the provided code does not directly use any synchronous `requests` methods (e.g., `requests.get`, `requests.post`), and only references `HTTPError`, no further modifications are required. The `requests_futures` library is compatible with the existing exception handling.

### Modified Code:
```python
from unpywall.__main__ import main
from requests_futures.sessions import FuturesSession
from requests_futures.exceptions import HTTPError
import pytest
import os

os.environ['UNPAYWALL_EMAIL'] = 'nick.haupka@gmail.com'


class TestUnpywallCli:

    def test_main(self):

        with pytest.raises(SystemExit) as pytest_raise_system_exit:
            assert main(test_args=['-h'])

            assert pytest_raise_system_exit.value.code == 0

        with pytest.raises(SystemExit) as pytest_raise_system_exit:
            main(test_args=['this is a bad argument'])
            assert pytest_raise_system_exit.value.code == 1

    def test_view(self):
        with pytest.raises(SystemExit) as pytest_raise_system_exit:
            main(test_args=['view'])

            assert pytest_raise_system_exit.value.code == 2

        with pytest.raises(HTTPError):
            bad_doi = 'bad_doi'
            main(test_args=['view', bad_doi])

    def test_download(self, capfd):

        bad_doi = 'bad_doi'
        main(test_args=['download', bad_doi])
        captured = capfd.readouterr()
        assert captured.out == 'Could not download file.\n'

        with pytest.raises(SystemExit) as pytest_raise_system_exit:
            main(test_args=['download'])

            assert pytest_raise_system_exit.value.code == 2

    def test_link(self):
        with pytest.raises(SystemExit) as pytest_raise_system_exit:
            main(test_args=['link'])

            assert pytest_raise_system_exit.value.code == 2

        with pytest.raises(HTTPError):
            bad_doi = 'bad_doi'
            main(test_args=['link', bad_doi])
```

### Notes:
- The `requests_futures` library is designed for asynchronous requests, but since the provided code does not directly make HTTP requests, no asynchronous functionality is utilized here.
- The `HTTPError` exception is still valid and works the same way in `requests_futures` as it does in `requests`.