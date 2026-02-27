import pytest
import numpy as np

from glasbey._converters import get_rgb_palette, palette_to_sRGB1
from seaborn import color_palette
from colorspacious import cspace_convert


TAB10 = np.array(color_palette("tab10", 10))
SET1 = np.array(color_palette("Set1", 6))
ACCENT = np.array(color_palette("Accent", 6))


@pytest.mark.parametrize("palette", ["tab10", "Set1", "Accent"])
def test_palette_conversion(palette):
    pal = np.array(color_palette(palette, 6))
    cam_pal = cspace_convert(pal, "sRGB1", "CAM02-UCS")

    hex_pal = get_rgb_palette(cam_pal, as_hex=True)
    converted_pal = np.asarray([tuple(color) for color in hex_pal])
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
            pal = np.array(color_palette(palette))
            assert len(pal) == len(srgb1_pal)
            assert np.allclose(pal, srgb1_pal)
    else:
        assert len(palette) == len(srgb1_pal)
