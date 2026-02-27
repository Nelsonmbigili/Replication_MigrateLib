### Explanation of Changes:
To migrate the code from using the `tqdm` library to the `progressbar2` library, the following changes were made:
1. **Import Replacement**: Removed the `tqdm` import and replaced it with `progressbar` (the main module of `progressbar2`).
2. **Progress Bar Initialization**: Replaced the `tqdm` progress bar initialization with `progressbar.ProgressBar()`.
3. **Progress Bar Usage**: Updated the loops where `tqdm` was used to use `progressbar.ProgressBar()` instead. Specifically:
   - Replaced `tqdm(file_list, ...)` with `progressbar.ProgressBar()` and wrapped the loop with the progress bar.
   - Adjusted the `disable` parameter logic to conditionally enable or disable the progress bar using `progressbar.NullBar()` when `silent` is `True`.
4. **Bar Format**: Removed the `bar_format` parameter from `tqdm` since `progressbar2` does not support it directly. Instead, the default progress bar format of `progressbar2` is used.

### Modified Code:
Here is the updated code after migrating to `progressbar2`:

```python
"""This module contains functions for detecting overlap between
a set of test files (files to check for plagairism) and a set of
reference files (files that might have been plagairised from).
"""

from pathlib import Path
import time
import logging
import webbrowser
import importlib.resources
import io
import base64
import json

import progressbar  # Replaced tqdm with progressbar2
import numpy as np
import matplotlib.pyplot as plt
from jinja2 import Template

import copydetect.data as data_files
from .utils import (filter_code, highlight_overlap, get_copied_slices,
                    get_document_fingerprints, find_fingerprint_overlap,
                    get_token_coverage)
from . import __version__
from . import defaults
from ._config import CopydetectConfig

# (The rest of the unchanged code remains here...)

class CopyDetector:
    """Main plagairism detection class. Searches provided directories
    and uses detection parameters to calculate similarity between all
    files found in the directories
    """
    def __init__(self, test_dirs=None, ref_dirs=None,
                 boilerplate_dirs=None, extensions=None,
                 noise_t=defaults.NOISE_THRESHOLD,
                 guarantee_t=defaults.GUARANTEE_THRESHOLD,
                 display_t=defaults.DISPLAY_THRESHOLD,
                 same_name_only=False, ignore_leaf=False, autoopen=True,
                 disable_filtering=False, force_language=None,
                 truncate=False, out_file="./report.html", css_files=None,
                 silent=False, encoding: str = "utf-8"):
        conf_args = locals()
        conf_args = {
            key: val
            for key, val in conf_args.items()
            if key != "self" and val is not None
        }
        self.conf = CopydetectConfig(**conf_args)

        self.test_files = self._get_file_list(
            self.conf.test_dirs, self.conf.extensions
        )
        self.ref_files = self._get_file_list(
            self.conf.ref_dirs, self.conf.extensions
        )
        self.boilerplate_files = self._get_file_list(
            self.conf.boilerplate_dirs, self.conf.extensions
        )

        # before run() is called, similarity data should be empty
        self.similarity_matrix = np.array([])
        self.token_overlap_matrix = np.array([])
        self.slice_matrix = {}
        self.file_data = {}

    # (Other unchanged methods remain here...)

    def _preprocess_code(self, file_list):
        """Generates a CodeFingerprint object for each file in the
        provided file list. This is where the winnowing algorithm is
        actually used.
        """
        boilerplate_hashes = self._get_boilerplate_hashes()
        progress = progressbar.ProgressBar() if not self.conf.silent else progressbar.NullBar()
        for code_f in progress(file_list):  # Replaced tqdm with progressbar
            if code_f not in self.file_data:
                try:
                    self.file_data[code_f] = CodeFingerprint(
                        code_f, self.conf.noise_t, self.conf.window_size,
                        boilerplate_hashes, not self.conf.disable_filtering,
                        self.conf.force_language, encoding=self.conf.encoding)

                except UnicodeDecodeError:
                    logging.warning(f"Skipping {code_f}: file not UTF-8 text")
                    continue

    def _comparison_loop(self):
        """The core code used to determine code overlap. The overlap
        between each test file and each compare file is computed and
        stored in similarity_matrix. Token overlap information and the
        locations of copied code are stored in slice_matrix and
        token_overlap_matrix, respectively.
        """

        self.similarity_matrix = np.full(
            (len(self.test_files), len(self.ref_files), 2),
            -1,
            dtype=np.float64,
        )
        self.token_overlap_matrix = np.full(
            (len(self.test_files), len(self.ref_files)), -1
        )
        self.slice_matrix = {}

        # this is used to track which files have been compared to avoid
        # unnecessary duplication when there is overlap between the
        # test and reference files
        comparisons = {}

        progress = progressbar.ProgressBar() if not self.conf.silent else progressbar.NullBar()
        for i, test_f in enumerate(progress(self.test_files)):  # Replaced tqdm with progressbar
            for j, ref_f in enumerate(self.ref_files):
                if (test_f not in self.file_data
                        or ref_f not in self.file_data
                        or test_f == ref_f
                        or (self.conf.same_name_only
                            and (Path(test_f).name != Path(ref_f).name))
                        or (self.conf.ignore_leaf
                            and (Path(test_f).parent == Path(ref_f).parent))):
                    continue

                if (ref_f, test_f) in comparisons:
                    ref_idx, test_idx = comparisons[(ref_f, test_f)]
                    overlap = self.token_overlap_matrix[ref_idx, test_idx]
                    sim2, sim1 = self.similarity_matrix[ref_idx, test_idx]
                else:
                    overlap, (sim1, sim2), (slices1, slices2) = compare_files(
                        self.file_data[test_f], self.file_data[ref_f]
                    )
                    comparisons[(test_f, ref_f)] = (i, j)
                    if slices1.shape[0] != 0:
                        self.slice_matrix[(test_f, ref_f)] = [slices1, slices2]

                self.similarity_matrix[i, j] = np.array([sim1, sim2])
                self.token_overlap_matrix[i, j] = overlap

    # (The rest of the unchanged methods remain here...)
```

### Summary of Changes:
- Replaced `tqdm` with `progressbar2` for progress bar functionality.
- Used `progressbar.ProgressBar()` for normal progress bars and `progressbar.NullBar()` to disable progress bars when `silent=True`.
- Removed `bar_format` since it is not supported by `progressbar2`. The default progress bar format is used instead.