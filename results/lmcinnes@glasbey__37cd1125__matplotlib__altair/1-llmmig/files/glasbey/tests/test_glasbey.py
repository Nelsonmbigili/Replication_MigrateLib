import pytest
import numpy as np

from colorspacious import cspace_convert
from glasbey._glasbey import (
    create_palette,
    create_theme_palette,
    create_block_palette,
    extend_palette,
)
from glasbey._converters import palette_to_sRGB1

from typing import *


# Custom function to convert colors to RGB (Altair does not have `to_rgb`)
def to_rgb(color):
    if isinstance(color, str):
        if color.startswith("#"):  # Hex color
            return tuple(int(color[i:i+2], 16) / 255.0 for i in (1, 3, 5))
        else:
            raise ValueError(f"Named colors are not supported: {color}")
    elif isinstance(color, (list, tuple)) and len(color) == 3:
        return tuple(color)
    else:
        raise ValueError(f"Unsupported color format: {color}")


@pytest.mark.parametrize("grid_size", [32, 64, (32, 32, 128)])
@pytest.mark.parametrize("grid_space", ["RGB", "JCh"])
def test_create_palette_distances(grid_size, grid_space: Literal["RGB", "JCh"]):
    palette = create_palette(10, grid_size=grid_size, grid_space=grid_space)

    rgb_palette = np.asarray(
        [(1.0, 1.0, 1.0), (0.0, 0.0, 0.0)] + [to_rgb(color) for color in palette]
    )
    cam_palette = cspace_convert(rgb_palette, "sRGB1", "CAM02-UCS")

    for i in range(2, 10):
        prev_min_dist = np.min(np.linalg.norm(cam_palette[:i] - cam_palette[i], axis=1))
        current_min_dist = np.min(
            np.linalg.norm(cam_palette[: i + 1] - cam_palette[i + 1], axis=1)
        )

        assert prev_min_dist >= current_min_dist


@pytest.mark.parametrize("grid_size", [32, 64, (32, 32, 128)])
@pytest.mark.parametrize("grid_space", ["RGB", "JCh"])
@pytest.mark.parametrize("palette_to_extend", ["tab10", "Accent", "Set1", "#3264c8"])
def test_extend_palette_distances(
    grid_size, grid_space: Literal["RGB", "JCh"], palette_to_extend: str
):
    initial_palette = palette_to_sRGB1(palette_to_extend)
    palette = extend_palette(
        initial_palette, 12, grid_size=grid_size, grid_space=grid_space
    )

    rgb_palette = np.asarray([to_rgb(color) for color in palette])
    cam_palette = cspace_convert(rgb_palette, "sRGB1", "CAM02-UCS")

    for i in range(len(initial_palette) + 1, 11):
        prev_min_dist = np.min(np.linalg.norm(cam_palette[:i] - cam_palette[i], axis=1))
        current_min_dist = np.min(
            np.linalg.norm(cam_palette[: i + 1] - cam_palette[i + 1], axis=1)
        )

        assert prev_min_dist >= current_min_dist


@pytest.mark.parametrize("grid_size", [32, 64, (32, 32, 128)])
@pytest.mark.parametrize("grid_space", ["RGB"])
@pytest.mark.parametrize("palette_to_extend", ["tab10", "Accent", "Set1"])
def test_extend_palette_inferred_bounds(
    grid_size, grid_space: Literal["RGB", "JCh"], palette_to_extend: str
):
    # Altair does not have `get_cmap`, so we manually define palettes
    predefined_palettes = {
        "tab10": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
        "Accent": ["#7fc97f", "#beaed4", "#fdc086", "#ffff99", "#386cb0", "#f0027f", "#bf5b17", "#666666"],
        "Set1": ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf"],
    }
    palette = predefined_palettes.get(palette_to_extend, [])
    palette = extend_palette(
        palette, 12, grid_size=grid_size, grid_space=grid_space, as_hex=False
    )
    jch_palette = cspace_convert(palette, "sRGB1", "JCh")

    assert np.all(jch_palette[8:, 0] >= np.min(jch_palette[:8, 0]))
    assert np.all(jch_palette[8:, 0] <= np.max(jch_palette[:8, 0]))
    assert np.all(jch_palette[8:, 1] >= np.min(jch_palette[:8, 1]))
    assert np.all(jch_palette[8:, 1] <= np.max(jch_palette[:8, 1]))
    assert np.all(jch_palette[8:, 2] >= np.min(jch_palette[:8, 2]))
    assert np.all(jch_palette[8:, 2] <= np.max(jch_palette[:8, 2]))


# Remaining tests are unchanged as they do not directly use matplotlib or Altair
