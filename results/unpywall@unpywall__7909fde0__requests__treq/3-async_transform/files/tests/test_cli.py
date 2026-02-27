from unpywall.__main__ import main
from twisted.web.client import ResponseFailed
import pytest
import os

os.environ['UNPAYWALL_EMAIL'] = 'nick.haupka@gmail.com'


class TestUnpywallCli:

    @pytest.mark.asyncio
    async def test_main(self):

        with pytest.raises(SystemExit) as pytest_raise_system_exit:
            assert main(test_args=['-h'])

            assert pytest_raise_system_exit.value.code == 0

        with pytest.raises(SystemExit) as pytest_raise_system_exit:
            main(test_args=['this is a bad argument'])
            assert pytest_raise_system_exit.value.code == 1

    @pytest.mark.asyncio
    async def test_view(self):
        with pytest.raises(SystemExit) as pytest_raise_system_exit:
            main(test_args=['view'])

            assert pytest_raise_system_exit.value.code == 2

        with pytest.raises(ResponseFailed):
            bad_doi = 'bad_doi'
            main(test_args=['view', bad_doi])

    @pytest.mark.asyncio
    async def test_download(self, capfd):

        bad_doi = 'bad_doi'
        main(test_args=['download', bad_doi])
        captured = capfd.readouterr()
        assert captured.out == 'Could not download file.\n'

        with pytest.raises(SystemExit) as pytest_raise_system_exit:
            main(test_args=['download'])

            assert pytest_raise_system_exit.value.code == 2

    @pytest.mark.asyncio
    async def test_link(self):
        with pytest.raises(SystemExit) as pytest_raise_system_exit:
            main(test_args=['link'])

            assert pytest_raise_system_exit.value.code == 2

        with pytest.raises(ResponseFailed):
            bad_doi = 'bad_doi'
            main(test_args=['link', bad_doi])
