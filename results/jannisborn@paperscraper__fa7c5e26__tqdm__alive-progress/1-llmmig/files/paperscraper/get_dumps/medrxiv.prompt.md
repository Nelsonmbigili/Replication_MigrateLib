The following Python code currently uses the library "tqdm" version 4.67.1.
Migrate this code to use the library "alive-progress" version 3.2.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "tqdm" to "alive-progress".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "tqdm" and "alive-progress".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
"""Dump medrxiv data in JSONL format."""

import json
import os
from datetime import datetime
from typing import Optional

import pkg_resources
from tqdm import tqdm

from ..xrxiv.xrxiv_api import MedRxivApi

today = datetime.today().strftime("%Y-%m-%d")
save_folder = pkg_resources.resource_filename("paperscraper", "server_dumps")
save_path = os.path.join(save_folder, f"medrxiv_{today}.jsonl")


def medrxiv(
    begin_date: Optional[str] = None,
    end_date: Optional[str] = None,
    save_path: str = save_path,
    max_retries: int = 10,
):
    """Fetches papers from medrxiv based on time range, i.e., begin_date and end_date.
    If the begin_date and end_date are not provided, then papers will be fetched from
    medrxiv starting from the launch date of medrxiv until current date. The fetched
    papers will be stored in jsonl format in save_path.

    Args:
        begin_date (str, optional): begin date expressed as YYYY-MM-DD.
            Defaults to None, i.e., earliest possible.
        end_date (str, optional): end date expressed as YYYY-MM-DD.
            Defaults to None, i.e., today.
        save_path (str, optional): Path where the dump is stored.
            Defaults to save_path.
        max_retries (int, optional): Number of retries when API shows connection issues.
            Defaults to 10.
    """
    # create API client
    api = MedRxivApi(max_retries=max_retries)
    # dump all papers
    with open(save_path, "w") as fp:
        for index, paper in enumerate(
            tqdm(api.get_papers(begin_date=begin_date, end_date=end_date))
        ):
            if index > 0:
                fp.write(os.linesep)
            fp.write(json.dumps(paper))

```