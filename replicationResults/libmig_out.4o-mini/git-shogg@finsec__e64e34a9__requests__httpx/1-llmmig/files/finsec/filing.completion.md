### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `httpx`.
2. **HTTP Requests**: Any method calls that were using `requests` (like `requests.get`, `requests.post`, etc.) would need to be updated to use `httpx` equivalents. However, since the provided code does not show any direct HTTP request calls, this change is not explicitly visible in the provided snippet.
3. **Asynchronous Support**: If the original code were to use asynchronous features, `httpx` supports both synchronous and asynchronous requests. However, since the provided code does not indicate the use of async, we will keep it synchronous.

Since the provided code does not include any direct HTTP request calls, the migration primarily involves changing the import statement.

### Modified Code
```python
import httpx
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

This code reflects the necessary changes to migrate from `requests` to `httpx`, focusing solely on the import statement as the rest of the code does not include direct HTTP calls.