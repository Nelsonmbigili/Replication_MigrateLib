### Explanation of Changes:
The `requests` library is synchronous and blocking, while `treq` is an asynchronous HTTP client built on `Twisted`. To migrate from `requests` to `treq`, the following changes were made:
1. Removed the `requests` import and replaced it with `treq`.
2. Since `treq` is asynchronous, any HTTP request-related methods would need to be converted to asynchronous methods using `async def`.
3. Any calls to `requests` methods (e.g., `requests.get`, `requests.post`) would be replaced with their `treq` equivalents (e.g., `treq.get`, `treq.post`).
4. The code provided does not explicitly show any HTTP requests, so no direct changes to HTTP calls were necessary. However, if the methods in the `Filing` class or its parent class (`FilingBase`) internally use `requests`, those would need to be updated to use `treq`.

Since the provided code does not include any explicit HTTP requests, no changes to the method implementations were required. The only change was removing the `requests` import.

### Modified Code:
```python
import treq
from bs4 import BeautifulSoup as bs

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

### Notes:
- The provided code does not include any explicit HTTP requests, so no further changes were necessary.
- If the parent class (`FilingBase`) or other parts of the application use `requests`, those would need to be updated to use `treq` as well.
- Ensure that the application is set up to handle asynchronous methods if `treq` is used in other parts of the code.