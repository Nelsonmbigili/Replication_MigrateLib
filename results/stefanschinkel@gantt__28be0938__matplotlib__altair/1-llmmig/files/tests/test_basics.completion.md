### Explanation of Changes:
The original code uses `matplotlib` for rendering Gantt charts, specifically in the `Gantt` class's `render` method. To migrate to `altair`, the following changes were made:
1. Removed the `matplotlib` import and its usage (`matplotlib.use("agg")` and `g.ax.get_title()`).
2. Updated the `Gantt` class's `render` method to use `altair` for plotting. `altair` is a declarative visualization library, so the chart creation process is different. Instead of directly manipulating axes, we define a chart using `altair.Chart` and its methods.
3. Adjusted the `testPlotTitle` test to verify the title in the `altair` chart object instead of a `matplotlib` axis.

Below is the modified code:

---

### Modified Code:
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
        chart = g.render()
        self.assertEqual(chart.title, "Basic Title")


if __name__ == "__main__":
    unittest.main()
```

---

### Notes:
1. The `Gantt` class's `render` method must now use `altair` to create the Gantt chart. This involves defining an `altair.Chart` object with the appropriate data and encodings. Since the `Gantt` class implementation is not provided, you will need to update it separately to use `altair` instead of `matplotlib`.
2. The `testPlotTitle` test now checks the `title` attribute of the `altair.Chart` object returned by `g.render()`.

Let me know if you need help updating the `Gantt` class itself!