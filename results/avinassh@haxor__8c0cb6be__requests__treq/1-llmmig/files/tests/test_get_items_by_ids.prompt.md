The following Python code currently uses the library "requests" version 2.32.3.
Migrate this code to use the library "treq" version 24.9.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "requests" to "treq".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "requests" and "treq".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest

from hackernews import HackerNews
from hackernews import Item


class TestGetItemsByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_items_by_ids(self):
        items = self.hn.get_items_by_ids([1, 2, 3])
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 3)
        self.assertIsInstance(items[0], Item)

    def test_get_items_by_ids_filtered(self):
        items = self.hn.get_items_by_ids(
            [i for i in range(1, 50)],
            item_type='story'
        )
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 37)
        self.assertIsInstance(items[0], Item)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()

```