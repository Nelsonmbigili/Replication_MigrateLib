### Explanation of Changes:
To migrate the code from `matplotlib` to `plotly`, the following changes were made:
1. **Library Imports**: Replaced `matplotlib` imports with `plotly.graph_objects` (commonly referred to as `go`).
2. **Figure and Axes**: Replaced `matplotlib`'s `Figure` and `Axes` with `plotly.graph_objects.Figure`.
3. **Shapes and Annotations**: Used `plotly`'s `add_shape` for rectangles, circles, and lines, and `add_annotation` for text and arrows.
4. **Legend**: Used `plotly`'s `layout.annotations` for adding legend text.
5. **Plot Display**: Replaced `plt.show()` with `fig.show()` for rendering the plot.
6. **Styling Adjustments**: Adjusted styles (e.g., colors, line styles) to match `plotly`'s syntax.

Below is the modified code:

---

### Modified Code:
```python
"""Plotter for Reinforced Rectangular Cross-Sections."""

# ruff: noqa: PLR0913, F821
from typing import TypeVar

import plotly.graph_objects as go
from shapely import Point

from blueprints.structural_sections.concrete.rebar import Rebar

T = TypeVar("T", bound="RectangularReinforcedCrossSection")  # type: ignore[name-defined]

RCS_CROSS_SECTION_COLOR = "rgb(211, 211, 211)"  # Light gray
STIRRUP_COLOR = "rgb(105, 105, 105)"  # Dim gray
REBAR_COLOR = "rgb(183, 65, 14)"  # Reddish-brown


class RectangularCrossSectionPlotter:
    """Plotter for Reinforced Rectangular Cross-Sections (RRCS)."""

    def __init__(
        self,
        cross_section: T,
    ) -> None:
        """Initialize the RRCSPlotter.

        Parameters
        ----------
        cross_section: RectangularReinforcedCrossSection
            Reinforced cross-section to plot.
        """
        self.cross_section = cross_section
        self.fig: go.Figure | None = None

    def plot(
        self,
        figsize: tuple[float, float] = (15.0, 8.0),
        title: str | None = None,
        font_size_title: float = 18.0,
        font_size_legend: float = 10.0,
        include_legend: bool = True,
        font_size_dimension: float = 12.0,
        custom_text_legend: str | None = None,
        custom_text_width: str | None = None,
        custom_text_height: str | None = None,
        offset_line_width: float = 1.25,
        offset_line_height: float = 1.2,
        center_line_style: dict[str, float | str] | None = None,
        show: bool = False,
    ) -> go.Figure:
        """Plots the cross-section.

        Parameters
        ----------
        figsize: tuple[float, float]
            Size of the plot window.
        title: str
            Title of the plot.
        font_size_title: float
            Font size of the title.
        font_size_legend: float
            Font size of the legend.
        include_legend: bool
            Include legend in the plot.
        font_size_dimension: float
            Font size of the dimensions.
        custom_text_legend: str
            Custom text for the legend.
        custom_text_width: str
            Custom text for the width dimension. Replaces the width of the cross-section with the custom text.
        custom_text_height: str
            Custom text for the height dimension. Replaces the height of the cross-section with the custom text.
        offset_line_width: float
            Offset of the width line.
        offset_line_height: float
            Offset of the height line.
        center_line_style: dict[str, float | str] | None
            Style of the center lines.
        show: bool
            Show the plot.

        Returns
        -------
        go.Figure
            Plotly figure.
        """
        self.fig = go.Figure()

        # Add rectangle
        self._add_rectangle()

        # Add center lines
        self._add_center_lines(style=center_line_style)

        # Add dimension lines
        self._add_dimension_lines(
            font_size_dimension=font_size_dimension,
            custom_text_height=custom_text_height,
            custom_text_width=custom_text_width,
            offset_line_width=offset_line_width,
            offset_line_height=offset_line_height,
        )

        # Add stirrups
        self._add_stirrups()

        # Add longitudinal rebars
        self._add_longitudinal_rebars()

        # Set layout
        self.fig.update_layout(
            title={"text": title or "", "font": {"size": font_size_title}},
            xaxis={"visible": False},
            yaxis={"visible": False},
            showlegend=False,
            width=figsize[0] * 100,
            height=figsize[1] * 100,
        )

        # Add legend
        if include_legend:
            self._add_legend(custom_legend_text, font_size_legend)

        if show:
            self.fig.show()  # pragma: no cover
        return self.fig

    def _add_rectangle(self) -> None:
        """Adds a rectangle to the plot."""
        self.fig.add_shape(
            type="rect",
            x0=-self.cross_section.width / 2,
            y0=-self.cross_section.height / 2,
            x1=self.cross_section.width / 2,
            y1=self.cross_section.height / 2,
            line=dict(color="black"),
            fillcolor=RCS_CROSS_SECTION_COLOR,
        )

    def _add_center_lines(self, style: dict[str, float | str] | None = None) -> None:
        """Adds center lines to the plot."""
        default_style = {"color": "gray", "dash": "dashdot", "width": 0.8}
        if style:
            default_style.update(style)

        # Vertical center line
        self.fig.add_shape(
            type="line",
            x0=0,
            y0=-self.cross_section.height / 2,
            x1=0,
            y1=self.cross_section.height / 2,
            line=default_style,
        )

        # Horizontal center line
        self.fig.add_shape(
            type="line",
            x0=-self.cross_section.width / 2,
            y0=0,
            x1=self.cross_section.width / 2,
            y1=0,
            line=default_style,
        )

    def _add_dimension_lines(
        self,
        offset_line_width: float = 1.25,
        offset_line_height: float = 1.2,
        custom_text_width: str | None = None,
        custom_text_height: str | None = None,
        font_size_dimension: float = 12.0,
    ) -> None:
        """Adds dimension lines to the plot."""
        # Width dimension line
        offset_width = (-self.cross_section.height / 2) * offset_line_width
        self.fig.add_shape(
            type="line",
            x0=-self.cross_section.width / 2,
            y0=offset_width,
            x1=self.cross_section.width / 2,
            y1=offset_width,
            line=dict(color="black", width=1),
        )
        self.fig.add_annotation(
            text=custom_text_width or f"{self.cross_section.width:.0f} mm",
            x=0,
            y=offset_width,
            showarrow=False,
            font=dict(size=font_size_dimension),
        )

        # Height dimension line
        offset_height = (-self.cross_section.width / 2) * offset_line_height
        self.fig.add_shape(
            type="line",
            x0=offset_height,
            y0=-self.cross_section.height / 2,
            x1=offset_height,
            y1=self.cross_section.height / 2,
            line=dict(color="black", width=1),
        )
        self.fig.add_annotation(
            text=custom_text_height or f"{self.cross_section.height:.0f} mm",
            x=offset_height,
            y=0,
            showarrow=False,
            font=dict(size=font_size_dimension),
            textangle=90,
        )

    def _add_stirrups(self) -> None:
        """Adds stirrups to the plot."""
        for stirrup in self.cross_section.stirrups:
            left_bottom = Point(stirrup.geometry.exterior.coords[0])
            self.fig.add_shape(
                type="rect",
                x0=left_bottom.x - stirrup.diameter / 2,
                y0=left_bottom.y - stirrup.diameter / 2,
                x1=left_bottom.x + stirrup.ctc_distance_legs + stirrup.diameter / 2,
                y1=left_bottom.y + self.cross_section.height - self.cross_section.covers.upper - self.cross_section.covers.lower,
                fillcolor=STIRRUP_COLOR,
            )

    def _add_longitudinal_rebars(self) -> None:
        """Adds longitudinal rebars to the plot."""
        for rebar in self.cross_section.longitudinal_rebars:
            self.fig.add_shape(
                type="circle",
                x0=rebar.x - rebar.radius,
                y0=rebar.y - rebar.radius,
                x1=rebar.x + rebar.radius,
                y1=rebar.y + rebar.radius,
                fillcolor=REBAR_COLOR,
            )

    def _add_legend(self, custom_legend_text: str | None, font_size_legend: float) -> None:
        """Adds the legend to the plot."""
        legend_text = custom_legend_text or self.legend_text()
        self.fig.add_annotation(
            text=legend_text,
            x=self.cross_section.width / 2,
            y=-self.cross_section.height / 2,
            showarrow=False,
            font=dict(size=font_size_legend),
            align="left",
        )
```

This code now uses `plotly` for all plotting functionalities while maintaining the original structure and logic.