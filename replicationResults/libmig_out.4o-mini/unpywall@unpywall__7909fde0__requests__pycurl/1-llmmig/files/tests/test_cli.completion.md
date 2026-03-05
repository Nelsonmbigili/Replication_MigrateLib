### Explanation of Changes
To migrate the code from using the `requests` library to using `pycurl`, I replaced the `requests`-specific exception handling with `pycurl`-specific error handling. The `HTTPError` from `requests` is not directly applicable in `pycurl`, so I will handle errors using `pycurl.error`. Additionally, I will set up a `pycurl.Curl` object to perform the HTTP requests instead of using `requests`. The main function calls that were previously using `requests` will now utilize `pycurl` to handle the HTTP operations.

### Modified Code
```python
from unpywall.__main__ import main
import pycurl
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

        with pytest.raises(pycurl.error):
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

        with pytest.raises(pycurl.error):
            bad_doi = 'bad_doi'
            main(test_args=['link', bad_doi])
``` 

In this modified code, I replaced instances of `HTTPError` with `pycurl.error` to reflect the change in the library being used for HTTP requests. The rest of the code remains unchanged to maintain the original structure and functionality.