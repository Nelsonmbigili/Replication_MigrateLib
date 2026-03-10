### Explanation of Changes
To migrate the code from using the `tqdm` library to the `alive-progress` library, I replaced the `tqdm` import and its usage in the loop. The `alive-progress` library provides a different way to create a progress bar, which requires using the `alive_bar` context manager. The main change involves wrapping the iterable with `alive_bar` instead of `tqdm`. The progress bar will automatically handle the display and updating of the progress.

### Modified Code
```python
"""Dump bioRxiv data in JSONL format."""

import json
import os
from datetime import datetime
from typing import Optional

import pkg_resources
from alive_progress import alive_bar  # Changed import from tqdm to alive-progress

from ..xrxiv.xrxiv_api import BioRxivApi

today = datetime.today().strftime("%Y-%m-%d")
save_path = os.path.join(
    pkg_resources.resource_filename("paperscraper", "server_dumps"),
    f"biorxiv_{today}.jsonl",
)


def biorxiv(
    begin_date: Optional[str] = None,
    end_date: Optional[str] = None,
    save_path: str = save_path,
    max_retries: int = 10,
):
    """Fetches papers from biorxiv based on time range, i.e., begin_date and end_date.
    If the begin_date and end_date are not provided, papers will be fetched from biorxiv
    from the launch date of biorxiv until the current date. The fetched papers will be
    stored in jsonl format in save_path.

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
    api = BioRxivApi(max_retries=max_retries)

    # dump all papers
    with open(save_path, "w") as fp:
        papers = api.get_papers(begin_date=begin_date, end_date=end_date)
        with alive_bar(len(papers)) as bar:  # Using alive_bar for progress
            for index, paper in enumerate(papers):
                if index > 0:
                    fp.write(os.linesep)
                fp.write(json.dumps(paper))
                bar()  # Update the progress bar
```