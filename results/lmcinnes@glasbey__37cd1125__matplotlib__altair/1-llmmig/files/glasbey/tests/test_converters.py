import pytest
import numpy as np

from glasbey._converters import get_rgb_palette, palette_to_sRGB1
from colorspacious import cspace_convert
import altair as alt


# Define palettes using Altair's color schemes
TAB10 = np.array(alt.themes.get_scheme("category10")["range"])[:, :3]
SET1 = np.array(alt.themes.get_scheme("set1")["range"])[:, :3]
ACCENT = np.array(alt.themes.get_scheme("accent")["range"])[:, :3]


@pytest.mark.parametrize("palette", ["category10", "set1", "accent"])
def test_palette_conversion(palette):
    pal = np.array(alt.themes.get_scheme(palette)["range"])[:, :3]
    cam_pal = cspace_convert(pal, "sRGB1", "CAM02-UCS")

    hex_pal = get_rgb_palette(cam_pal, as_hex=True)
    converted_pal = np.asarray([color for color in hex_pal])  # No need for to_rgb
    assert np.allclose(pal, converted_pal)

@pytest.mark.parametrize(
    "palette",
    ["category10", "set1", "#836fa9", ["#836fa9", "#3264c8"], [(0.1, 0.75, 0.3)], [(128, 192, 255), (16, 32, 64)]]
)
def test_srgb1_conversion(palette):
    srgb1_pal = palette_to_sRGB1(palette)
    assert srgb1_pal.shape[1] == 3
    assert np.max(srgb1_pal) <= 1.0 and np.min(srgb1_pal) >= 0.0

    if type(palette) is str:
        if palette.startswith("#"):
            assert srgb1_pal.shape[0] == 1
        else:
            pal = np.array(alt.themes.get_scheme(palette)["range"])[:, :3]
            assert len(pal) == len(srgb1_pal)
            assert np.allclose(pal, srgb1_pal)
    else:
        assert len(palette) == len(srgb1_pal)
