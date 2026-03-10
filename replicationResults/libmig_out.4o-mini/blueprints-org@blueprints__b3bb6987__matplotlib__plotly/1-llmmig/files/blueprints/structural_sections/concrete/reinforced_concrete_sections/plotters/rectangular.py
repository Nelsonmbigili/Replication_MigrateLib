"""Plotter for Reinforced Rectangular Cross-Sections."""

# ruff: noqa: PLR0913, F821
from typing import TypeVar
import plotly.graph_objects as go
from shapely import Point

from blueprints.structural_sections.concrete.rebar import Rebar

T = TypeVar("T", bound="RectangularReinforcedCrossSection")  # type: ignore[name-defined]

RCS_CROSS_SECTION_COLOR = "rgba(210, 210, 210, 1)"
STIRRUP_COLOR = "rgba(105, 105, 105, 1)"
REBAR_COLOR = "rgba(183, 65, 14, 1)"


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
        title: str | None = None,
        include_legend: bool = True,
        show: bool = False,
    ) -> go.Figure:
        """Plots the cross-section.

        Parameters
        ----------
        title: str
            Title of the plot.
        include_legend: bool
            Include legend in the plot.
        show: bool
            Show the plot.

        Returns
        -------
        go.Figure
            Plotly figure.
        """
        self._start_plot()
        self._add_rectangle()
        self._add_center_lines()
        self._add_dimension_lines()
        self._add_stirrups()
        self._add_longitudinal_rebars()

        # set title
        self.fig.update_layout(
            title=title or "",
            showlegend=include_legend,
            xaxis=dict(showgrid=False, zeroline=False, showline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, showline=False, visible=False),
        )

        if show:
            self.fig.show()  # pragma: no cover
        assert self.fig is not None
        return self.fig

    def _start_plot(self) -> None:
        """Starts the plot by initializing a plotly figure."""
        self.fig = go.Figure()

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

    def _add_center_lines(self) -> None:
        """Adds center lines to the plot."""
        offset_center_line = 1.05
        self.fig.add_annotation(
            text="z",
            x=0,
            y=(-self.cross_section.height / 2) * offset_center_line,
            ax=0,
            ay=(self.cross_section.height / 2) * offset_center_line,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowcolor="gray",
            axref="x",
            ayref="y",
        )
        self.fig.add_annotation(
            text="y",
            x=((self.cross_section.width / 2) * offset_center_line),
            y=0,
            ax=-(self.cross_section.width / 2) * offset_center_line,
            ay=0,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowcolor="gray",
            axref="x",
            ayref="y",
        )

    def _add_dimension_lines(self) -> None:
        """Adds dimension lines to the plot."""
        offset_width = (-self.cross_section.height / 2) * 1.25
        self.fig.add_annotation(
            text="",
            x=-self.cross_section.width / 2,
            y=offset_width,
            ax=self.cross_section.width / 2,
            ay=offset_width,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            axref="x",
            ayref="y",
        )
        self.fig.add_annotation(
            text=f"{self.cross_section.width:.0f} mm",
            x=0,
            y=offset_width,
            showarrow=False,
        )

        offset_height = (-self.cross_section.width / 2) * 1.2
        self.fig.add_annotation(
            text="",
            x=offset_height,
            y=self.cross_section.height / 2,
            ax=offset_height,
            ay=-self.cross_section.height / 2,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            axref="x",
            ayref="y",
            textangle=90,
        )
        self.fig.add_annotation(
            text=f"{self.cross_section.height:.0f} mm",
            x=offset_height,
            y=0,
            showarrow=False,
            textangle=90,
        )

    def _add_stirrups(self) -> None:
        """Adds stirrups to the plot."""
        for stirrup in self.cross_section.stirrups:
            left_bottom = Point(stirrup.geometry.exterior.coords[0])  # left bottom point of the stirrup (center line)
            self.fig.add_shape(
                type="rect",
                x0=left_bottom.x - stirrup.diameter / 2,
                y0=left_bottom.y - stirrup.diameter / 2,
                x1=left_bottom.x + stirrup.ctc_distance_legs + stirrup.diameter / 2,
                y1=self.cross_section.height - self.cross_section.covers.upper - self.cross_section.covers.lower,
                fillcolor=STIRRUP_COLOR,
                line=dict(color=STIRRUP_COLOR),
            )
            self.fig.add_shape(
                type="rect",
                x0=left_bottom.x + stirrup.diameter / 2,
                y0=left_bottom.y + stirrup.diameter / 2,
                x1=left_bottom.x + stirrup.ctc_distance_legs - stirrup.diameter / 2,
                y1=self.cross_section.height - self.cross_section.covers.upper - self.cross_section.covers.lower - 2 * stirrup.diameter,
                fillcolor=RCS_CROSS_SECTION_COLOR,
                line=dict(color=RCS_CROSS_SECTION_COLOR),
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
                line=dict(color=REBAR_COLOR),
            )

    def legend_text(self) -> str:
        """Creates the legend text.

        Returns
        -------
        str
            Legend text.
        """
        # start building legend
        main_steel_material_used = self.cross_section.get_present_steel_materials()[0].name
        legend_text = f"{self.cross_section.concrete_material.concrete_class.value} - {main_steel_material_used}"

        legend_text += self._add_stirrups_to_legend()
        legend_text += self._add_longitudinal_rebars_to_legend()
        legend_text += self._add_rebar_configurations_to_legend()
        legend_text += self._add_single_longitudinal_rebars_to_legend()
        legend_text += self._add_covers_info_to_legend()

        return legend_text

    def _add_stirrups_to_legend(self) -> str:
        """Adds stirrups to the legend text."""
        stirrups_text = ""
        if self.cross_section.stirrups:
            stirrups_text += f"\nStirrups ({sum(stirrup.as_w for stirrup in self.cross_section.stirrups):.0f} mm²/m):"
            for stirrup in self.cross_section.stirrups:
                stirrups_text += (
                    f"\n  ⌀{stirrup.diameter}-{stirrup.distance} mm (b:{stirrup.ctc_distance_legs:.0f} mm) ({stirrup.as_w:.0f} " f"mm²/m)"
                )
        return stirrups_text

    def _add_longitudinal_rebars_to_legend(self) -> str:
        """Add longitudinal rebars to the legend text."""
        longitudinal_rebars = ""
        if self.cross_section.longitudinal_rebars:
            longitudinal_rebars += f"\nReinforcement ({sum(rebar.area for rebar in self.cross_section.longitudinal_rebars):.0f} mm²/m): "
        return longitudinal_rebars

    def _add_single_longitudinal_rebars_to_legend(self) -> str:
        """Add single longitudinal rebars to legend text."""
        single_longitudinal_text = ""
        if self.cross_section._single_longitudinal_rebars:  # noqa: SLF001
            rebar_diameters: dict[float, list[Rebar]] = {}
            for rebar in self.cross_section._single_longitudinal_rebars:  # noqa: SLF001
                rebar_diameters.setdefault(rebar.diameter, []).append(rebar)
            for diameter, rebars in rebar_diameters.items():
                single_longitudinal_text += f"\n  {len(rebars)}⌀{round(diameter, 2)} ({int(sum(rebar.area for rebar in rebars))} mm²/m)"
        return single_longitudinal_text

    def _add_rebar_configurations_to_legend(self) -> str:
        """Add rebar configurations to legend text (quantity in line)."""
        rebar_configurations_text = ""
        if self.cross_section._reinforcement_configurations:  # noqa: SLF001
            for _, configuration in self.cross_section._reinforcement_configurations:  # noqa: SLF001
                rebar_configurations_text += f"\n  {configuration!s} ({int(configuration.area)} mm²/m)"
        return rebar_configurations_text

    def _add_covers_info_to_legend(self) -> str:
        """Add covers info to legend text."""
        covers_text = ""
        if self.cross_section.stirrups or self.cross_section.longitudinal_rebars:
            covers_text += "\n" + self.cross_section.covers.get_covers_info()
        return covers_text

    def _add_legend(
        self,
        custom_legend_text: str | None = None,
    ) -> None:
        """Adds the legend to the plot.

        Parameters
        ----------
        custom_legend_text: str
            Custom legend text.
        """
        legend_text = custom_legend_text or self.legend_text()
        self.fig.add_annotation(
            text=legend_text,
            x=0,
            y=-self.cross_section.height / 2,
            showarrow=False,
            font=dict(size=10),
        )
