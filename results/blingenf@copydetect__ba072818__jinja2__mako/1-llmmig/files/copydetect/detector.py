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

from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from mako.template import Template  # Updated import for Mako

import copydetect.data as data_files
from .utils import (filter_code, highlight_overlap, get_copied_slices,
                    get_document_fingerprints, find_fingerprint_overlap,
                    get_token_coverage)
from . import __version__
from . import defaults
from ._config import CopydetectConfig

# (Other unchanged classes and methods remain the same)

    def generate_html_report(self, output_mode="save"):
        """Generates an html report listing all files with similarity
        above the display_threshold, with the copied code segments
        highlighted.

        Parameters
        ----------
        output_mode : {"save", "return"}
            If "save", the output will be saved to the file specified
            by self.out_file. If "return", the output HTML will be
            directly returned by this function.
        """
        if len(self.similarity_matrix) == 0:
            logging.error("Cannot generate report: no files compared")
            return

        code_list = self.get_copied_code_list()

        plot_mtx = np.copy(self.similarity_matrix[:,:,0])
        plot_mtx[plot_mtx == -1] = np.nan
        plt.imshow(plot_mtx)
        plt.colorbar()
        plt.tight_layout()
        sim_mtx_buffer = io.BytesIO()
        plt.savefig(sim_mtx_buffer)
        sim_mtx_buffer.seek(0)
        sim_mtx_base64 = base64.b64encode(sim_mtx_buffer.read()).decode()
        plt.close()

        scores=self.similarity_matrix[:,:,0][self.similarity_matrix[:,:,0]!=-1]
        plt.hist(scores, bins=20)
        plt.tight_layout()
        sim_hist_buffer = io.BytesIO()
        plt.savefig(sim_hist_buffer)
        sim_hist_buffer.seek(0)
        sim_hist_base64 = base64.b64encode(sim_hist_buffer.read()).decode()
        plt.close()

        # render template with mako and save as html
        with importlib.resources.open_text(
            data_files, "report.html", encoding="utf-8"
        ) as template_fp:
            template = Template(template_fp.read())  # Updated to use Mako's Template

        flagged = self.similarity_matrix[:,:,0] > self.conf.display_t
        flagged_file_count = np.sum(np.any(flagged, axis=1))

        formatted_conf = json.dumps(self.conf.to_json(), indent=4)
        output = template.render(
            config_params=formatted_conf,
            css_files=self.conf.css_files,
            version=__version__,
            test_count=len(self.test_files),
            test_files=self.test_files,
            compare_count=len(self.ref_files),
            compare_files=self.ref_files,
            flagged_file_count=flagged_file_count,
            code_list=code_list,
            sim_mtx_base64=sim_mtx_base64,
            sim_hist_base64=sim_hist_base64
        )  # Updated render method for Mako

        if output_mode == "save":
            with open(self.conf.out_file, "w", encoding="utf-8") as report_f:
                report_f.write(output)

            if not self.conf.silent:
                print(
                    f"Output saved to {self.conf.out_file.replace('//', '/')}"
                )
            if self.conf.autoopen:
                webbrowser.open(
                    'file://' + str(Path(self.conf.out_file).resolve())
                )
        elif output_mode == "return":
            return output
        else:
            raise ValueError("output_mode not supported")
