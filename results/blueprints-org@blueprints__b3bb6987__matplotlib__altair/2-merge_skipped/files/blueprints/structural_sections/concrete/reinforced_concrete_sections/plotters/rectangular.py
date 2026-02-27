"""Plotter for Reinforced Rectangular Cross-Sections."""

# ruff: noqa: PLR0913, F821
from typing import TypeVar

import altair as alt
import pandas as pd
from shapely import Point

from blueprints.structural_sections.concrete.rebar import Rebar

T = TypeVar("T", bound="RectangularReinforcedCrossSection")  # type: ignore[name-defined]

RCS_CROSS_SECTION_COLOR = "#d3d3d3"  # Light gray
STIRRUP_COLOR = "#696969"  # Dim gray
REBAR_COLOR = "#b8410e"  # Reddish-brown


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
        self.chart: alt.Chart | None = None

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
        axes_i: int = 0,
    ) -> alt.Chart:
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
        axes_i: int
            Index of the axes to plot on. Default is 0.

        Returns
        -------
        alt.Chart
            Altair chart.
        """
        # Create the base chart
        base_chart = self._add_rectangle()

        # Add center lines
        center_lines = self._add_center_lines()

        # Add stirrups
        stirrups = self._add_stirrups()

        # Add longitudinal rebars
        rebars = self._add_longitudinal_rebars()

        # Combine all layers
        self.chart = base_chart + center_lines + stirrups + rebars

        # Add title
    def _add_rectangle(
        self,
        edge_color: str = "black",
        axes_i: int = 0,
    ) -> mplpatches.Rectangle:
        """Adds a rectangle to the plot.

        Parameters
        ----------
        edge_color: str
            Color of the edge of the rectangle. Use any matplotlib color.
        axes_i: int
            Index of the axes to plot on. Default is 0.
        """
        patch = mplpatches.Rectangle(
            xy=(-self.cross_section.width / 2, -self.cross_section.height / 2),
            width=self.cross_section.width,
            height=self.cross_section.height,
            edgecolor=edge_color,
            facecolor=RCS_CROSS_SECTION_COLOR,
            fill=True,
            lw=1,
        )
        self.axes[axes_i].add_patch(patch)
        return patch

    def _add_center_lines(self, axes_i: int = 0, style: dict[str, float | str] | None = None) -> None:
        """Adds center lines to the plot.

        Parameters
        ----------
        axes_i: int
            Index of the axes to plot on. Default is 0.
        style: dict[str, float]
            Style of the center lines. Check matplotlib documentation for more information (Annotation-arrowprops).
        """
        default_style = {"arrowstyle": "-", "linewidth": 0.8, "color": "gray", "linestyle": "dashdot"}
        if style:
            default_style.update(style)
        offset_center_line = 1.05
        self.axes[axes_i].annotate(
            text="z",
            xy=(0, (-self.cross_section.height / 2) * offset_center_line),
            xytext=(0, (self.cross_section.height / 2) * offset_center_line),
            arrowprops=default_style,
            verticalalignment="bottom",
            horizontalalignment="center",
        )
        self.axes[axes_i].annotate(
            text="y",
            xy=((self.cross_section.width / 2) * offset_center_line, 0),
            xytext=(-(self.cross_section.width / 2) * offset_center_line, 0),
            arrowprops=default_style,
            verticalalignment="center",
            horizontalalignment="right",
        )

    def _add_dimension_lines(
        self,
        axes_i: int = 0,
        style: mplpatches.ArrowStyle | None = None,
        offset_line_width: float = 1.25,
        offset_line_height: float = 1.2,
        custom_text_width: str | None = None,
        custom_text_height: str | None = None,
        font_size_dimension: float = 12.0,
    ) -> None:
        """Adds dimension lines to the plot.

        Parameters
        ----------
        axes_i: int
            Index of the axes to plot on. Default is 0.
        style: dict[str, float]
            Style of the dimension lines. Check matplotlib documentation for more information (Annotation-arrowprops).
        offset_line_width: float
            Offset of the width line.
        offset_line_height: float
            Offset of the height line.
        custom_text_width: str
            Custom text for the width dimension. Replaces the width of the cross-section with the custom text.
        custom_text_height: str
            Custom text for the height dimension. Replaces the height of the cross-section with the custom text.
        font_size_dimension: float
            Font size of the dimensions.
        """
        # add the width dimension line
        diameter_line_style = {
            "arrowstyle": style or mplpatches.ArrowStyle(stylename="<->", head_length=0.5, head_width=0.5),
        }
        offset_width = (-self.cross_section.height / 2) * offset_line_width
        self.axes[axes_i].annotate(
            text="",
            xy=(-self.cross_section.width / 2, offset_width),
            xytext=(self.cross_section.width / 2, offset_width),
            verticalalignment="center",
            horizontalalignment="center",
            arrowprops=diameter_line_style,
            annotation_clip=False,
        )
        self.axes[axes_i].text(
            s=custom_text_width or f"{self.cross_section.width:.0f} mm",
            x=0,
            y=offset_width,
            verticalalignment="bottom",
            horizontalalignment="center",
            fontsize=font_size_dimension,
        )

        # add the height dimension line
        offset_height = (-self.cross_section.width / 2) * offset_line_height
        self.axes[axes_i].annotate(
            text="",
            xy=(offset_height, self.cross_section.height / 2),
            xytext=(offset_height, -self.cross_section.height / 2),
            verticalalignment="center",
            horizontalalignment="center",
            arrowprops=diameter_line_style,
            rotation=90,
            annotation_clip=False,
        )
        self.axes[axes_i].text(
            s=custom_text_height or f"{self.cross_section.height:.0f} mm",
            x=offset_height,
            y=0,
            verticalalignment="center",
            horizontalalignment="right",
            fontsize=font_size_dimension,
            rotation=90,
        )

    def _add_stirrups(
        self,
        axes_i: int = 0,
    ) -> None:
        """Adds stirrups to the plot.

        Parameters
        ----------
        axes_i: int
            Index of the axes to plot on. Default is 0.
        """
        for stirrup in self.cross_section.stirrups:
            left_bottom = Point(stirrup.geometry.exterior.coords[0])  # left bottom point of the stirrup (center line)
            self.axes[axes_i].add_patch(
                mplpatches.Rectangle(
                    xy=(left_bottom.x - stirrup.diameter / 2, left_bottom.y - stirrup.diameter / 2),
                    width=stirrup.ctc_distance_legs + stirrup.diameter,
                    height=self.cross_section.height - self.cross_section.covers.upper - self.cross_section.covers.lower,
                    facecolor=STIRRUP_COLOR,
                    fill=True,
                )
            )
            self.axes[axes_i].add_patch(
                mplpatches.Rectangle(
                    xy=(left_bottom.x + stirrup.diameter / 2, left_bottom.y + stirrup.diameter / 2),
                    width=stirrup.ctc_distance_legs - stirrup.diameter,
                    height=self.cross_section.height - self.cross_section.covers.upper - self.cross_section.covers.lower - 2 * stirrup.diameter,
                    facecolor=RCS_CROSS_SECTION_COLOR,
                    fill=True,
        if title:
            self.chart = self.chart.properties(
                title=alt.TitleParams(
                    text=title,
                    fontSize=font_size_title,
                )
            )

        if show:
            self.chart.show()  # pragma: no cover

        return self.chart

    def _add_rectangle(self) -> alt.Chart:
        """Adds a rectangle to the plot."""
        data = pd.DataFrame(
            {
                "x": [-self.cross_section.width / 2],
                "y": [-self.cross_section.height / 2],
                "width": [self.cross_section.width],
                "height": [self.cross_section.height],
            }
        )
        return alt.Chart(data).mark_rect(
            color=RCS_CROSS_SECTION_COLOR,
            stroke="black",
        ).encode(
            x="x:Q",
            y="y:Q",
            x2=alt.datum("x + width"),
            y2=alt.datum("y + height"),
        )

    def _add_center_lines(self) -> alt.Chart:
        """Adds center lines to the plot."""
        data = pd.DataFrame(
            {
                "x": [0, 0, -self.cross_section.width / 2, self.cross_section.width / 2],
                "y": [-self.cross_section.height / 2, self.cross_section.height / 2, 0, 0],
                "line_group": ["vertical", "vertical", "horizontal", "horizontal"],
            }
        )
        return alt.Chart(data).mark_line(
            strokeDash=[4, 4],
            color="gray",
        ).encode(
            x="x:Q",
            y="y:Q",
            detail="line_group:N",
        )

    def _add_stirrups(self) -> alt.Chart:
        """Adds stirrups to the plot."""
        stirrup_data = []
        for stirrup in self.cross_section.stirrups:
            left_bottom = Point(stirrup.geometry.exterior.coords[0])
            stirrup_data.append(
                {
                    "x": left_bottom.x,
                    "y": left_bottom.y,
                    "width": stirrup.ctc_distance_legs,
                    "height": self.cross_section.height - self.cross_section.covers.upper - self.cross_section.covers.lower,
                }
            )
        data = pd.DataFrame(stirrup_data)
        return alt.Chart(data).mark_rect(
            color=STIRRUP_COLOR,
        ).encode(
            x="x:Q",
            y="y:Q",
            x2=alt.datum("x + width"),
            y2=alt.datum("y + height"),
        )

    def _add_longitudinal_rebars(self) -> alt.Chart:
        """Adds longitudinal rebars to the plot."""
        rebar_data = [
            {"x": rebar.x, "y": rebar.y, "radius": rebar.radius}
            for rebar in self.cross_section.longitudinal_rebars
        ]
        data = pd.DataFrame(rebar_data)
        return alt.Chart(data).mark_point(
            filled=True,
            color=REBAR_COLOR,
        ).encode(
            x="x:Q",
            y="y:Q",
            size=alt.Size("radius:Q", legend=None),
        )