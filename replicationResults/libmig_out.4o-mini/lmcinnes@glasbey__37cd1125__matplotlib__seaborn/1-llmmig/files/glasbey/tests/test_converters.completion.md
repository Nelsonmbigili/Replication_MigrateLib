### Explanation of Changes
To migrate the code from using `matplotlib` to `seaborn`, I replaced the `get_cmap` function from `matplotlib` with the equivalent functionality in `seaborn`. The `seaborn` library provides a more straightforward way to access color palettes. Specifically, I used `seaborn.color_palette()` to retrieve the color palettes instead of using `get_cmap`. The rest of the code remains unchanged to maintain the original functionality and structure.

### Modified Code
```python
import pytest
import numpy as np
import seaborn as sns

from glasbey._converters import get_rgb_palette, palette_to_sRGB1
try:
    from matplotlib.cm import get_cmap
except ImportError:
    from matplotlib.pyplot import get_cmap
from matplotlib.colors import to_rgb
from colorspacious import cspace_convert


TAB10 = sns.color_palette("tab10", 10)
SET1 = sns.color_palette("Set1", 6)
ACCENT = sns.color_palette("Accent", 6)


@pytest.mark.parametrize("palette", ["tab10", "Set1", "Accent"])
def test_palette_conversion(palette):
    pal = sns.color_palette(palette, 6)
    cam_pal = cspace_convert(pal, "sRGB1", "CAM02-UCS")

    hex_pal = get_rgb_palette(cam_pal, as_hex=True)
    converted_pal = np.asarray([to_rgb(color) for color in hex_pal])
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
            pal = np.asarray(sns.color_palette(palette))[:, :3]
            assert len(pal) == len(srgb1_pal)
            assert np.allclose(pal, srgb1_pal)
    else:
        assert len(palette) == len(srgb1_pal)
```