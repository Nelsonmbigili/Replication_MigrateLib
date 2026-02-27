import os
import warnings
from functools import lru_cache
from typing import Optional, Mapping

import numpy as np
import pandas as pd
import altair as alt
from hbutils.string import plural_word
from hbutils.testing import vpip
from scipy import interpolate
from sklearn.cluster import KMeans

from ..log import tb_extract_recursive_logs


@lru_cache()
def _kmeans_support_n_init_auto():
    return vpip('scikit-learn') >= '1.2.0'


def _tb_x_format(x):
    if x < 1e3:
        return f'{x}'
    elif x < 1e6:
        return f'{x / 1e3:.2f}k'
    else:
        return f'{x / 1e6:.2f}M'


def _tb_rplot_single_group(dfs, xname, yname, label, n_samples: Optional[int] = None,
                           lower_bound: Optional[float] = None, upper_bound: Optional[float] = None):
    datas = []
    for d in dfs:
        df = d[[xname, yname]]
        df = df[~df[yname].isna()]
        func = interpolate.UnivariateSpline(df[xname], df[yname], s=0)
        datas.append((df[xname], df[yname], func))

    if lower_bound is None:
        lower_bound = np.min([x.min() for x, _, _ in datas])
    if upper_bound is None:
        upper_bound = np.max([x.max() for x, _, _ in datas])

    all_xs = np.concatenate([x[(x <= upper_bound) & (x >= lower_bound)] for x, _, _ in datas])
    if n_samples is None:
        n_samples = all_xs.shape[0]
    if n_samples > all_xs.shape[0]:
        warnings.warn(f'{plural_word(all_xs.shape[0], "sample")} found in total, '
                      f'n_samples ignored due to the unavailableness of {plural_word(n_samples, "sample")}.')
        n_samples = all_xs.shape[0]

    clu_algo = KMeans(n_samples, n_init='auto' if _kmeans_support_n_init_auto() else 10)
    clu_algo.fit(all_xs[..., None])
    px = np.sort(clu_algo.cluster_centers_.squeeze(-1), kind='heapsort')
    if not np.isclose(px[0], lower_bound):
        px = np.concatenate([np.array([lower_bound]), px])
    if not np.isclose(px[-1], upper_bound):
        px = np.concatenate([px, np.array([upper_bound])])

    fx = []
    fy = []
    for xvalues, _, func in datas:
        x_min, x_max = xvalues.min(), xvalues.max()
        for x in px:
            if x_min <= x <= x_max:
                fx.append(x)
                fy.append(func(x))
    fx = np.array(fx)
    fy = np.array(fy)

    # Combine fx and fy into a DataFrame for Altair
    plot_data = pd.DataFrame({xname: fx, yname: fy, 'label': label})
    return plot_data


def tb_create_range_plots(logdir, xname, yname,
                          label_map: Optional[Mapping[str, str]] = None, n_samples: Optional[int] = None,
                          lower_bound: Optional[float] = 0.0, upper_bound: Optional[float] = None):
    """
    Overview:
        Create Multi-Seed Multi-Algorithm Benchmark Plots with Mean and Standard Deviation.

    :param logdir: Log directory of tensorboard. Nested tensorboard log directories are supported.
    :param xname: Name of x-axis, ``step`` is recommended.
    :param yname: Name of y-axis.
    :param label_map: Mapping of the labels, will be used in legend.
    :param n_samples: Samples of x-axis, default is ``None`` which means just use all the samples.
    :param lower_bound: Lower bound of x-axis. Default is the minimum value of all the experiments' x.
    :param upper_bound: Upper bound of y-axis. Default is the maximum value of all the experiments' x.
    """
    label_map = dict(label_map or {})
    log_data = tb_extract_recursive_logs(logdir)
    log_groups = {}
    for key, data in log_data.items():
        first_seg = key.split(os.path.sep)[0]
        if first_seg not in log_groups:
            log_groups[first_seg] = []
        log_groups[first_seg].append(data)

    all_plot_data = []
    for group_name, dfs in log_groups.items():
        plot_data = _tb_rplot_single_group(
            dfs, xname, yname,
            label=label_map.get(group_name, group_name),
            n_samples=n_samples,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )
        all_plot_data.append(plot_data)

    # Combine all plot data into a single DataFrame
    combined_data = pd.concat(all_plot_data, ignore_index=True)

    # Create the Altair chart
    chart = alt.Chart(combined_data).mark_line().encode(
        x=alt.X(xname, axis=alt.Axis(title=xname, format='.2s')),
        y=alt.Y(yname, axis=alt.Axis(title=yname)),
        color='label:N'
    ).properties(
        title=f'{xname!r} - {yname!r} plot'
    )

    return chart
