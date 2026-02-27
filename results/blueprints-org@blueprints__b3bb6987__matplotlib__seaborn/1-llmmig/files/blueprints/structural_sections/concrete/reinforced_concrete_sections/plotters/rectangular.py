"""Plotter for Reinforced Rectangular Cross-Sections."""

# ruff: noqa: PLR0913, F821
from typing import TypeVar

from matplotlib import patches as mplpatches
from shapely import Point
import seaborn as sns

from blueprints.structural_sections.concrete.rebar import Rebar

T = TypeVar("T", bound="RectangularReinforcedCrossSection")  # type: ignore[name-defined]

RCS_CROSS_SECTION_COLOR = (0.827, 0.827, 0.827)
STIRRUP_COLOR = (0.412, 0.412, 0.412)
REBAR_COLOR = (0.717, 0.255, 0.055)


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
        self.fig = None
        self.axes = []

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
    ) -> None:
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
            Style of the center lines. Check matplotlib documentation for more information (Annotation-arrowprops).
        show: bool
            Show the plot.
        axes_i: int
            Index of the axes to plot on. Default is 0.
        """
        sns.set_theme(style="whitegrid")
        sns.set_context("notebook", font_scale=1.5)
        self._start_plot(figsize=figsize)
        self._add_rectangle(axes_i=axes_i)
        self._add_center_lines(axes_i=axes_i, style=center_line_style)
        self._add_dimension_lines(
            axes_i=axes_i,
            font_size_dimension=font_size_dimension,
            custom_text_height=custom_text_height,
            custom_text_width=custom_text_width,
            offset_line_width=offset_line_width,
            offset_line_height=offset_line_height,
        )
        self._add_stirrups(axes_i=axes_i)
        self._add_longitudinal_rebars(axes_i=axes_i)

        # set limits and title
        self.axes[axes_i].axis("off")
        self.axes[axes_i].axis("equal")
        self.axes[axes_i].set_title(
            label=title or "",
            fontdict={"fontsize": font_size_title},
        )

        if include_legend:
            self._add_legend(
                axes_i=axes_i,
                font_size_legend=font_size_legend,
                custom_legend_text=custom_text_legend,
            )
        if show:
            sns.despine()  # Clean up the plot
        return self.fig

    def _start_plot(self, figsize: tuple[float, float] = (15.0, 8.0)) -> tuple[float, float]:
        """Starts the plot by initializing a seaborn plot window of the given size.

        Parameters
        ----------
        figsize: tuple[float, float]
            Size of the plot window.
        """
        sns.set_style("white")
        self.fig, self.axes = sns.subplots(figsize=figsize)
        return self.fig.get_figwidth(), self.fig.get_figheight()

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

    # Other methods remain unchanged, as they rely on matplotlib.patches for shapes.
