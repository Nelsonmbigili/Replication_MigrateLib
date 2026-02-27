### Explanation of Changes:
To migrate the code from using `beautifulsoup4` to `pyquery`, the following changes were made:
1. **Import Change**: Replaced the `BeautifulSoup` import with `PyQuery` from the `pyquery` library.
2. **HTML Parsing**: Replaced the `BeautifulSoup` object creation (`BeautifulSoup(page.text, "html.parser")`) with `PyQuery` object creation (`PyQuery(page.text)`).
3. **Element Selection**: Replaced the `find_all` method of `BeautifulSoup` with the `items` method of `PyQuery` to select elements with the class `barChart`.
4. **Text Extraction**: Replaced the `get_text` method of `BeautifulSoup` with the `text()` method of `PyQuery` for extracting text from elements.

The rest of the code remains unchanged, as the migration only affects the HTML parsing and element selection parts.

---

### Modified Code:
```python
"""
The Pitt API, to access workable data of the University of Pittsburgh
Copyright (C) 2015 Ritwik Gupta

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from __future__ import annotations

from pyquery import PyQuery as pq
import requests
from typing import NamedTuple

GYM_URL = "https://connect2concepts.com/connect2/?type=bar&key=17c2cbcb-ec92-4178-a5f5-c4860330aea0"

GYM_NAMES = [
    "Baierl Rec Center",
    "Bellefield Hall: Fitness Center & Weight Room",
    "Bellefield Hall: Court & Dance Studio",
    "Trees Hall: Fitness Center",
    "Trees Hall: Courts",
    "Trees Hall: Racquetball Courts & Multipurpose Room",
    "William Pitt Union",
    "Pitt Sports Dome",
]


class Gym(NamedTuple):
    name: str
    date: str
    count: int
    percentage: int

    @classmethod
    def from_text(cls, text: str) -> Gym:
        info = text.split("|")
        name = info[0]
        if len(info) < 4:
            return cls(name=name, date=None, count=None, percentage=None)
        count = int(info[2][12:])
        date = info[3][9:]
        try:
            percentage = int(info[4].rstrip("%"))
        except ValueError:
            percentage = 0

        return cls(name=name, date=date, count=count, percentage=percentage)


def get_all_gyms_info() -> list[Gym]:
    """Fetches list of Gym named tuples with all gym information"""
    # Was getting a Mod Security Error
    # Fix: https://stackoverflow.com/questions/61968521/python-web-scraping-request-errormod-security
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
    }

    page = requests.get(GYM_URL, headers=headers)
    doc = pq(page.text)  # Parse the HTML using PyQuery
    gym_info_list = doc("div.barChart").items()  # Select all div elements with class "barChart"

    # Iterate through list and add to dictionary
    gyms = [Gym.from_text(gym.text().replace("\n", "|")) for gym in gym_info_list]
    return gyms


def get_gym_info(gym_name: str) -> Gym | None:
    """Fetches the information of a singular gym as a tuple"""
    info = get_all_gyms_info()
    if gym_name in GYM_NAMES:
        for gym in info:
            if gym.name == gym_name and gym.date and gym.count and gym.percentage:
                return gym
    return None
```

---

### Key Changes in Detail:
1. **Import Statement**:
   ```python
   from bs4 import BeautifulSoup
   ```
   was replaced with:
   ```python
   from pyquery import PyQuery as pq
   ```

2. **HTML Parsing**:
   ```python
   soup = BeautifulSoup(page.text, "html.parser")
   ```
   was replaced with:
   ```python
   doc = pq(page.text)
   ```

3. **Element Selection**:
   ```python
   gym_info_list = soup.find_all("div", class_="barChart")
   ```
   was replaced with:
   ```python
   gym_info_list = doc("div.barChart").items()
   ```

4. **Text Extraction**:
   The `get_text("|", strip=True)` method of `BeautifulSoup` was replaced with:
   ```python
   gym.text().replace("\n", "|")
   ```
   This ensures the text is extracted and formatted similarly to the original code.

These changes ensure the code now uses `pyquery` for HTML parsing and element selection while maintaining the original functionality.