from typing import Literal, Any, Optional, Union

import plotly.graph_objects as go
import numpy

PlotlyColor = Any
"""Type: New type to represent a plotly color, simply an alias of Any"""


def plot_truss(
    truss,
    starting_shape: Optional[Union[Literal["fos", "force"], PlotlyColor]] = "k",
    deflected_shape: Optional[Union[Literal["fos", "force"], PlotlyColor]] = None,
    exaggeration_factor: float = 10,
    fos_threshold: float = 1.0,
) -> go.Figure:
    """Plot the truss.

    Parameters
    ----------
    truss: Truss
        The truss to plot.
    starting_shape: None or "fos" or "force" or PlotlyColor, default="k"
        How to show the starting shape. If None, the starting shape is not shown. If "fos", the members are colored
        green if the factor of safety is above the threshold and red if it is below. If "force", the members are colored
        according to the force in the member. If a color, the members are colored that color.
    deflected_shape:  None or "fos" or "force" or PlotlyColor, default = None
        How to show the deflected shape. If None, the starting shape is not shown. If "fos", the members are colored
        green if the factor of safety is above the threshold and red if it is below. If "force", the members are colored
        according to the force in the member. If a color, the members are colored that color.
    exaggeration_factor: float, default=10
        The factor by which to exaggerate the deflected shape.
    fos_threshold: float, default=1.0
        The threshold for the factor of safety. If the factor of safety is below this value, the member is colored red.

    Returns
    -------
    Figure
        A plotly figure containing the truss
    """

    fig = go.Figure()

    scaler: float = numpy.max(numpy.abs([member.force for member in truss.members]))

    # Define a manual colormap for "force"
    def force_colormap(value):
        # Normalize value to [0, 1]
        normalized_value = (value / (2 * scaler)) + 0.5
        # Interpolate between red, gray, and blue
        if normalized_value <= 0.5:
            return f"rgb({255 * (1 - 2 * normalized_value)}, 0, {255 * 2 * normalized_value})"
        else:
            return f"rgb(0, {255 * (2 * (normalized_value - 0.5))}, {255 * (1 - 2 * (normalized_value - 0.5))})"

    # Plot starting shape
    for member in truss.members:
        if starting_shape == "fos":
            color = (
                "green"
                if numpy.min([member.fos_buckling, member.fos_yielding]) > fos_threshold
                else "red"
            )
        elif starting_shape == "force":
            color = force_colormap(member.force)
        elif starting_shape is None:
            break
        else:
            color = starting_shape
        fig.add_trace(
            go.Scatter(
                x=[member.begin_joint.coordinates[0], member.end_joint.coordinates[0]],
                y=[member.begin_joint.coordinates[1], member.end_joint.coordinates[1]],
                mode="lines",
                line=dict(color=color),
                showlegend=False,
            )
        )

    # Plot deflected shape
    for member in truss.members:
        if deflected_shape == "fos":
            color = (
                "green"
                if numpy.min([member.fos_buckling, member.fos_yielding]) > fos_threshold
                else "red"
            )
        elif deflected_shape == "force":
            color = force_colormap(member.force)
        elif deflected_shape is None:
            break
        else:
            color = deflected_shape
        fig.add_trace(
            go.Scatter(
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
                mode="lines",
                line=dict(color=color),
                showlegend=False,
            )
        )

    # Set axis properties
    fig.update_layout(
        xaxis=dict(scaleanchor="y", showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        template="plotly_white",
    )

    return fig
