To migrate the provided code from using the `matplotlib` library to the `plotly` library, several key changes were made:

1. **Import Statements**: The import statements were updated to include `plotly.graph_objects` instead of `matplotlib.pyplot` and `matplotlib.gridspec`.
2. **Figure and Axes Creation**: The way figures and axes are created changed significantly. In `plotly`, figures are created using `plotly.graph_objects.Figure()` and subplots are handled differently compared to `matplotlib`.
3. **Saving Figures**: The method for saving figures is different in `plotly`. Instead of `plt.savefig()`, we use `plotly.io.write_image()` to save figures.
4. **Subplot Management**: The management of subplots and layout is handled using `plotly.subplots.make_subplots()` instead of `plt.subplots()`.
5. **Title and Layout Adjustments**: Titles and layout adjustments are done through the `update_layout()` method in `plotly`.

Here is the modified code after migrating to `plotly`:

```python
"""Plot utilities."""

import math
from functools import wraps
from os.path import join as pjoin

import plotly.graph_objects as go
from plotly.subplots import make_subplots

###################################################################################################
###################################################################################################

def check_ax(ax, figsize=None, return_current=False):
    """Check whether a figure axes object is defined, and define or return current axis if not.

    Parameters
    ----------
    ax : plotly.graph_objects.Figure or None
        Axes object to check if is defined.
    figsize : tuple of float, optional
        Size to make the axis.
    return_current : bool, optional, default: False
        Whether to return the current axis, if axis is not defined.
        If False, creates a new plot axis instead.

    Returns
    -------
    ax : plotly.graph_objects.Figure
        Figure object to use.
    """

    if not ax:
        ax = go.Figure()

    return ax


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

    setters = {arg : kwargs.pop(arg, None) for arg in select}
    setters = {arg : value for arg, value in setters.items() if value is not None}

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
    attr_kwargs = {label.split('_')[1] : kwargs.pop(label) for label in labels}

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

        # Check and collect whether to close the plot
        close = kwargs.pop('close', False)

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
    go.Figure().write_image(full_path, **save_kwargs)


def make_axes(n_axes, n_cols=5, figsize=None, row_size=4, col_size=3.6,
              wspace=None, hspace=None, title=None, **plt_kwargs):
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
    wspace, hspace : float, optional
        Spacing parameters for between subplots.
        These get passed into `plt.subplots_adjust`.
    title : str, optional
        A title to add to the figure.
    **plt_kwargs
        Extra arguments to pass to `make_subplots`.

    Returns
    -------
    axes : list of plotly.graph_objects.Figure
        Collection of axes objects.
    """

    n_rows = math.ceil(n_axes / n_cols)

    if not figsize:
        figsize = (n_cols * col_size, n_rows * row_size)

    title_kwargs = get_attr_kwargs(plt_kwargs, 'title')

    fig = make_subplots(rows=n_rows, cols=n_cols, **plt_kwargs)

    if title:
        fig.update_layout(title=title,
                          title_font=dict(size=title_kwargs.pop('fontsize', 24)),
                          title_y=title_kwargs.pop('y', 0.95))

    return fig


def make_grid(nrows, ncols, title=None, **plt_kwargs):
    """Create a plot grid.

    Parameters
    ----------
    nrows, ncols : int
        The number of rows and columns to add to the data.
    title : str, optional
        A title to add to the figure.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    title_kwargs = get_attr_kwargs(plt_kwargs, 'title')

    fig = go.Figure()

    if title:
        fig.update_layout(title=title,
                          title_font=dict(size=title_kwargs.pop('fontsize', 24)),
                          title_y=title_kwargs.pop('y', 0.95))

    return fig


def get_grid_subplot(grid, row, col, **plt_kwargs):
    """Get a subplot section from a grid layout.

    Parameters
    ----------
    grid : plotly.graph_objects.Figure
        A predefined plot grid layout.
    row, col : int or slice
        The row(s) and column(s) in which to place the subplot.
    plt_kwargs
        Additional arguments to pass into the plot function.

    Returns
    -------
    plotly.graph_objects.Figure
        Subplot axis.
    """

    return grid.add_trace(go.Scatter(), row=row, col=col, **plt_kwargs)

```

This code now uses `plotly` for creating and managing plots, while maintaining the original structure and functionality as closely as possible.