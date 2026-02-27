"""Rectangular reinforced cross-section."""

# ruff: noqa: PLR0913
from typing import Literal

import plotly.graph_objects as go  # Added for plotly support
from shapely import LineString, Point, Polygon

from blueprints.materials.concrete import ConcreteMaterial
from blueprints.materials.reinforcement_steel import ReinforcementSteelMaterial
from blueprints.structural_sections.concrete.covers import CoversRectangular
from blueprints.structural_sections.concrete.reinforced_concrete_sections.base import ReinforcedCrossSection
from blueprints.structural_sections.concrete.reinforced_concrete_sections.plotters.rectangular import RectangularCrossSectionPlotter
from blueprints.structural_sections.concrete.reinforced_concrete_sections.reinforcement_configurations import ReinforcementByQuantity
from blueprints.structural_sections.concrete.stirrups import StirrupConfiguration
from blueprints.structural_sections.cross_section_shapes import RectangularCrossSection
from blueprints.type_alias import DIMENSIONLESS, MM, RATIO


class RectangularReinforcedCrossSection(ReinforcedCrossSection):
    """Representation of a reinforced rectangular concrete cross-section like a beam.

    Parameters
    ----------
    width : MM
        The width of the rectangular cross-section [mm].
    height : MM
        The height of the rectangular cross-section [mm].
    concrete_material : ConcreteMaterial
        Material properties of the concrete.
    covers : CoversRectangular, optional
        The reinforcement covers for the cross-section [mm]. The default on all sides is 50 mm.
    """

    def __init__(
        self,
        width: MM,
        height: MM,
        concrete_material: ConcreteMaterial,
        covers: CoversRectangular = CoversRectangular(),
    ) -> None:
        """Initialize the rectangular reinforced concrete section."""
        super().__init__(
            cross_section=RectangularCrossSection(
                width=width,
                height=height,
            ),
            concrete_material=concrete_material,
        )
        self.width = width
        self.height = height
        self.covers = covers
        self.plotter = RectangularCrossSectionPlotter(cross_section=self)

    def add_stirrup_along_edges(
        self,
        diameter: MM,
        distance: MM,
        material: ReinforcementSteelMaterial,
        shear_check: bool = True,
        torsion_check: bool = True,
        mandrel_diameter_factor: DIMENSIONLESS | None = None,
        anchorage_length: MM = 0.0,
        relative_start_position: RATIO = 0.0,
        relative_end_position: RATIO = 1.0,
    ) -> StirrupConfiguration:
        """Adds a stirrup configuration along the edges of the cross-section taking the covers into account. The created configuration goes around
        the longitudinal rebars (if any).

        Use .add_stirrup_configuration() to add a stirrup configuration of any shape, size, and position (as long as it is inside the cross-section).


        Parameters
        ----------
        diameter: MM
            Diameter of the stirrups [mm].
        distance: MM
            Longitudinal distance between stirrups [mm].
        material : ReinforcementSteelMaterial
            Representation of the properties of reinforcement steel suitable for use with NEN-EN 1992-1-1
        shear_check: bool
            Take stirrup into account in shear check
        torsion_check: bool
            Take stirrup into account in torsion check
        mandrel_diameter_factor: DIMENSIONLESS
            Inner diameter of mandrel as multiple of stirrup diameter [-]
            (default: 4⌀ for ⌀<=16mm and 5⌀ for ⌀>16mm) Tabel 8.1Na NEN-EN 1992-1-1 Dutch National Annex.
        anchorage_length: MM
            Anchorage length [mm]
        relative_start_position: RATIO
            Relative position of the start of the stirrup configuration inside the cross-section (longitudinal direction). Value between 0 and 1.
            Default is 0 (start).
        relative_end_position: RATIO
            Relative position of the end of the stirrup configuration inside the cross-section (longitudinal direction). Value between 0 and 1.
            Default is 1 (end).


        Returns
        -------
        StirrupConfiguration
            Newly created stirrup configuration inside the cross-section.
        """
        # get the corners of the cross-section
        min_x, min_y, max_x, max_y = self.cross_section.geometry.bounds

        # create the corners of the stirrup configuration based on the covers present
        left_bottom_corner = Point(min_x + self.covers.left + (diameter / 2), min_y + self.covers.lower + (diameter / 2))
        left_top_corner = Point(min_x + self.covers.left + (diameter / 2), max_y - self.covers.upper - (diameter / 2))
        right_top_corner = Point(max_x - self.covers.right - (diameter / 2), max_y - self.covers.upper - (diameter / 2))
        right_bottom_corner = Point(max_x - self.covers.right - (diameter / 2), min_y + self.covers.lower + (diameter / 2))

        return self.add_stirrup_configuration(
            StirrupConfiguration(
                geometry=Polygon([left_bottom_corner, left_top_corner, right_top_corner, right_bottom_corner]),
                diameter=diameter,
                distance=distance,
                material=material,
                shear_check=shear_check,
                torsion_check=torsion_check,
                mandrel_diameter_factor=mandrel_diameter_factor,
                anchorage_length=anchorage_length,
                based_on_cover=True,
                relative_start_position=relative_start_position,
                relative_end_position=relative_end_position,
            )
        )

    def plot(self, *args, **kwargs) -> go.Figure:
        """Plot the cross-section. Making use of the standard plotter.

        If you want to use a custom plotter, use the .plotter attribute to plot the cross-section.

        Parameters
        ----------
        *args
            Additional arguments passed to the plotter.
        **kwargs
            Additional keyword arguments passed to the plotter.
        """
        return self.plotter.plot(*args, **kwargs)
