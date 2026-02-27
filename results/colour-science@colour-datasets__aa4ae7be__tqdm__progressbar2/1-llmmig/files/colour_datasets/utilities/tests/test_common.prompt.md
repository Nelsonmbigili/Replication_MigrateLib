The following Python code currently uses the library "tqdm" version 4.67.1.
Migrate this code to use the library "progressbar2" version 4.5.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "tqdm" to "progressbar2".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "tqdm" and "progressbar2".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
"""Define the unit tests for the :mod:`colour_datasets.utilities.common` module."""

import os
import shutil
import tempfile

import pytest

from colour_datasets.loaders import build_Labsphere2019
from colour_datasets.utilities import (
    hash_md5,
    json_open,
    unpack_gzipfile,
    url_download,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2019 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "TestHashMd5",
    "TestUrlDownload",
    "TestJsonOpen",
    "TestUnpackGzipfile",
]


class TestHashMd5:
    """
    Define :func:`colour_datasets.utilities.common.hash_md5` definition unit
    tests methods.
    """

    def test_hash_md5(self) -> None:
        """Test :func:`colour_datasets.utilities.common.hash_md5` definition."""

        dataset = build_Labsphere2019()
        dataset.load()

        assert (
            hash_md5(
                os.path.join(dataset.record.repository, "dataset", "SRS-99-020.txt")
            )
            == "7c7a7b76c399e5c4e3afbd32e22b2b2e"
        )

        assert (
            hash_md5(
                os.path.join(dataset.record.repository, "dataset", "SRS-99-020.txt"),
                chunk_size=8,
            )
            == "7c7a7b76c399e5c4e3afbd32e22b2b2e"
        )


class TestUrlDownload:
    """
    Define :func:`colour_datasets.utilities.common.url_download` definition
    unit tests methods.
    """

    def setup_method(self) -> None:
        """Initialise the common tests attributes."""

        self._temporary_file = tempfile.NamedTemporaryFile(delete=False).name  # noqa: SIM115

    def teardown_method(self) -> None:
        """After tests actions."""

        os.remove(self._temporary_file)

    def test_url_download(self) -> None:
        """Test :func:`colour_datasets.utilities.common.url_download` definition."""

        dataset = build_Labsphere2019()
        dataset.load()

        md5 = hash_md5(
            os.path.join(dataset.record.repository, "dataset", "SRS-99-020.txt")
        )
        url_download(
            "https://zenodo.org/api/files/"
            "a1f87ae9-bf9b-4451-becd-b4b3d7e35cc5/SRS-99-020.txt",
            self._temporary_file,
        )

        assert md5 == hash_md5(self._temporary_file)

        url_download(
            "https://zenodo.org/api/files/"
            "a1f87ae9-bf9b-4451-becd-b4b3d7e35cc5/SRS-99-020.txt",
            self._temporary_file,
            md5,
        )

        pytest.raises(
            IOError,
            lambda: url_download("https://nemo.io", self._temporary_file),
        )
        pytest.raises(
            ValueError,
            lambda: url_download(
                "https://zenodo.org/api/files/"
                "a1f87ae9-bf9b-4451-becd-b4b3d7e35cc5/SRS-99-020.txt",
                self._temporary_file,
                "7c7a7b76c399e5c4e3afbd32e22b2b2f",
            ),
        )


class TestJsonOpen:
    """
    Define :func:`colour_datasets.utilities.common.json_open` definition
    unit tests methods.
    """

    def test_json_open(self) -> None:
        """Test :func:`colour_datasets.utilities.common.json_open` definition."""

        data = json_open("https://zenodo.org/api/records/3245883")

        assert data["id"] == 3245883

        pytest.raises(IOError, lambda: json_open("https://nemo.io"))


class TestUnpackGzipfile:
    """
    Define :func:`colour_datasets.utilities.common.unpack_gzipfile` definition
    unit tests methods.
    """

    def setup_method(self) -> None:
        """Initialise the common tests attributes."""

        self._temporary_directory = tempfile.mkdtemp()

    def teardown_method(self) -> None:
        """After tests actions."""

        shutil.rmtree(self._temporary_directory)

    def test_unpack_gzipfile(self) -> None:
        """
        Test :func:`colour_datasets.utilities.common.unpack_gzipfile`
        definition.
        """

        unpack_gzipfile(
            os.path.join(os.path.dirname(__file__), "resources", "example.txt.gz"),
            self._temporary_directory,
        )

        with open(
            os.path.join(self._temporary_directory, "example.txt")
        ) as file_handle:
            assert (
                file_handle.read()
                == 'This is the content of a text file stored inside a "GZIP" file.'
            )

```