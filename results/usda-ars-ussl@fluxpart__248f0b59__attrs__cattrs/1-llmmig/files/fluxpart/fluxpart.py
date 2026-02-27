from copy import deepcopy
import datetime as pydatetime
from functools import lru_cache
from glob import iglob
import os
import pickle
import zipfile

import cattrs

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from .__version__ import __version__
from .wue import water_use_efficiency, WUEError
from .hfdata import (
    HFData,
    HFSummary,
    HFDataSource,
    HFDataReadError,
    TooFewDataError,
)
from .partition import fvspart_progressive, FVSPSolution
from .util import vapor_press_deficit
from .containers import AllFluxes, WUE
from .constants import MOLECULAR_WEIGHT as MW


EC_TOA5 = {
    "filetype": "csv",
    "skiprows": 4,
    "time_col": 0,
    "cols": (2, 3, 4, 5, 6, 7, 8),
    "temper_unit": "C",
    "unit_convert": dict(q=1e-3, c=1e-6, P=1e3),
    "na_values": "NAN",
    # since pandas >2.0, format="ISO8601" is needed for auto detection
    # if fractional seconds (.%f) not present in all timestamps
    # e.g.: ..., 08:21:48.9, 08:21:49, 08:21:49.1, ...
    "to_datetime_kws": {"format": "ISO8601"},
 }

EC_TOB1 = {
    "filetype": "tob1",
    "time_col": 0,
    "cols": (3, 4, 5, 6, 7, 8, 9),
    "temper_unit": "C",
    "unit_convert": dict(q=1e-3, c=1e-6, P=1e3),
}

EC_GHG1 = {
    "filetype": "ghg",
    "sep": "\t",
    "cols": (11, 12, 13, 7, 8, 9, 10),
    "time_col": [5, 6],
    "unit_convert": dict(q=1e-3 * MW.vapor, c=1e-3 * MW.co2, P=1e3),
    "temper_unit": "C",
    "skiprows": 8,
    "na_values": "NAN",
    "to_datetime_kws": {"format": "%Y-%m-%d %H:%M:%S:%f"},
}

HFD_FORMAT = EC_TOA5

WUE_OPTIONS = {
    "ci_mod": "const_ratio",
    "ci_mod_param": None,
    "leaf_temper": None,
    "leaf_temper_corr": 0,
    "diff_ratio": 1.6,
}

HFD_OPTIONS = {
    "bounds": {"c": (0, np.inf), "q": (0, np.inf)},
    "rd_tol": 0.5,
    "ad_tol": 1024,
    "ustar_tol": 0.1,
    "correct_external": True,
}

PART_OPTIONS = dict(adjust_fluxes=True)

_bad_ustar = "ustar = {:.4} <= ustar_tol = {:.4}"
_bad_vpd = "vpd = {:.4} Pa <= 0"
_bad_qflux = "Fq = {:.4} <= 0"
_night_mssg = "Nighttime, fluxes all non-stomatal"
_fp_result_str = (
    "===============\n"
    "Fluxpart Result\n"
    "===============\n"
    "fluxpart version = {version}\n"
    "date = {date}\n"
    "---------------\n"
    "dataread = {dataread}\n"
    "attempt_partition = {attempt_partition}\n"
    "partition_success = {partition_success}\n"
    "mssg = {mssg}\n"
    "label = {label}\n"
    "sunrise = {sunrise}\n"
    "sunset = {sunset}\n"
    + AllFluxes().results_str()
    + "\n"
    + HFSummary().results_str()
    + "\n"
    + WUE().results_str()
    + "\n"
    + FVSPSolution().results_str()
)


class Error(Exception):
    pass


class FluxpartError(Error):
    def __init__(self, message):
        self.message = message


def fvspart(
    file_or_dir,
    time_sorted=False,
    interval=None,
    hfd_format=None,
    hfd_options=None,
    meas_wue=None,
    wue_options=None,
    part_options=None,
    label=None,
    stdout=True,
    verbose=True,
):
    # Function body remains unchanged
    ...


class FVSResult(object):
    """FVS partitioning result."""

    def __init__(
        self,
        dataread=False,
        attempt_partition=False,
        partition_success=False,
        mssg=None,
        label=None,
        sunrise=None,
        sunset=None,
        fluxes=AllFluxes(),
        hfsummary=HFSummary(),
        wue=WUE(),
        fvsp_solution=FVSPSolution(),
    ):
        """Fluxpart result."""
        self.version = __version__
        self.dataread = dataread
        self.attempt_partition = attempt_partition
        self.partition_success = partition_success
        self.mssg = mssg
        self.fluxes = fluxes
        self.label = label
        self.sunrise = sunrise
        self.sunset = sunset
        self.fvsp_solution = fvsp_solution
        self.wue = wue
        self.hfsummary = hfsummary

    def __str__(self):
        fluxpart = cattrs.unstructure(self.fvsp_solution)
        wqc_data = fluxpart.pop("wqc_data")
        rootsoln = fluxpart.pop("rootsoln")
        return _fp_result_str.format(
            timenow=pydatetime.datetime.now(),
            version=self.version,
            dataread=self.dataread,
            attempt_partition=self.attempt_partition,
            partition_success=self.partition_success,
            mssg=self.mssg,
            label=self.label,
            sunrise=self.sunrise,
            sunset=self.sunset,
            **cattrs.unstructure(self.fluxes),
            **cattrs.unstructure(self.hfsummary),
            **cattrs.unstructure(self.wue),
            **fluxpart,
            **wqc_data,
            **rootsoln,
        )


class FluxpartResult(object):
    def __init__(self, fp_results):
        if isinstance(fp_results, pd.DataFrame):
            self.df = fp_results
            return
        index = pd.DatetimeIndex(r.label for r in fp_results)
        df0 = pd.DataFrame(
            (r.fluxes.common_units() for r in fp_results),
            index=index,
            columns=fp_results[0].fluxes.common_units().keys(),
        )
        df1 = pd.DataFrame(
            (r.hfsummary.common_units() for r in fp_results),
            index=index,
            columns=fp_results[0].hfsummary.common_units().keys(),
        )
        df2 = pd.DataFrame(
            (r.wue.common_units() for r in fp_results),
            index=index,
            columns=fp_results[0].wue.common_units().keys(),
        )
        df3 = pd.DataFrame(
            (r.fvsp_solution.common_units() for r in fp_results),
            index=index,
            columns=fp_results[0].fvsp_solution.common_units().keys(),
        )
        df4 = pd.DataFrame(
            {
                "dataread": [r.dataread for r in fp_results],
                "attempt_partition": [r.attempt_partition for r in fp_results],
                "partition_success": [r.partition_success for r in fp_results],
                "mssg": [r.mssg for r in fp_results],
                "sunrise": [r.sunrise for r in fp_results],
                "sunset": [r.sunset for r in fp_results],
            },
            index=index,
        )
        self.df = pd.concat(
            [df0, df1, df2, df3, df4],
            axis=1,
            sort=False,
            keys=["fluxes", "hfsummary", "wue", "fvsp_solution", "fluxpart"],
        )

        self.meta = {
            "version": fp_results[0].version,
            "date": str(pydatetime.datetime.now()),
        }

    def __str__(self):
        if len(self.df) == 1:
            return self.istr(0)
        else:
            return self.df.__str__()

    def __getitem__(self, item):
        return self.df[item]

    def __getattr__(self, x):
        return getattr(self.df, x)

    def plot_co2(
        self,
        start=None,
        end=None,
        units="mass",
        components=(0, 1, 2),
        ax=None,
        **kws,
    ):
        if ax is None:
            ax = plt.gca()
        if units == "mass":
            cols = ["Fc", "Fcp", "Fcr"]
            ylab = r"$\mathrm{CO_2\ Flux\ (mg\ m^{-2}\ s^{-1})}$"
        else:
            cols = ["Fc_mol", "Fcp_mol", "Fcr_mol"]
            ylab = r"$\mathrm{CO_2\ Flux\ (umol\ m^{-2}\ s^{-1})}$"
        labels = [
            r"$\mathrm{F_c}$",
            r"$\mathrm{F_{c_p}}$",
            r"$\mathrm{F_{c_r}}$",
        ]
        cols = [cols[j] for j in components]
        labels = [labels[j] for j in components]
        self.df.loc[start:end, ("fluxes", cols)].plot(ax=ax)
        ax.legend(labels)
        ax.set_ylabel(ylab)
        return ax

    def plot_h2o(
        self,
        start=None,
        end=None,
        units="mass",
        components=(0, 1, 2),
        ax=None,
        **kws,
    ):
        if ax is None:
            ax = plt.gca()
        if units == "mass":
            cols = ["Fq", "Fqt", "Fqe"]
            ylab = r"$\mathrm{H_20\ Flux\ (g\ m^{-2}\ s^{-1})}$"
        elif units == "mol":
            cols = ["Fq_mol", "Fqt_mol", "Fqe_mol"]
            ylab = r"$\mathrm{H_20\ Flux\ (mmol\ m^{-2}\ s^{-1})}$"
        else:
            cols = ["LE", "LEt", "LEe"]
            ylab = r"$\mathrm{LE\ (W\ m^{-2})}$"
        labels = [
            r"$\mathrm{F_q}$",
            r"$\mathrm{F_{q_t}}$",
            r"$\mathrm{F_{q_e}}$",
        ]

        cols = [cols[j] for j in components]
        labels = [labels[j] for j in components]

        self.df.loc[start:end, ("fluxes", cols)].plot(ax=ax)
        ax.legend(labels)
        ax.set_ylabel(ylab)
        return ax

    def istr(self, i):
        """Return a string representation of the ith result"""
        return _fp_result_str.format(
            version=self.meta["version"],
            date=self.meta["date"],
            label=self.df.index[i],
            **self.df.iloc[i]["fluxpart"].to_dict(),
            **self.df.iloc[i]["fluxes"].to_dict(),
            **self.df.iloc[i]["fvsp_solution"].to_dict(),
            **self.df.iloc[i]["hfsummary"].to_dict(),
            **self.df.iloc[i]["wue"].to_dict(),
        )

    def save(self, filename):
        self.save_pickle(filename)

    def save_csv(self, filename):
        self.df.to_csv(filename) #, na_rep="NAN")

    def save_pickle(self, filename):
        self.df.to_pickle(filename)


def _converter_func(slope, intercept):
    """Return a function for linear transform of data."""

    if type(slope) is str:
        return slope

    def func(val):
        return slope * val + intercept

    return func


def _files(file_or_dir):
    if type(file_or_dir) is str:
        file_or_dir = [file_or_dir]
    unsorted_files = []
    for path in file_or_dir:
        if os.path.isfile(path):
            unsorted_files.append(path)
            continue
        if os.path.isdir(path):
            path = os.path.join(path, "*")
        unsorted_files += iglob(path)
    return unsorted_files


def _set_leaf_wue(
    meas_wue, wue_options, part_options, hfsum, date, datetime, temper_unit
):
    # TODO: these should work with file objects, not just str name
    wue_options = {**WUE_OPTIONS, **(wue_options or {})}
    heights, leaf_temper = None, None
    canopy_ht = wue_options.pop("canopy_ht", None)
    meas_ht = wue_options.pop("meas_ht", None)
    if "heights" in wue_options:
        heights = wue_options.pop("heights")
        if not callable(heights):
            heights = _lookup(heights, 0, 1, 2)
    if "leaf_temper" in wue_options:
        leaf_temper = wue_options.pop("leaf_temper")
        if type(leaf_temper) is str:
            leaf_temper = _lookup(leaf_temper, 0, 1)
    if meas_wue:
        if type(meas_wue) is str:
            meas_wue = _lookup(meas_wue, 0, 1)

    try:
        if meas_wue:
            if callable(meas_wue):
                leaf_wue = WUE(wue=meas_wue(datetime))
            else:
                leaf_wue = WUE(wue=float(meas_wue))
        else:
            if heights is not None:
                if callable(heights):
                    canopy_ht, meas_ht = heights(date)
                else:
                    canopy_ht, meas_ht = heights
            else:
                if callable(canopy_ht):
                    canopy_ht = canopy_ht(date)
                if callable(meas_ht):
                    meas_ht = meas_ht(date)
            leaf_t = None
            if leaf_temper is not None:
                if callable(leaf_temper):
                    leaf_t = leaf_temper(datetime)
                else:
                    leaf_t = float(leaf_temper)
                if temper_unit == "C" or temper_unit == "CELSIUS":
                    leaf_t = leaf_t + 273.15
            leaf_wue = water_use_efficiency(
                hfsum,
                canopy_ht=canopy_ht,
                meas_ht=meas_ht,
                leaf_temper=leaf_t,
                **wue_options,
            )
        return leaf_wue

    except WUEError:
        raise


def _peektime(files, **kwargs):
    if kwargs["filetype"] == "csv" or kwargs["filetype"] == "ghg":
        dtcols = kwargs["time_col"]
        if type(dtcols) is int:
            dtcols = [dtcols]
        sep = kwargs.get("delimiter", ",")
        sep = kwargs.get("sep", sep)
        datetimes = []
        to_datetime_kws = kwargs.get("to_datetime_kws", {})
    if kwargs["filetype"] == "csv":
        for file_ in files:
            with open(file_, "rt") as f:
                for _ in range(kwargs.get("skiprows", 0)):
                    f.readline()
                row = f.readline().split(sep)
                tstamp = " ".join([row[i].strip("'\"") for i in dtcols])
                datetimes.append(pd.to_datetime(tstamp, **to_datetime_kws))
    elif kwargs["filetype"] == "ghg":
        for file_ in files:
            with zipfile.ZipFile(file_) as z:
                with z.open(os.path.basename(file_)[:-3] + "data", "r") as f:
                    for _ in range(kwargs.get("skiprows", 0)):
                        f.readline()
                    row = f.readline().decode("utf-8").split(sep)
                    tstamp = " ".join([row[i].strip("'\"") for i in dtcols])
                    datetimes.append(pd.to_datetime(tstamp, **to_datetime_kws))
    else:  # "tob1"
        source = HFDataSource(files, count=5, **kwargs)
        datetimes = [df.index[0] for df in source.reader(interval=None)]
    return datetimes


def _validate_hfd_format(hfd_format):
    if "cols" not in hfd_format:
        raise Error("No value for hfd_format['cols'] given.")
    if "filetype" not in hfd_format:
        raise Error("No value for hfd_format['filetype'] given.")
    if hfd_format["filetype"] not in ("csv", "tob1", "ghg"):
        raise Error(f"Unrecognized filetype: {hfd_format['filetype']}")


def _lookup(csv_file, date_icol, icol1, icol2=None, method="ffill"):
    """Create a function for looking up data in csv file.
    date_icol, icol1, icol2 : int
        column index for the respective data
    method : str
        Interpolation method used with pandas df.index.get_indexer. The
        default 'ffill' returns the PREVIOUS values if no exact date
        match is found in the lookup.

    """
    df = pd.read_csv(csv_file, index_col=date_icol, parse_dates=True)

    @lru_cache()
    def func(date):
        ix = df.index.get_indexer([pd.to_datetime(date)], method=method)[0]
        if icol2 is None:
            return df.iloc[ix, icol1 - 1]
        else:
            return df.iloc[ix, icol1 - 1], df.iloc[ix, icol2 - 1]

    return func
