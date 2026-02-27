import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
import aiohttp

try:
    # Import for normal execution
    from scripts.gist import Gist
except ImportError:
    # Import for testing context
    from gist import Gist

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# GitHub username and access token are defined as ENV variables
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "rjvitorino")
GITHUB_TOKEN = os.getenv("GISTMASTER_TOKEN")

# API Endpoint to retrieve Gists and Headers for authentication
GITHUB_API = f"https://api.github.com/users/{GITHUB_USERNAME}/gists"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

GIST_FORMAT = """

### [{heading}](gists/{folder_name}/index.md)

* **Description**: {description}
* **Language**: {language}
* **Created at**: {creation_date}
* **Last updated at**: {update_date}

"""


README = r"""
# GistMaster

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/{github_username}/gists-catalogue/update_gists.yml?branch=main)
![GitHub commits](https://img.shields.io/github/commit-activity/m/{github_username}/gists-catalogue)
![GitHub contributors](https://img.shields.io/github/contributors/{github_username}/gists-catalogue)
![Coverage Status](https://coveralls.io/repos/github/{github_username}/gists-catalogue/badge.svg?branch=main)
![GitHub issues](https://img.shields.io/github/issues/{github_username}/gists-catalogue)
![GitHub last commit](https://img.shields.io/github/last-commit/{github_username}/gists-catalogue)
![GitHub language count](https://img.shields.io/github/languages/count/{github_username}/gists-catalogue)
![License](https://img.shields.io/github/license/{github_username}/gists-catalogue)
![GitHub pull requests](https://img.shields.io/github/issues-pr/{github_username}/gists-catalogue)

![GistMaster, a catalogue for your gists](docs/gistmaster.png)

Welcome to **GistMaster**, your self-updating catalogue for **Github Gists**!

This repository compiles my Gists automatically using Github Actions, keeping them organised in a well-structured and easy-to-browse format.

👉 **[Check my Gists below](#gists)** to explore various code samples.

🧑‍💻 If you like this, you can create your own catalogue! The project is designed to be easily reused by other Github users with minimal configuration, as explained in the [Quick Start](#quick-start) guide.


## Table of Contents

- [About](#about)
- [Quick Start](#quick-start)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Gists](#gists)

## About

👋 I'm **[@{github_username}]({github_url})**, and my open-source contributions are available on my **[Github profile]({github_url})**.
In this repository, you will find solutions to various interview questions, coding challenges, and random snippets and scripts I've created.
These gists are automatically fetched and updated using **Github Actions** and can be set up for your profile as well. 

👉 **[Explore my Gists below](#gists)** to see my work and discover useful code samples.

## Quick Start

🚀 For detailed installation and setup instructions, please refer to the [Installation Guide](docs/SETUP.md).

## Contributing

🤝 Contributions are welcome! Please read the [Contributing Guidelines](docs/CONTRIBUTING.md) and [Code of Conduct](docs/CODE_OF_CONDUCT.md).

## License

📜 This project is licensed under the terms of the [GPL-3.0 license](LICENSE).

## Contact

📧 For any questions, feel free to contact me via my [GitHub profile]({github_url}).

## Gists

"""

# Functions that use Github API to fetch its data


async def fetch_gists() -> List[Gist]:
    """
    Fetch the list of Gists for the user with username set in `GITHUB_USERNAME`.

    Returns:
        List[Gist]: A list of Gist objects.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(GITHUB_API, headers=HEADERS) as response:
                response.raise_for_status()
                gists_data = await response.json()
                return [Gist.from_dict(gist) for gist in gists_data]
        except aiohttp.ClientResponseError as http_error:
            logging.error(f"HTTP error occurred: {http_error}")
            raise
        except Exception as error:
            logging.error(f"An error occurred: {error}")
            raise


async def fetch_gist_content(raw_url: str) -> str:
    """
    Fetch the content of a Gist file.

    Args:
        raw_url (str): The raw URL of the gist file.

    Returns:
        response.text (str): The content of the gist file.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(raw_url) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientResponseError as http_error:
            logging.error(f"HTTP error occurred: {http_error}")
            raise
        except Exception as error:
            logging.error(f"An error occurred: {error}")
            raise


# The rest of the code remains unchanged
