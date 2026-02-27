The following Python code currently uses the library "requests" version 2.32.3.
Migrate this code to use the library "requests_futures" version 1.0.2 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "requests" to "requests_futures".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "requests" and "requests_futures".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest

from hackernews import HackerNews


class TestGetAsync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_async(self):
        response = self.hn._run_async([self.url])
        self.assertEqual(response[0]['id'], 8863)
        self.assertEqual(response[0]['by'], 'dhouston')

    def test_get_async_error(self):
        response = self.hn._run_async([self.err_url])
        self.assertEqual(response, [None])

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()

```