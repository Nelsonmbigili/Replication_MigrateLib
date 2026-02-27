"""
Zenodo
======

Define the objects implementing support for a *Zenodo* community and its
records:

-   :class:`colour_datasets.Record`
-   :class:`colour_datasets.Community`
"""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import tempfile
import textwrap
import typing
import urllib
import urllib.error
from collections.abc import Mapping
from html.parser import HTMLParser
from pprint import pformat

import setuptools.archive_util
from colour.utilities import optional, warning

from colour_datasets.records import Configuration
from colour_datasets.utilities import json_open, url_download

# Import progressbar2
import progressbar

if typing.TYPE_CHECKING:
    from colour.hints import (
        Any,
        Callable,
        Dict,
        Generator,
        List,
    )

__author__ = "Colour Developers"
__copyright__ = "Copyright 2019 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "Record",
    "Community",
]


class Record:
    """
    Define an object storing a *Zenodo* record data and providing methods to
    sync it in a local repository.

    Parameters
    ----------
    data
        *Zenodo* record data.
    configuration
        *Colour - Datasets* configuration.

    Attributes
    ----------
    -   :attr:`colour_datasets.Record.data`
    -   :attr:`colour_datasets.Record.configuration`
    -   :attr:`colour_datasets.Record.repository`
    -   :attr:`colour_datasets.Record.id`
    -   :attr:`colour_datasets.Record.title`

    Methods
    -------
    -   :meth:`colour_datasets.Record.__init__`
    -   :meth:`colour_datasets.Record.__str__`
    -   :meth:`colour_datasets.Record.__repr__`
    -   :meth:`colour_datasets.Record.from_id`
    -   :meth:`colour_datasets.Record.synced`
    -   :meth:`colour_datasets.Record.pull`
    -   :meth:`colour_datasets.Record.remove`

    Examples
    --------
    >>> record = Record(json_open("https://zenodo.org/api/records/3245883"))
    >>> record.id
    '3245883'
    >>> record.title
    'Camera Spectral Sensitivity Database - Jiang et al. (2013)'
    """

    def __init__(self, data: dict, configuration: Configuration | None = None) -> None:
        self._data: dict = data
        self._configuration: Configuration = optional(configuration, Configuration())

    @property
    def data(self) -> dict:
        """
        Getter property for the *Zenodo* record data.

        Returns
        -------
        :class:`dict`
            *Zenodo* record data.
        """

        return self._data

    @property
    def configuration(self) -> Configuration:
        """
        Getter property for the *Colour - Datasets* configuration.

        Returns
        -------
        :class:`colour_datasets.Configuration`
           *Colour - Datasets* configuration.
        """

        return self._configuration

    @property
    def repository(self) -> str:
        """
        Getter property for the *Zenodo* record local repository.

        Returns
        -------
        :class:`str`
            *Zenodo* record local repository.
        """

        return os.path.join(self._configuration.repository, self.id)

    @property
    def id(self) -> str:
        """
        Getter property for the *Zenodo* record id.

        Returns
        -------
        :class:`str`
            *Zenodo* record id.
        """

        return str(self._data["id"])

    @property
    def title(self) -> str:
        """
        Getter property for the *Zenodo* record title.

        Returns
        -------
        :class:`str`
            *Zenodo* record title.
        """

        return self._data["metadata"]["title"]

    def pull(self, use_urls_txt_file: bool = True, retries: int = 3) -> None:
        """
        Pull the *Zenodo* record data to the local repository.

        Parameters
        ----------
        use_urls_txt_file
            Whether to use the *urls.txt* file: if such a file is present in
            the *Zenodo* record data, the urls it defines take precedence over
            the record data files. The later will be used in the eventuality
            where the urls are not available.
        retries
            Number of retries in case where a networking error occurs or the
            *MD5* hash is not matching.

        Examples
        --------
        >>> from colour_datasets.utilities import suppress_stdout
        >>> record = Record.from_id("3245883")
        >>> record.remove()
        >>> with suppress_stdout():
        ...     record.pull()
        >>> record.synced()
        True
        """

        print(f'Pulling "{self.title}" record content...')  # noqa: T201

        if not os.path.exists(self._configuration.repository):
            os.makedirs(self._configuration.repository)

        downloads_directory = os.path.join(
            self.repository, self._configuration.downloads_directory
        )
        if not os.path.exists(downloads_directory):
            os.makedirs(downloads_directory)

        # As much as possible, the original file urls are used, those are
        # given by the content of :attr:`URLS_TXT_FILE` attribute file.
        urls_txt = None
        for file_data in self.data["files"]:
            if file_data["key"] == self._configuration.urls_txt_file:
                urls_txt = file_data
                break

        def urls_download(urls: Dict) -> None:
            """Download given urls."""

            # Initialize progress bar
            bar = progressbar.ProgressBar(max_value=len(urls))
            for i, (url, md5) in enumerate(urls.items()):
                filename = re.sub("/content$", "", url)
                filename = os.path.join(
                    downloads_directory,
                    urllib.parse.unquote(  # pyright: ignore
                        filename.split("/")[-1]
                    ),
                )
                url_download(url, filename, md5.split(":")[-1], retries)
                bar.update(i + 1)  # Update progress bar

        try:
            if use_urls_txt_file and urls_txt:
                urls = {}
                urls_txt_file = tempfile.NamedTemporaryFile(delete=False).name  # noqa: SIM115
                url_download(
                    urls_txt["links"]["self"],
                    urls_txt_file,
                    urls_txt["checksum"].split(":")[-1],
                    retries,
                )

                with open(urls_txt_file) as json_file:
                    urls_txt_json = json.load(json_file)
                    for url, md5 in urls_txt_json["urls"].items():
                        urls[url] = md5.split(":")[-1]

                shutil.copyfile(
                    urls_txt_file,
                    os.path.join(
                        downloads_directory, self._configuration.urls_txt_file
                    ),
                )

                urls_download(urls)
            else:
                msg = (
                    f'"{self._configuration.urls_txt_file}" file was not '
                    f"found in record data!"
                )
                raise ValueError(  # noqa: TRY301
                    msg
                )
        except (urllib.error.URLError, ValueError) as error:
            warning(
                f"An error occurred using urls from "
                f'"{self._configuration.urls_txt_file}" file: {error}\n'
                f"Switching to record urls..."
            )

            urls = {}
            for file_data in self.data["files"]:
                if file_data["key"] == self._configuration.urls_txt_file:
                    continue

                # TODO: Remove the following space escaping: The new Zenodo API
                # is not quoting filenames properly thus we are temporarily
                # escaping spaces for now.
                # https://github.com/colour-science/colour-datasets/issues/
                # 36#issuecomment-1773464695
                url = file_data["links"]["self"].replace(" ", "%20")

                urls[url] = file_data["checksum"].split(":")[-1]

            urls_download(urls)

        deflate_directory = os.path.join(
            self.repository, self._configuration.deflate_directory
        )
        if os.path.exists(deflate_directory):
            shutil.rmtree(deflate_directory, onerror=_remove_readonly)

        shutil.copytree(downloads_directory, deflate_directory)

        for filename in os.listdir(deflate_directory):
            filename = os.path.join(  # noqa: PLW2901
                deflate_directory, filename
            )
            if not os.path.isfile(filename):
                continue

            basename, extension = os.path.splitext(filename)
            basename = os.path.basename(basename)
            if extension.lower() in (".zip", ".tar", ".gz", ".bz2"):
                if basename.lower().endswith(".tar"):
                    basename = basename.rsplit(".", 1)[0]

                basename = basename.replace(".", "_")
                unpacking_directory = os.path.join(deflate_directory, basename)

                print(f'Unpacking "{filename}" archive...')  # noqa: T201
                setuptools.archive_util.unpack_archive(filename, unpacking_directory)
                os.remove(filename)

        with open(os.path.join(self.repository, "record.json"), "w") as record_json:
            json.dump(self.data, record_json, indent=4, sort_keys=True)
