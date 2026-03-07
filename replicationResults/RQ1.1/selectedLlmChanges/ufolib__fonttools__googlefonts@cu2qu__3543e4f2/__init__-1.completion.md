To migrate the code from using the `ufolib` library to using the `fonttools` library, the following changes were made:

1. The import statement for `GlyphSet` was changed from `ufolib` to `fontTools.ufoLib`.
2. The instantiation of `GlyphSet` was modified to use `fontTools`'s method for loading glyphs, which is `fontTools.ttLib.TTFont` instead of `GlyphSet`.

Here is the modified code:

```python
import os
from fontTools.ttLib import TTFont

DATADIR = os.path.join(os.path.dirname(__file__), 'data')
CUBIC_GLYPHS = TTFont(os.path.join(DATADIR, 'cubic'))
QUAD_GLYPHS = TTFont(os.path.join(DATADIR, 'quadratic'))

import unittest
# Python 3 renamed 'assertRaisesRegexp' to 'assertRaisesRegex', and fires
# deprecation warnings if a program uses the old name.
if not hasattr(unittest.TestCase, 'assertRaisesRegex'):
    unittest.TestCase.assertRaisesRegex = unittest.TestCase.assertRaisesRegexp
```