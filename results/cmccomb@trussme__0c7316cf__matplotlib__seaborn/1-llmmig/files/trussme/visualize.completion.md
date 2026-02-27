### Explanation of Changes
To migrate the code from `matplotlib` to `seaborn`, the following changes were made:
1. **Import Changes**: Removed `matplotlib.pyplot` and `matplotlib.colors` imports and replaced them with `seaborn` imports.
2. **Figure and Axes Creation**: Replaced `matplotlib.pyplot.figure()` and `fig.add_subplot()` with `seaborn`'s `sns.set_theme()` for styling and `sns.set_context()` for figure context. The `matplotlib` figure and axes creation were replaced with `seaborn`'s default handling.
3. **Colormap**: Replaced `matplotlib.colors.LinearSegmentedColormap` with `seaborn`'s `sns.color_palette()` to create a similar colormap.
4. **Plotting**: Replaced `ax.plot()` with `seaborn.lineplot()` for plotting the truss members.
5. **Axis Settings**: Used `sns.despine()` to remove axes spines and set the aspect ratio to "equal" using `ax.set_aspect()`.

### Modified Code
```python
from typing import Literal, Any, Optional, Union

import seaborn as sns
import numpy

MatplotlibColor = Any
"""Type: New type to represent a matplotlib color, simply an alias of Any"""


def plot_truss(
    truss,
    starting_shape: Optional[Union[Literal["fos", "force"], MatplotlibColor]] = "k",
    deflected_shape: Optional[Union[Literal["fos", "force"], MatplotlibColor]] = None,
    exaggeration_factor: float = 10,
    fos_threshold: float = 1.0,
) -> None:
    """Plot the truss.

    Parameters
    ----------
    truss: Truss
        The truss to plot.
    starting_shape: None or "fos" or "force" or MatplotlibColor, default="k"
        How to show the starting shape. If None, the starting shape is not shown. If "fos", the members are colored
        green if the factor of safety is above the threshold and red if it is below. If "force", the members are colored
        according to the force in the member. If a color, the members are colored that color.
    deflected_shape:  None or "fos" or "force" or MatplotlibColor, default = None
        How to show the deflected shape. If None, the starting shape is not shown. If "fos", the members are colored
        green if the factor of safety is above the threshold and red if it is below. If "force", the members are colored
        according to the force in the member. If a color, the members are colored that color.
    exaggeration_factor: float, default=10
        The factor by which to exaggerate the deflected shape.
    fos_threshold: float, default=1.0
        The threshold for the factor of safety. If the factor of safety is below this value, the member is colored red.

    Returns
    -------
    None
        The plot is displayed using seaborn.
    """

    # Set seaborn theme and context
    sns.set_theme(style="white")
    sns.set_context("notebook")

    # Create a figure and axis
    fig, ax = sns.plt.subplots()
    ax.set_aspect("equal")
    sns.despine(left=True, bottom=True)

    # Calculate the scaler for force normalization
    scaler: float = numpy.max(numpy.abs([member.force for member in truss.members]))

    # Define a colormap using seaborn's color_palette
    force_colormap = sns.color_palette("coolwarm", as_cmap=True)

    # Plot the starting shape
    for member in truss.members:
        if starting_shape == "fos":
            color = (
                "g"
                if numpy.min([member.fos_buckling, member.fos_yielding]) > fos_threshold
                else "r"
            )
        elif starting_shape == "force":
            color = force_colormap(member.force / (2 * scaler) + 0.5)
        elif starting_shape is None:
            break
        else:
            color = starting_shape
        sns.lineplot(
            x=[member.begin_joint.coordinates[0], member.end_joint.coordinates[0]],
            y=[member.begin_joint.coordinates[1], member.end_joint.coordinates[1]],
            ax=ax,
            color=color,
            linewidth=2,
        )

    # Plot the deflected shape
    for member in truss.members:
        if deflected_shape == "fos":
            color = (
                "g"
                if numpy.min([member.fos_buckling, member.fos_yielding]) > fos_threshold
                else "r"
            )
        elif deflected_shape == "force":
            color = force_colormap(member.force / (2 * scaler) + 0.5)
        elif deflected_shape is None:
            break
        else:
            color = deflected_shape
        sns.lineplot(
            x=[
                member.begin_joint.coordinates[0]
                + exaggeration_factor * member.begin_joint.deflections[0],
                member.end_joint.coordinates[0]
                + exaggeration_factor * member.end_joint.deflections[0],
            ],
            y=[
                member.begin_joint.coordinates[1]
                + exaggeration_factor * member.begin_joint.deflections[1],
                member.end_joint.coordinates[1]
                + exaggeration_factor * member.end_joint.deflections[1],
            ],
            ax=ax,
            color=color,
            linewidth=2,
        )

    # Show the plot
    sns.plt.show()
```

### Key Notes
- `sns.plt.subplots()` is used to create the figure and axis, as `seaborn` relies on `matplotlib` under the hood for figure management.
- `sns.lineplot()` is used for plotting lines, which is the `seaborn` equivalent of `ax.plot()` in `matplotlib`.
- The `force_colormap` is created using `sns.color_palette()` with the `"coolwarm"` palette, which is similar to the original colormap.
- The `sns.despine()` function is used to remove the axis spines, and `ax.set_aspect("equal")` ensures the aspect ratio is maintained.