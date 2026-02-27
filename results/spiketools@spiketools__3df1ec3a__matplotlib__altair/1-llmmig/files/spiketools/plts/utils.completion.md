### Explanation of Changes
The original code uses `matplotlib` for plotting and grid management. To migrate to `altair`, the following changes were made:
1. **Removed `matplotlib` Imports**: All `matplotlib` imports (`pyplot`, `gridspec`, etc.) were removed.
2. **Replaced Plotting Functions**: Functions like `check_ax`, `make_axes`, `make_grid`, and `get_grid_subplot` were rewritten to use `altair` constructs.
3. **Altair-Specific Constructs**: `altair.Chart` and related methods were used to create plots. Since `altair` does not have direct equivalents for some `matplotlib` features (e.g., grid layouts), the code was adapted to use `altair`'s declarative charting approach.
4. **Removed `plt.subplots_adjust` and Similar Calls**: These are specific to `matplotlib` and do not have direct equivalents in `altair`.
5. **Saving Figures**: `altair` charts are saved using the `save` method, which supports formats like `.html` and `.png`.

Below is the modified code using `altair`:

---

### Modified Code
```python
"""Plot utilities."""

import math
from functools import wraps
from os.path import join as pjoin

import altair as alt

###################################################################################################
###################################################################################################

def check_chart(chart=None, data=None, return_current=False):
    """Check whether a chart object is defined, and define or return a new chart if not.

    Parameters
    ----------
    chart : alt.Chart or None
        Chart object to check if is defined.
    data : pandas.DataFrame or None
        Data to use for the chart, if creating a new one.
    return_current : bool, optional, default: False
        Whether to return the current chart, if chart is not defined.
        If False, creates a new chart instead.

    Returns
    -------
    chart : alt.Chart
        Chart object to use.
    """

    if not chart:
        if return_current:
            raise ValueError("Altair does not support a 'current chart' concept.")
        else:
            if data is None:
                raise ValueError("Data must be provided to create a new chart.")
            chart = alt.Chart(data)

    return chart


def get_kwargs(kwargs, select):
    """Get keyword arguments.

    Parameters
    ----------
    kwargs : dict
        Keyword arguments to extract from.
    select : list of str
        The arguments to extract.

    Returns
    -------
    setters : dict
        Selected keyword arguments.
    """

    setters = {arg: kwargs.pop(arg, None) for arg in select}
    setters = {arg: value for arg, value in setters.items() if value is not None}

    return setters


def get_attr_kwargs(kwargs, attr):
    """Get keyword arguments related to a particular attribute.

    Parameters
    ----------
    kwargs : dict
        Plotting related keyword arguments.
    attr : str
        The attribute to select related arguments.

    Returns
    -------
    attr_kwargs : dict
        Selected keyword arguments, related to the given attribute.
    """

    labels = [key for key in kwargs.keys() if attr in key]
    attr_kwargs = {label.split('_')[1]: kwargs.pop(label) for label in labels}

    return attr_kwargs


def savefig(func):
    """Decorator function to save out figures."""

    @wraps(func)
    def decorated(*args, **kwargs):

        # Grab file name and path arguments, if they are in kwargs
        file_name = kwargs.pop('file_name', None)
        file_path = kwargs.pop('file_path', None)

        # Check for an explicit argument for whether to save figure or not
        #   Defaults to saving when file name given (since bool(str)->True; bool(None)->False)
        save_fig = kwargs.pop('save_fig', bool(file_name))

        # Check and collect any other plot keywords
        save_kwargs = kwargs.pop('save_kwargs', {})

        func(*args, **kwargs)

        if save_fig:
            save_figure(file_name, file_path, **save_kwargs)

    return decorated


def save_figure(file_name, file_path=None, **save_kwargs):
    """Save out a figure.

    Parameters
    ----------
    file_name : str
        File name for the figure file to save out.
    file_path : str or Path
        Path for where to save out the figure to.
    save_kwargs
        Additional arguments to pass into the save function.
    """

    full_path = pjoin(file_path, file_name) if file_path else file_name
    if full_path.endswith('.html'):
        chart.save(full_path)
    elif full_path.endswith('.png'):
        chart.save(full_path, scale_factor=save_kwargs.get('scale_factor', 2))
    else:
        raise ValueError("Unsupported file format. Use '.html' or '.png'.")


def make_axes(n_axes, n_cols=5, figsize=None, row_size=4, col_size=3.6,
              title=None, **alt_kwargs):
    """Make a subplot with multiple axes.

    Parameters
    ----------
    n_axes : int
        The total number of axes to create in the figure.
    n_cols : int, optional, default: 5
        The number of columns in the figure.
    figsize : tuple of float, optional
        Size to make the overall figure.
        If not given, is estimated from the number of axes.
    row_size, col_size : float, optional
        The size to use per row / column.
        Only used if `figsize` is None.
    title : str, optional
        A title to add to the figure.
    **alt_kwargs
        Extra arguments to pass to `altair` charts.

    Returns
    -------
    charts : list of alt.Chart
        Collection of chart objects.
    """

    n_rows = math.ceil(n_axes / n_cols)

    charts = []
    for _ in range(n_axes):
        chart = alt.Chart().mark_point(**alt_kwargs)
        charts.append(chart)

    if title:
        print(f"Title: {title}")  # Altair does not support global titles directly.

    return charts


def make_grid(nrows, ncols, title=None, **alt_kwargs):
    """Create a plot grid.

    Parameters
    ----------
    nrows, ncols : int
        The number of rows and columns to add to the data.
    title : str, optional
        A title to add to the figure.
    alt_kwargs
        Additional arguments to pass into the plot function.
    """

    charts = []
    for _ in range(nrows * ncols):
        chart = alt.Chart().mark_point(**alt_kwargs)
        charts.append(chart)

    if title:
        print(f"Title: {title}")  # Altair does not support global titles directly.

    return charts


def get_grid_subplot(grid, row, col, **alt_kwargs):
    """Get a subplot section from a grid layout.

    Parameters
    ----------
    grid : list of alt.Chart
        A predefined plot grid layout.
    row, col : int
        The row(s) and column(s) in which to place the subplot.
    alt_kwargs
        Additional arguments to pass into the plot function.

    Returns
    -------
    alt.Chart
        Subplot chart.
    """

    index = row * len(grid[0]) + col
    return grid[index]
```

---

### Notes
- `altair` does not have direct equivalents for some `matplotlib` features, such as grid layouts or subplot adjustments. The code was adapted to use `altair`'s declarative approach.
- Global titles are not directly supported in `altair`. A workaround (e.g., printing the title) was used.
- Saving charts in `altair` requires specifying the format (`.html` or `.png`).