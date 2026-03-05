### Explanation of Changes
To migrate the code from using the `beautifulsoup4` library to the `pyquery` library, the following changes were made:

1. **Import Statement**: The import statement for `BeautifulSoup` was replaced with the import statement for `pyquery`. Specifically, `from bs4 import BeautifulSoup as bs` was changed to `from pyquery import PyQuery as pq`.
  
2. **Parsing HTML**: The way HTML is parsed and manipulated changes between the two libraries. In `BeautifulSoup`, you typically create a `BeautifulSoup` object with the HTML content, while in `pyquery`, you create a `PyQuery` object. The syntax for selecting elements also differs slightly, as `pyquery` uses jQuery-like selectors.

3. **Element Selection**: Any method calls that were specific to `BeautifulSoup` (like `.find()`, `.find_all()`, etc.) would need to be replaced with their `pyquery` equivalents (like `pq('selector')`).

However, since the provided code does not include any HTML parsing or manipulation, the migration primarily involves changing the import statement. The rest of the code remains unchanged as it does not interact with HTML content directly.

### Modified Code
```python
import requests
from pyquery import PyQuery as pq

from .base import FilingBase

class Filing(FilingBase):

    def get_a_13f_filing(self, qtr_year:str, amend_filing:bool = True):
        return self.get_13f_filing(qtr_year, amend_filing)

    def filings_to_excel(self, simplified:bool = True, inc_cover_page_tabs:bool = False):
        return self.convert_filings_to_excel(simplified, inc_cover_page_tabs)

    def latest_13f_filing(self, simplified:bool = True, amend_filing:bool = True):
        return self.get_latest_13f_filing(simplified, amend_filing)

    @property
    def latest_13f_portfolio_value(self):
        return self.get_latest_13f_value()

    @property
    def latest_13f_count_holdings(self):
        return self.get_latest_13f_num_holdings()

    def latest_13f_filing_detailed(self):
        return self.get_latest_13f_filing(simplified=False, amend_filing=True)

    @property
    def latest_13f_filing_cover_page(self):
        return self.get_latest_13f_filing_cover_page()
```