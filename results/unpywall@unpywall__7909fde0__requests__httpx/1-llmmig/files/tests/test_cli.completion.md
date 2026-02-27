### Explanation of Changes
To migrate the code from using the `requests` library to `httpx`, the following changes were made:
1. **Exception Handling**: The `requests.exceptions.HTTPError` was replaced with `httpx.HTTPStatusError`, as `httpx` uses this exception for HTTP-related errors.
2. **Imports**: The `requests.exceptions` import was replaced with `httpx`.

No other changes were made, as the code does not directly use `requests` or `httpx` for making HTTP requests. The changes are limited to exception handling and imports.

---

### Modified Code
```python
from unpywall.__main__ import main
from httpx import HTTPStatusError
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

        with pytest.raises(HTTPStatusError):
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

        with pytest.raises(HTTPStatusError):
            bad_doi = 'bad_doi'
            main(test_args=['link', bad_doi])
```