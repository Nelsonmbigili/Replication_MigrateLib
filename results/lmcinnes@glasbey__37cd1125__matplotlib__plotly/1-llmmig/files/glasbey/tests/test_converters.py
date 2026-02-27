import pytest
import numpy as np

from glasbey._converters import get_rgb_palette, palette_to_sRGB1
from colorspacious import cspace_convert
from plotly.colors import qualitative

# Helper function to convert hex to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

# Mapping plotly palettes to variables
TAB10 = np.array([hex_to_rgb(color) for color in qualitative.T10])
SET1 = np.array([hex_to_rgb(color) for color in qualitative.Set1])
ACCENT = np.array([hex_to_rgb(color) for color in qualitative.Accent])

@pytest.mark.parametrize("palette", ["tab10", "Set1", "Accent"])
def test_palette_conversion(palette):
    # Access the appropriate plotly palette
    if palette == "tab10":
        pal = TAB10
    elif palette == "Set1":
        pal = SET1
    elif palette == "Accent":
        pal = ACCENT
    else:
        raise ValueError(f"Unknown palette: {palette}")

    cam_pal = cspace_convert(pal, "sRGB1", "CAM02-UCS")

    hex_pal = get_rgb_palette(cam_pal, as_hex=True)
    converted_pal = np.asarray([hex_to_rgb(color) for color in hex_pal])
    assert np.allclose(pal, converted_pal)

@pytest.mark.parametrize(
    "palette",
    ["tab10", "Set1", "#836fa9", ["#836fa9", "#3264c8"], [(0.1, 0.75, 0.3)], [(128, 192, 255), (16, 32, 64)]]
)
def test_srgb1_conversion(palette):
    srgb1_pal = palette_to_sRGB1(palette)
    assert srgb1_pal.shape[1] == 3
    assert np.max(srgb1_pal) <= 1.0 and np.min(srgb1_pal) >= 0.0

    if type(palette) is str:
        if palette.startswith("#"):
            assert srgb1_pal.shape[0] == 1
        else:
            # Access the appropriate plotly palette
            if palette == "tab10":
                pal = TAB10
            elif palette == "Set1":
                pal = SET1
            elif palette == "Accent":
                pal = ACCENT
            else:
                raise ValueError(f"Unknown palette: {palette}")

            assert len(pal) == len(srgb1_pal)
            assert np.allclose(pal, srgb1_pal)
    else:
        assert len(palette) == len(srgb1_pal)
