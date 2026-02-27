### Explanation of Changes:
The original code does not directly use the `requests` library in any of its methods, but it imports it. Since the task is to migrate from `requests` to `urllib3`, the only change required is to replace the `requests` import with the `urllib3` import. No other changes are necessary because the code does not actually utilize `requests` functionality.

### Modified Code:
```python
import urllib3
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

### Summary:
- Replaced `import requests` with `import urllib3`.
- No other changes were made since the code does not use any functionality from the `requests` library.