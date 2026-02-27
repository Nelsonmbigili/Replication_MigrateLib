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

from alive_progress import alive_bar
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

class CodeFingerprint:
    # (Class definition remains unchanged)
    ...

def compare_files(file1_data, file2_data):
    # (Function definition remains unchanged)
    ...

class CopyDetector:
    # (Class definition remains unchanged up to the _preprocess_code method)

    def _preprocess_code(self, file_list):
        """Generates a CodeFingerprint object for each file in the
        provided file list. This is where the winnowing algorithm is
        actually used.
        """
        boilerplate_hashes = self._get_boilerplate_hashes()
        with alive_bar(len(file_list), title="Processing files") as bar:
            for code_f in file_list:
                if code_f not in self.file_data:
                    try:
                        self.file_data[code_f] = CodeFingerprint(
                            code_f, self.conf.noise_t, self.conf.window_size,
                            boilerplate_hashes, not self.conf.disable_filtering,
                            self.conf.force_language, encoding=self.conf.encoding)

                    except UnicodeDecodeError:
                        logging.warning(f"Skipping {code_f}: file not UTF-8 text")
                        continue
                bar()  # Update the progress bar

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

        with alive_bar(len(self.test_files), title="Comparing files") as bar:
            for i, test_f in enumerate(self.test_files):
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
                bar()  # Update the progress bar

    def run(self):
        """Runs the copy detection loop for detecting overlap between
        test and reference files. If no files are in the provided
        directories, the similarity matrix will remain empty and any
        attempts to generate a report will fail.
        """
        if len(self.test_files) == 0:
            logging.error("Copy detector failed: No files found in "
                          "test directories")
        elif len(self.ref_files) == 0:
            logging.error("Copy detector failed: No files found in "
                          "reference directories")
        else:
            start_time = time.time()

            if not self.conf.silent:
                print("  0.00: Generating file fingerprints")

            self._preprocess_code(self.test_files + self.ref_files)

            if not self.conf.silent:
                print(f"{time.time()-start_time:6.2f}: Beginning code comparison")

            self._comparison_loop()

            if not self.conf.silent:
                print(f"{time.time()-start_time:6.2f}: Code comparison completed")

    # (Remaining methods remain unchanged)
    ...
