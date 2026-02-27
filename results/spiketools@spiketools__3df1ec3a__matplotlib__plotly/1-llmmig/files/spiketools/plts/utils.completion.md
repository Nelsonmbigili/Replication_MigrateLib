### Explanation of Changes
To migrate the code from `matplotlib` to `plotly`, the following changes were made:
1. **Import Changes**: Removed `matplotlib` imports (`pyplot` and `gridspec`) and replaced them with `plotly.graph_objects` (`go`) and `plotly.subplots` for subplot handling.
2. **Figure and Axes Handling**: Replaced `matplotlib`'s `plt.subplots` and `plt.gca` with `plotly.subplots.make_subplots` and `go.Figure` for creating and managing figures and axes.
3. **GridSpec Replacement**: Replaced `matplotlib.gridspec.GridSpec` with `plotly.subplots.make_subplots` for grid-based layouts.
4. **Saving Figures**: Replaced `plt.savefig` with `plotly.io.write_image` for saving figures.
5. **Plot Adjustments**: Removed `plt.subplots_adjust` and replaced it with `plotly`'s layout adjustments (e.g., `update_layout`).
6. **Titles and Layouts**: Used `update_layout` to handle figure titles and spacing instead of `plt.suptitle`.

Below is the modified code:

---

### Modified Code
```python
"""Plot utilities."""

import math
from functools import wraps
from os.path import join as pjoin

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

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
        Figure axes object to use.
    """

    if not ax:
        if return_current:
            ax = go.Figure()
        else:
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
        save_kwargs.setdefault('format', 'png')

        # Check and collect whether to close the plot
        close = kwargs.pop('close', False)

        fig = func(*args, **kwargs)

        if save_fig:
            save_figure(fig, file_name, file_path, close, **save_kwargs)

    return decorated


def save_figure(fig, file_name, file_path=None, close=False, **save_kwargs):
    """Save out a figure.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        The figure object to save.
    file_name : str
        File name for the figure file to save out.
    file_path : str or Path
        Path for where to save out the figure to.
    close : bool, optional, default: False
        Whether to close the plot after saving.
    save_kwargs
        Additional arguments to pass into the save function.
    """

    full_path = pjoin(file_path, file_name) if file_path else file_name
    pio.write_image(fig, full_path, **save_kwargs)

    if close:
        del fig


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
        These get passed into `update_layout`.
    title : str, optional
        A title to add to the figure.
    **plt_kwargs
        Extra arguments to pass to `make_subplots`.

    Returns
    -------
    fig : plotly.graph_objects.Figure
        Figure object with subplots.
    """

    n_rows = math.ceil(n_axes / n_cols)

    if not figsize:
        figsize = (n_cols * col_size, n_rows * row_size)

    title_kwargs = get_attr_kwargs(plt_kwargs, 'title')

    fig = make_subplots(rows=n_rows, cols=n_cols, **plt_kwargs)

    if title:
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=title_kwargs.pop('fontsize', 24)),
                y=title_kwargs.pop('y', 0.95)
            )
        )

    fig.update_layout(
        width=figsize[0] * 100,  # Convert to pixels
        height=figsize[1] * 100,  # Convert to pixels
        margin=dict(t=50, b=50, l=50, r=50),
    )

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

    fig = make_subplots(rows=nrows, cols=ncols, **plt_kwargs)

    if title:
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=title_kwargs.pop('fontsize', 24)),
                y=title_kwargs.pop('y', 0.95)
            )
        )

    return fig


def get_grid_subplot(grid, row, col, **plt_kwargs):
    """Get a subplot section from a grid layout.

    Parameters
    ----------
    grid : plotly.graph_objects.Figure
        A predefined plot grid layout.
    row, col : int
        The row and column in which to place the subplot.
    plt_kwargs
        Additional arguments to pass into the plot function.

    Returns
    -------
    plotly.graph_objects.Figure
        Subplot axis.
    """

    # Plotly does not have a direct equivalent for this functionality.
    # Instead, we return the figure object and expect the user to add traces to the specified subplot.
    return grid
```

---

### Notes
- `plotly` does not have a direct equivalent for `matplotlib`'s `GridSpec` or `subplot` slicing. Instead, subplots are managed using `make_subplots`, and traces are added to specific rows and columns.
- The `savefig` decorator now uses `plotly.io.write_image` to save figures. Ensure `kaleido` or `orca` is installed for saving images.