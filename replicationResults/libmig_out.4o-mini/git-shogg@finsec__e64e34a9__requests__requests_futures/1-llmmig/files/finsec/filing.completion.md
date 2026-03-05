### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `requests_futures.sessions`. This allows us to use the `FuturesSession` class, which is designed to handle asynchronous requests.
2. **Session Creation**: Instead of using the standard `requests.Session()`, we now create an instance of `FuturesSession()`. This enables the code to send requests asynchronously.
3. **Request Method**: The method calls for making requests (e.g., `get`, `post`) are now called on the `FuturesSession` instance, which returns a `Future` object. This allows the program to continue executing while waiting for the response.

The following code reflects these changes while maintaining the original structure and functionality.

### Modified Code
```python
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup as bs

from .base import FilingBase

class Filing(FilingBase):
    def __init__(self):
        self.session = FuturesSession()

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

In this modified code, the `FuturesSession` is instantiated in the `__init__` method of the `Filing` class, allowing for asynchronous requests to be made throughout the class methods.