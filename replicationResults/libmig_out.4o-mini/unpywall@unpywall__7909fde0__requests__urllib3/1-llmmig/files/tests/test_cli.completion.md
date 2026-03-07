### Explanation of Changes
To migrate the code from using the `requests` library to using `urllib3`, the following changes were made:

1. **Importing `urllib3`**: Instead of importing `HTTPError` from `requests.exceptions`, we will use `urllib3.exceptions.HTTPError`.
2. **Error Handling**: The way errors are raised and handled may differ slightly between the two libraries. We will ensure that the `HTTPError` is raised correctly when using `urllib3`.

The rest of the code remains unchanged to adhere to the guidelines provided.

### Modified Code
```python
from unpywall.__main__ import main
from urllib3.exceptions import HTTPError
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