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
