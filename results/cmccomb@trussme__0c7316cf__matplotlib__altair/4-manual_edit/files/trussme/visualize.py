from typing import Literal, Any, Optional, Union
import pandas as pd
import altair as alt
import numpy as np

MatplotlibColor = Any
"""Type: New type to represent a matplotlib color, simply an alias of Any"""


def plot_truss(
    truss,
    starting_shape: Optional[Union[Literal["fos", "force"], MatplotlibColor]] = "k",
    deflected_shape: Optional[Union[Literal["fos", "force"], MatplotlibColor]] = None,
    exaggeration_factor: float = 10,
    fos_threshold: float = 1.0,
) -> alt.Chart:
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
    Chart
        An Altair chart containing the truss
    """

    # Prepare data for starting shape
    scaler: float = np.max(np.abs([member.force for member in truss.members]))
    starting_data = []
    for member in truss.members:
        if starting_shape == "fos":
            color = (
                "green"
                if np.min([member.fos_buckling, member.fos_yielding]) > fos_threshold
                else "red"
            )
        elif starting_shape == "force":
            normalized_force = member.force / (2 * scaler) + 0.5
            color = f"rgb({255 * (1 - normalized_force)}, {255 * normalized_force}, 255)"
        elif starting_shape is None:
            continue
        else:
            color = starting_shape

        starting_data.append({
            "x": member.begin_joint.coordinates[0],
            "y": member.begin_joint.coordinates[1],
            "x2": member.end_joint.coordinates[0],
            "y2": member.end_joint.coordinates[1],
            "color": color,
        })

    # Prepare data for deflected shape
    deflected_data = []
    for member in truss.members:
        if deflected_shape == "fos":
            color = (
                "green"
                if np.min([member.fos_buckling, member.fos_yielding]) > fos_threshold
                else "red"
            )
        elif deflected_shape == "force":
            normalized_force = member.force / (2 * scaler) + 0.5
            color = f"rgb({255 * (1 - normalized_force)}, {255 * normalized_force}, 255)"
        elif deflected_shape is None:
            continue
        else:
            color = deflected_shape

        deflected_data.append({
            "x": member.begin_joint.coordinates[0]
            + exaggeration_factor * member.begin_joint.deflections[0],
            "y": member.begin_joint.coordinates[1]
            + exaggeration_factor * member.begin_joint.deflections[1],
            "x2": member.end_joint.coordinates[0]
            + exaggeration_factor * member.end_joint.deflections[0],
            "y2": member.end_joint.coordinates[1]
            + exaggeration_factor * member.end_joint.deflections[1],
            "color": color,
        })

    # Convert data to DataFrame
    starting_df = pd.DataFrame(starting_data)
    deflected_df = pd.DataFrame(deflected_data)

    # Create Altair charts
    starting_chart = alt.Chart(starting_df).mark_line().encode(
        x="x:Q",
        y="y:Q",
        x2="x2:Q",
        y2="y2:Q",
        color=alt.Color("color:N", scale=None),
    )

    deflected_chart = alt.Chart(deflected_df).mark_line().encode(
        x="x:Q",
        y="y:Q",
        x2="x2:Q",
        y2="y2:Q",
        color=alt.Color("color:N", scale=None),
    )

    # Combine charts
    combined_chart = starting_chart + deflected_chart
    combined_chart = combined_chart.configure_axis(
        grid=False, domain=False, labels=False, ticks=False
    ).properties(width=600, height=400)

    return combined_chart