### Explanation of Changes:
To migrate the code from using the `tqdm` library to the `alive-progress` library, the following changes were made:
1. **Import Statement**: Removed the `tqdm` import and replaced it with the `alive-progress` import.
2. **Progress Bar Usage**: Replaced the `tqdm` progress bar calls with the equivalent `alive-progress` calls:
   - Replaced `tqdm(iterable, total=len(iterable))` with `alive_bar(len(iterable))` from `alive-progress`.
   - Used the `with alive_bar(...) as bar:` context manager to handle the progress bar.
   - Called `bar()` inside the loop to update the progress bar for each iteration.

These changes ensure that the functionality remains the same while using the `alive-progress` library instead of `tqdm`.

---

### Modified Code:
```python
"""The wrapper class around a transformer and its functionality."""

import logging
import os
from typing import Dict, List, Union

import numpy as np
import pandas as pd
import torch
import umap

from torch.utils.data import DataLoader
from alive_progress import alive_bar  # Replaced tqdm with alive-progress

from tx2 import calc, dataset, utils
from tx2.cache import check, read, write


class Wrapper:
    """A wrapper or interface class between a transformer and the dashboard.

    This class handles running all of the calculations for the data needed by
    the front-end visualizations.
    """

    # (Constructor and other methods remain unchanged)

    def _compute_all_salience_maps(self):
        """Get a salience map of every test entrypoint and store it. This is one of
        the longest running steps (~1s per entry), and is separate so that it doesn't
        have to be recomputed just because the user wants to try different clusterings
        (which does not impact salience)"""

        logging.info("Computing salience maps...")
        self.salience_maps = []
        with alive_bar(len(self.test_texts), title="Computing salience maps") as bar:  # Replaced tqdm with alive-progress
            for entry in self.test_texts:
                deltas = calc.salience_map(
                    self.soft_classify, entry[: self.max_len], self.encodings
                )
                self.salience_maps.append(deltas)
                bar()  # Update the progress bar
        logging.info("Saving salience maps...")
        write(self.salience_maps, self.salience_maps_path)
        logging.info("Done!")

        self.salience_computed = True

    def _compute_all_salience_maps_raw(self):
        """Get a salience map of every test entrypoint and store it. This is one of
        the longest running steps (~1s per entry), and is separate so that it doesn't
        have to be recomputed just because the user wants to try different clusterings
        (which does not impact salience)"""

        logging.info("Computing salience maps...")
        self.salience_maps = []
        with alive_bar(len(self.test_texts), title="Computing salience maps (raw)") as bar:  # Replaced tqdm with alive-progress
            for entry in self.test_texts:
                deltas = calc.salience_map_batch(
                    self.raw_soft_classify, entry[: self.max_len], self.encodings
                )
                self.salience_maps.append(deltas)
                bar()  # Update the progress bar
        logging.info("Saving salience maps...")
        write(self.salience_maps, self.salience_maps_path)
        logging.info("Done!")

        self.salience_computed = True

    # (Other methods remain unchanged)
```

---

### Key Points:
1. **Progress Bar Replacement**: The `tqdm` progress bar was replaced with `alive-progress` using the `alive_bar` context manager.
2. **Progress Updates**: The `bar()` method is called inside the loop to update the progress bar for each iteration.
3. **No Other Changes**: The rest of the code remains unchanged to ensure compatibility with the existing application.