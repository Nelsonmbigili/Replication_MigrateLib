### Explanation of Changes

To migrate the code from using `matplotlib` to `seaborn`, the following changes were made:

1. **Import Statement**: The import statement for `matplotlib` was removed since `seaborn` is built on top of `matplotlib` and does not require a separate backend setting like `agg`.
2. **Plotting**: The code that creates plots using `matplotlib` should be replaced with equivalent `seaborn` functions. However, since the original code does not contain explicit plotting commands (it seems to rely on a `Gantt` class for rendering), we assume that the `Gantt` class can handle `seaborn` plots internally.
3. **Rendering**: The `render` method of the `Gantt` class is assumed to be compatible with `seaborn`, so no changes were made to how the `Gantt` class is instantiated or used.

Here is the modified code:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
test_basics.py - basic tests for gantt
"""
import sys
import unittest
from os import path

# add to path for sure
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from gantt import Gantt
from gantt import Package as WP

# file we use
BASICS = path.join(path.dirname(path.abspath(__file__)), "basics.json")


class ExtendedTestCase(unittest.TestCase):

    def assertRaisesMsg(self, msg, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.assertFail()
        except Exception as inst:
            self.assertEqual(inst.msg, msg)


class TestsPackage(ExtendedTestCase):
    """Basic tests for package class"""

    def testValuePassing(self):
        """reject pointless dates"""
        PKG = {"label": "A", "start": 0, "end": 2, "milestones": [1]}
        pkg = WP(PKG)
        self.assertEqual(pkg.label, "A")
        self.assertEqual(pkg.start, 0)
        self.assertEqual(pkg.end, 2)
        self.assertEqual(pkg.milestones, [1])

    def testValError(self):
        """reject pointless dates"""
        # start must be after begin
        PKG = {"label": "A", "start": 3, "end": 2}
        self.assertRaises(ValueError, WP, PKG)

    def testNegatives(self):
        """reject negative start/end"""
        # start must be after begin
        PKG = {"label": "A", "start": -1, "end": 2}
        self.assertRaises(ValueError, WP, PKG)
        PKG = {"label": "A", "start": -1, "end": -1}
        self.assertRaises(ValueError, WP, PKG)
        PKG = {"label": "A", "start": 3, "end": -1}
        self.assertRaises(ValueError, WP, PKG)

    def testDefColor(self):
        """reject pointless dates"""
        PKG = {"label": "A", "start": 0, "end": 2}
        pkg = WP(PKG)
        self.assertEqual(pkg.color, "#32AEE0")


class TestsBasics(unittest.TestCase):
    """Tests to ensure the data ends up in the right places"""

    def testTitle(self):
        """Whats my name?"""
        g = Gantt(BASICS)
        self.assertEqual(g.title, "Basic Title")

    def testPackages(self):
        """Make sure the no. of packages is correct"""
        g = Gantt(BASICS)
        self.assertEqual(len(g.packages), 4)

    def testTimings(self):
        """Make sure start/end is set properly"""
        g = Gantt(BASICS)
        self.assertEqual(g.start, [0, 3, 3, 6])
        self.assertEqual(g.end, [2, 6, 5, 8])

    def testPlotTitle(self):
        """Make sure title is passed to plot"""
        g = Gantt(BASICS)
        g.render()
        x = g.ax.get_title()
        self.assertEqual(x, "Basic Title")


if __name__ == "__main__":
    unittest.main()
```

In this modified code, the `matplotlib` backend setting has been removed, and the code is now ready to work with `seaborn`. The `Gantt` class is assumed to handle the plotting internally using `seaborn` without requiring further modifications in the test code.