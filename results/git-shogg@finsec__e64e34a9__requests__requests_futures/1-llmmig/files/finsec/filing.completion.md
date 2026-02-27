### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the primary difference is that `requests_futures` provides asynchronous capabilities by using `FuturesSession` instead of the synchronous `requests` methods. However, the provided code does not directly use any `requests` methods (e.g., `requests.get`, `requests.post`), so there are no explicit calls to replace. 

Since the migration involves replacing `requests` with `requests_futures`, the only change required is to import `FuturesSession` from `requests_futures` instead of importing `requests`. This ensures that any future usage of HTTP requests in this code or its dependencies can leverage the asynchronous capabilities of `requests_futures`.

### Modified Code:
```python
from requests_futures.sessions import FuturesSession
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

### Summary of Changes:
1. Replaced the import of `requests` with the import of `FuturesSession` from `requests_futures`.
2. No other changes were made, as the provided code does not directly use any `requests` methods.