### Explanation of Changes:
The original code uses the `attrs` library for defining data classes (e.g., `@attr.s` and `attr.ib`). To migrate to the `cattrs` library, which is primarily used for serialization and deserialization of data classes, the following changes were made:

1. **Replace `attrs` with `dataclasses`:**
   - The `cattrs` library works seamlessly with Python's built-in `dataclasses` module. Therefore, the `@attr.s` decorator is replaced with `@dataclass` from the `dataclasses` module.
   - The `attr.ib` fields are replaced with standard `dataclasses.field` or simple type annotations.

2. **Remove `attrs` import:**
   - The `import attr` statement is removed since `attrs` is no longer used.

3. **Add `dataclasses` import:**
   - The `dataclasses` module is imported to use `@dataclass` and `field`.

4. **No changes to logic:**
   - The logic and structure of the code remain unchanged, as the migration only involves replacing `attrs` with `dataclasses` and ensuring compatibility with `cattrs`.

---

### Modified Code:
```python
"""
Read and model eddy covariance high-frequency time series data.

The following notation is used in variable naming to represent
meteorological quantities (SI units)::

    u, v, w = wind velocities (m/s)
    q = water vapor mass concentration (kg/m^3)
    c = carbon dioxide mass concentration (kg/m^3)
    T = air temperature (K)
    P = total air pressure (Pa)

"""
from dataclasses import dataclass, field
import math
import numpy as np
import pandas as pd

from . import util
from .constants import MOLECULAR_WEIGHT as MW
from .constants import SPECIFIC_HEAT_CAPACITY as CP
from .constants import SPECIFIC_GAS_CONSTANT as GC


class Error(Exception):
    pass


class HFDataReadError(Error):
    def __init__(self, message):
        self.message = message


class TooFewDataError(Error):
    pass


VAR_NAMES = ["u", "v", "w", "c", "q", "T", "P"]

_badfiletype = "File type not recognized ({})"
_toofewdata_rel = "data frac = {frac:.4} < rd_tol = {rd_tol:.4}"
_toofewdata_abs = "data length = {N} < ad_tol = {ad_tol}"


class HFData(object):
    """
    Parameters
    ----------
    hf_dataframe
        High frequency eddy covariance dataframe. Must include columns
        for ["u", "v", "w", "c", "q", "T", "P"]. Normally, dataframe
        should have a datetime index. Dataframe may include also boolean
        mask columns.

    """

    def __init__(self, hf_dataframe):
        self.dataframe = hf_dataframe
        self._already_corrected_external = False

    def __getitem__(self, name):
        """Column-wise get without specifying dataframe attribute"""
        return self.dataframe.loc[:, name]

    def __setitem__(self, name, value):
        """Column-wise set without specifying dataframe attribute"""
        self.dataframe.loc[:, name] = value

    def cleanse(self, bounds=None, rd_tol=0.5, ad_tol=1024):
        """Apply some data QC, remove bad data.

        If problems are found (data not readable, out-of-bounds, or
        flagged), self.dataframe is modified to contain only the longest
        contiguous stretch of good data. An error is raised if the
        resulting data are too few. The criteria for judging 'too few'
        can be specified in both relative and absolute terms: the
        datafile is rejected if the good stretch is a fraction of the
        total data that is less than `rd_tol`, and/or is less than
        `ad_tol` records long.

        Parameters
        ----------
        bounds : dict, optional
            Dictionary specifying lower and upper bounds for legal data.
            Dict entries have the form ``varname: (lower, upper)``,
            where varname is one of 'u', 'v', 'w', 'q', 'c', 'T', or
            'P', and the 2-tuple holds values for the lower and upper
            bounds. Default is None.
        rd_tol : float, optional
            Relative tolerance for rejecting the datafile. Default is
            `rd_tol` = 0.5.
        ad_tol : int, optional
            Absolute tolerance for rejecting the datafile. Default is
            `ad_tol` = 1024.

        """
        bounds = bounds or {}
        data = self.dataframe

        # 1D mask is True for a row if any data are nan, any flag is
        # True, or any data are out-of-bounds
        varindx = pd.Index(VAR_NAMES)
        mask = data.loc[:, varindx].isnull().any(axis=1)
        mask |= data.loc[:, data.columns.difference(varindx)].any(axis=1)
        for var, (low, high) in bounds.items():
            mask |= (data[var] < low) | (data[var] > high)
        if isinstance(data.index, pd.DatetimeIndex) and data.shape[0] > 1:
            diff = data.index.to_series().diff()
            mask |= (abs((diff / diff.mode()[0]) - 1) > .0001)

        # Find longest span of valid (unmasked) data
        marray = np.ma.array(np.zeros([data.shape[0]]), mask=mask.values)
        unmasked_slices = np.ma.clump_unmasked(marray) or [slice(0, 0)]
        max_indx = np.argmax([s.stop - s.start for s in unmasked_slices])
        max_slice = unmasked_slices[max_indx]
        len_max_slice = max_slice.stop - max_slice.start

        # verify sufficient data length
        data_frac = len_max_slice / data.shape[0]
        if data_frac < rd_tol:
            self.dataframe = None
            mssg = _toofewdata_rel.format(frac=data_frac, rd_tol=rd_tol)
            raise TooFewDataError(mssg)
        if len_max_slice < ad_tol:
            self.dataframe = None
            mssg = _toofewdata_abs.format(N=len_max_slice, ad_tol=ad_tol)
            raise TooFewDataError(mssg)

        self.dataframe = data.iloc[max_slice]
        return

    def correct_external(self):
        """Adjust q and c data series to correct for external effects.

        Water vapor and carbon dioxide series data in the dataframe are
        corrected for external fluctuations associated with air
        temperature and vapor density. See: [WPL80]_ and [DK07]_.

        """
        if self._already_corrected_external:
            return
        ave_vapor = self["q"].mean()
        ave_co2 = self["c"].mean()
        ave_T = self["T"].mean()
        dev_vapor = self["q"] - ave_vapor
        dev_T = self["T"] - ave_T

        Pdryair = self["P"].mean() - ave_vapor * GC.vapor * ave_T
        rho_totair = ave_vapor + Pdryair / GC.dryair / ave_T

        specific_vapor = ave_vapor / rho_totair
        specific_co2 = ave_co2 / rho_totair
        mu = MW.dryair / MW.vapor
        muq = mu * specific_vapor
        muc = mu * specific_co2

        self["q"] += muq * dev_vapor + (1 + muq) * ave_vapor * dev_T / ave_T
        self["c"] += muc * dev_vapor + (1 + muq) * ave_co2 * dev_T / ave_T
        self._already_corrected_external = True
        return

    def summarize(self):
        """Summarize high frequency dataframe statistics.

        Returns
        -------
        :class:`~fluxpart.hfdata.HFSummary`

        """
        hfs = util.stats2(self.dataframe, VAR_NAMES)
        Pvap = hfs.ave_q * GC.vapor * hfs.ave_T
        rho_dryair = (hfs.ave_P - Pvap) / GC.dryair / hfs.ave_T
        rho_totair = rho_dryair + hfs.ave_q
        Cp = CP.dryair * (1 + 0.84 * hfs.ave_q / rho_totair)

        return HFSummary(
            T=hfs.ave_T,
            P=hfs.ave_P,
            Pvap=Pvap,
            ustar=(hfs.cov_w_u ** 2 + hfs.cov_w_v ** 2) ** 0.25,
            wind_w=hfs.ave_w,
            var_w=hfs.var_w,
            rho_vapor=hfs.ave_q,
            var_vapor=hfs.var_q,
            rho_co2=hfs.ave_c,
            var_co2=hfs.var_c,
            corr_q_c=hfs.cov_q_c / math.sqrt(hfs.var_q * hfs.var_c),
            H=rho_totair * Cp * hfs.cov_w_T,
            cov_w_q=hfs.cov_w_q,
            cov_w_c=hfs.cov_w_c,
            rho_dryair=rho_dryair,
            rho_totair=rho_totair,
            cov_w_T=hfs.cov_w_T,
            N=self.dataframe.shape[0],
        )

    def truncate_pow2(self):
        """Truncate dataframe length to largest possible power of 2."""
        truncate_len = 2 ** int(np.log2(self.dataframe.shape[0]))
        self.dataframe = self.dataframe.iloc[:truncate_len]


@dataclass
class HFSummary:
    """Summary of high frequency eddy covariance data.

    Parameters
    ----------
    T : float
        Mean air temperature, K.
    P, Pvap : float
        Mean total atmospheric (`P`) and vapor (`Pvap`) pressure, Pa.
    ustar : float
        Mean friction velocity, m/s.
    wind_w : float
        Mean vertical wind velocity, m/s.
    var_w : float
        Variance of vertical wind velocity, (m/s)^2.
    rho_vapor, rho_co2 : float
        Mean H2O vapor and CO2 concentrations, kg/m^3.
    var_vapor, var_co2 : float
        Variance of H2O vapor and CO2 concentrations, (kg/m^3)^2.
    corr_q_c : float
        Correlation coefficient for H2O and CO2 concentrations
    cov_w_q, cov_w_c : float
        Covariance of vertical wind velocity (w) with water vapor (q)
        and CO2 (c) mass densities, kg/m^2/s.
    H : float
        Sensible heat flux, W/m^2.
    rho_dryair, rho_totair : float
        Dry and moist air densities, kg/m^3.
    cov_w_T : float
        Covariance of temperature and vertical wind velocity, K m/s.
    N : int
        Length of data series.

    """

    T: float = field(default=np.nan)
    P: float = field(default=np.nan)
    Pvap: float = field(default=np.nan)
    ustar: float = field(default=np.nan)
    wind_w: float = field(default=np.nan)
    var_w: float = field(default=np.nan)
    rho_vapor: float = field(default=np.nan)
    rho_co2: float = field(default=np.nan)
    var_vapor: float = field(default=np.nan)
    var_co2: float = field(default=np.nan)
    corr_q_c: float = field(default=np.nan)
    cov_w_q: float = field(default=np.nan)
    cov_w_c: float = field(default=np.nan)
    H: float = field(default=np.nan)
    rho_dryair: float = field(default=np.nan)
    rho_totair: float = field(default=np.nan)
    cov_w_T: float = field(default=np.nan)
    N: int = field(default=np.nan)

    def __str__(self):
        # prints common units instead of SI
        return self.results_str().format(**self.common_units())

    @property
    def fc_ov_fq(self):
        return self.cov_w_c / self.cov_w_q

    @property
    def sigc_ov_sigq(self):
        return math.sqrt(self.var_co2 / self.var_vapor)

    def results_str(self):
        lab = self.common_units_labels()
        return (
            "---------------\n"
            "HF Data Summary\n"
            "---------------\n"
            "  T = {T:.4} " + lab["T"] + "\n"
            "  P = {P:.4} " + lab["P"] + "\n"
            "  Pvap = {Pvap:.4} " + lab["Pvap"] + "\n"
            "  ustar = {ustar:.4} " + lab["ustar"] + "\n"
            "  wind_w = {wind_w:.4} " + lab["wind_w"] + "\n"
            "  var_w = {var_w:.4} " + lab["var_w"] + "\n"
            "  rho_vapor = {rho_vapor:.4} " + lab["rho_vapor"] + "\n"
            "  rho_co2 = {rho_co2:.4} " + lab["rho_co2"] + "\n"
            "  var_vapor = {var_vapor:.4} " + lab["var_vapor"] + "\n"
            "  var_co2 = {var_co2:.4} " + lab["var_co2"] + "\n"
            "  corr_q_c = {corr_q_c:.4} " + lab["corr_q_c"] + "\n"
            "  cov_w_q = {cov_w_q:.4} " + lab["cov_w_q"] + "\n"
            "  H = {H:.4} " + lab["H"] + "\n"
            "  cov_w_c = {cov_w_c:.4} " + lab["cov_w_c"] + "\n"
            "  rho_dryair = {rho_dryair:.4} " + lab["rho_dryair"] + "\n"
            "  rho_totair = {rho_totair:.4} " + lab["rho_totair"] + "\n"
            "  cov_w_T = {cov_w_T:.4} " + lab["cov_w_T"] + "\n"
            "  N = {N:.0f} " + lab["N"]
        )

    def common_units(self):
        return dict(
            T=self.T - 273.15,
            P=1e-3 * self.P,
            Pvap=1e-3 * self.Pvap,
            ustar=self.ustar,
            wind_w=self.wind_w,
            var_w=self.var_w,
            rho_vapor=1e3 * self.rho_vapor,
            rho_co2=1e6 * self.rho_co2,
            var_vapor=1e6 * self.var_vapor,
            var_co2=1e12 * self.var_co2,
            corr_q_c=self.corr_q_c,
            cov_w_q=1e3 * self.cov_w_q,
            fc_ov_fq=1e3 * self.fc_ov_fq,
            sigc_ov_sigq=1e3 * self.sigc_ov_sigq,
            H=self.H,
            cov_w_c=1e6 * self.cov_w_c,
            rho_dryair=self.rho_dryair,
            rho_totair=self.rho_totair,
            cov_w_T=self.cov_w_T,
            N=self.N,
        )

    def common_units_labels(self):
        return dict(
            T="C",
            P="kPa",
            Pvap="kPa",
            ustar="m/s",
            wind_w="m/s",
            var_w="(m/s)^2",
            rho_vapor="g/m^3",
            rho_co2="mg/m^3",
            var_vapor="(g/m^3)^2",
            var_co2="(mg/m^3)^2",
            corr_q_c="",
            cov_w_q="g/m^2/s",
            fc_ov_fq="mg/g",
            sigc_ov_sigq="mg/g",
            H="W/m^2",
            cov_w_c="mg/m^2/s",
            rho_dryair="kg/m^3",
            rho_totair="kg/m^3",
            cov_w_T="C m/s",
            N="",
        )
```

---

### Summary of Changes:
- Replaced `@attr.s` with `@dataclass`.
- Replaced `attr.ib` with standard `dataclasses` field definitions.
- Removed `attrs` import and added `dataclasses` import.
- No changes were made to the logic or structure of the code.